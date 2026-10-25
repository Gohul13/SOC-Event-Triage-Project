from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.config import settings
from app.database import get_db, init_db
from app.ml_classifier import get_classifier
from app.models import SecurityEvent
from app.schemas import (
    ErrorResponse,
    EventCreate,
    EventCreateBatch,
    EventCreateResponse,
    EventOut,
    EventStatus,
    EventStatusUpdate,
    RiskLevel,
    StatsOut,
)

BACKEND_ROOT = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Raksha SOC Event Triage API",
    version="1.0.0",
    description="Ingest security logs, classify risk, and support analyst triage workflows.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            detail="Validation failed",
            errors=exc.errors(),
        ).model_dump(),
    )


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    get_classifier(settings.resolved_model_path(BACKEND_ROOT))


def _parse_event_payload(data: Any) -> list[EventCreate]:
    if isinstance(data, list):
        return [EventCreate.model_validate(item) for item in data]
    if isinstance(data, dict) and "events" in data:
        return EventCreateBatch.model_validate(data).events
    if isinstance(data, dict):
        return [EventCreate.model_validate(data)]
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Body must be a single event, { events: [...] }, or a JSON array of events",
    )


def _classify_and_persist(db: Session, payload: EventCreate) -> SecurityEvent:
    clf = get_classifier(settings.resolved_model_path(BACKEND_ROOT))
    risk, confidence = clf.predict(payload.raw_log)
    event = SecurityEvent(
        raw_log=payload.raw_log,
        source=payload.source,
        risk_level=risk.value,
        confidence=confidence,
        status=EventStatus.PENDING.value,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/events",
    response_model=list[EventCreateResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
async def create_events(request: Request, db: Session = Depends(get_db)) -> list[SecurityEvent]:
    try:
        data = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body") from exc

    try:
        items = _parse_event_payload(data)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        ) from exc

    if not items:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No events provided")

    return [_classify_and_persist(db, item) for item in items]


@app.get("/events", response_model=list[EventOut])
def list_events(
    db: Session = Depends(get_db),
    risk_level: Annotated[RiskLevel | None, Query()] = None,
    source: Annotated[str | None, Query(max_length=128)] = None,
    status_filter: Annotated[EventStatus | None, Query(alias="status")] = None,
    from_date: Annotated[datetime | None, Query(alias="from")] = None,
    to_date: Annotated[datetime | None, Query(alias="to")] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[SecurityEvent]:
    stmt = select(SecurityEvent).order_by(SecurityEvent.created_at.desc())
    if risk_level:
        stmt = stmt.where(SecurityEvent.risk_level == risk_level.value)
    if source:
        stmt = stmt.where(SecurityEvent.source.ilike(f"%{source.strip()}%"))
    if status_filter:
        stmt = stmt.where(SecurityEvent.status == status_filter.value)
    if from_date:
        stmt = stmt.where(SecurityEvent.created_at >= from_date)
    if to_date:
        stmt = stmt.where(SecurityEvent.created_at <= to_date)
    stmt = stmt.offset(offset).limit(limit)
    return list(db.scalars(stmt).all())


@app.get("/events/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)) -> SecurityEvent:
    event = db.get(SecurityEvent, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@app.patch(
    "/events/{event_id}",
    response_model=EventOut,
    dependencies=[Depends(require_api_key)],
)
def update_event_status(
    event_id: int,
    body: EventStatusUpdate,
    db: Session = Depends(get_db),
) -> SecurityEvent:
    event = db.get(SecurityEvent, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    event.status = body.status.value
    db.commit()
    db.refresh(event)
    return event


@app.get("/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db)) -> StatsOut:
    total = db.scalar(select(func.count()).select_from(SecurityEvent)) or 0

    risk_rows = db.execute(
        select(SecurityEvent.risk_level, func.count()).group_by(SecurityEvent.risk_level)
    ).all()
    by_risk = {level.value: 0 for level in RiskLevel}
    for risk, count in risk_rows:
        by_risk[risk] = int(count)

    source_rows = db.execute(
        select(SecurityEvent.source, func.count())
        .group_by(SecurityEvent.source)
        .order_by(func.count().desc())
    ).all()
    by_source = {src: int(count) for src, count in source_rows}

    return StatsOut(total_events=int(total), by_risk_level=by_risk, by_source=by_source)
