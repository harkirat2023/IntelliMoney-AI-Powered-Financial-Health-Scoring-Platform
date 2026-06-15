# Expense Classifier

Run the training script from the repository root:

```bash
python ml/train_model.py
```

The script trains a `TfidfVectorizer + LogisticRegression` pipeline and writes
`expense_classifier.joblib` into this directory. The API falls back to keyword
classification when the model file has not been generated yet.
