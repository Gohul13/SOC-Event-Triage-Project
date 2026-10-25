import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RiskLevel(str, enum.Enum):
    BENIGN = "Benign"
    SUSPICIOUS = "Suspicious"
    MALICIOUS = "Malicious"


class EventStatus(str, enum.Enum):
    PENDING = "Pending"
    REVIEWED = "Reviewed"
    FALSE_POSITIVE = "False Positive"
    ESCALATED = "Escalated"


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    raw_log: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    risk_level: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=EventStatus.PENDING.value, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
