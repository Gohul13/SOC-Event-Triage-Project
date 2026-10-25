# Classifier validation

After running `python ml/train.py`, inspect `ml/models/training_metrics.json`.

**Method**

- Model: `TfidfVectorizer(ngram_range=(1,2))` → `LogisticRegression(class_weight="balanced")`
- Split: 75% train / 25% test, stratified by label, `random_state=42`
- Metrics: accuracy and macro F1 on the holdout set, plus per-class precision/recall in the classification report

On the bundled synthetic dataset (60 lines, keyword-rich labels), holdout accuracy is typically **very high** (often 100%) because benign vs suspicious vs malicious lines use distinct vocabulary. This is acceptable for the assignment demo but would **not** generalize to production logs without richer data and ongoing retraining.
