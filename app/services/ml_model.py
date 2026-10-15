"""
Machine Learning Pipeline for Automotive TARA (ISO/SAE 21434).

Trains and evaluates two sklearn classifiers:
  1. STRIDE Category Classifier    — RandomForestClassifier
  2. Risk Level Classifier         — GradientBoostingClassifier

Generates a reproducible synthetic dataset derived from ISO 21434 Annex G
parameter ranges, trains with stratified 80/20 split, evaluates with
accuracy, weighted F1, and 5-fold cross-validation.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler

# ── Constants ────────────────────────────────────────────────────────────────

STRIDE_CATEGORIES: List[str] = [
    "Spoofing",
    "Tampering",
    "Repudiation",
    "Information Disclosure",
    "Denial of Service",
    "Elevation of Privilege",
]

ELAPSED_TIME_VALS = [0, 1, 4, 10]
EXPERTISE_VALS    = [0, 3, 6, 8]
KNOWLEDGE_VALS    = [0, 3, 7, 11]
WINDOW_VALS       = [0, 1, 4, 10]
EQUIPMENT_VALS    = [0, 4, 7]

_RISK_MATRIX: Dict[int, Dict[str, int]] = {
    4: {"Very Low": 2, "Low": 3, "Medium": 4, "High": 5},
    3: {"Very Low": 2, "Low": 3, "Medium": 4, "High": 4},
    2: {"Very Low": 1, "Low": 2, "Medium": 3, "High": 3},
    1: {"Very Low": 1, "Low": 1, "Medium": 1, "High": 1},
}

STRIDE_PROFILES: Dict[str, Dict[str, List[int]]] = {
    "Spoofing": {
        "et": [0, 1], "exp": [0, 3], "know": [0, 3], "win": [0, 1], "equip": [0, 4],
        "i_s": [2, 3], "i_f": [2, 3], "i_o": [2, 3], "i_p": [1, 2]
    },
    "Tampering": {
        "et": [1, 4], "exp": [3, 6], "know": [3, 7], "win": [1, 4], "equip": [4, 7],
        "i_s": [3, 4], "i_f": [2, 3], "i_o": [3, 4], "i_p": [1, 2]
    },
    "Repudiation": {
        "et": [0, 1], "exp": [0, 3], "know": [3, 7], "win": [0, 1], "equip": [0, 4],
        "i_s": [1, 1], "i_f": [3, 4], "i_o": [2, 3], "i_p": [2, 3]
    },
    "Information Disclosure": {
        "et": [1, 4], "exp": [3, 6], "know": [3, 7], "win": [0, 1], "equip": [0, 4],
        "i_s": [1, 1], "i_f": [2, 3], "i_o": [1, 2], "i_p": [3, 4]
    },
    "Denial of Service": {
        "et": [0, 1], "exp": [0, 3], "know": [0, 3], "win": [0, 1], "equip": [0, 0],
        "i_s": [2, 3], "i_f": [1, 2], "i_o": [3, 4], "i_p": [1, 1]
    },
    "Elevation of Privilege": {
        "et": [4, 10], "exp": [6, 8], "know": [7, 11], "win": [4, 10], "equip": [4, 7],
        "i_s": [3, 4], "i_f": [3, 4], "i_o": [3, 4], "i_p": [3, 4]
    },
}

FEATURE_COLS_STRIDE = [
    "elapsed_time", "expertise", "knowledge", "window", "equipment",
    "impact_safety", "impact_financial", "impact_operational", "impact_privacy",
    "attack_score", "max_impact",
]

FEATURE_COLS_RISK = [
    "elapsed_time", "expertise", "knowledge", "window", "equipment",
    "impact_safety", "impact_financial", "impact_operational", "impact_privacy",
]


# ── Dataset generation ───────────────────────────────────────────────────────

def _feasibility(score: int) -> str:
    if score <= 9:
        return "High"
    elif score <= 13:
        return "Medium"
    elif score <= 19:
        return "Low"
    return "Very Low"


def generate_synthetic_dataset(n_per_class: int = 150, seed: int = 42) -> pd.DataFrame:
    """
    Build a synthetic automotive threat dataset with realistic ISO 21434
    parameter distributions (n_per_class samples per STRIDE category).
    """
    rng = np.random.default_rng(seed)
    records: List[Dict[str, Any]] = []

    for stride, p in STRIDE_PROFILES.items():
        for _ in range(n_per_class):
            et    = int(rng.choice(p["et"]))
            exp   = int(rng.choice(p["exp"]))
            know  = int(rng.choice(p["know"]))
            win   = int(rng.choice(p["win"]))
            equip = int(rng.choice(p["equip"]))
            i_s   = int(rng.choice(p["i_s"]))
            i_f   = int(rng.choice(p["i_f"]))
            i_o   = int(rng.choice(p["i_o"]))
            i_p   = int(rng.choice(p["i_p"]))
            score   = et + exp + know + win + equip
            max_imp = max(i_s, i_f, i_o, i_p)
            feas    = _feasibility(score)
            risk_lvl = _RISK_MATRIX[max_imp][feas]
            records.append({
                "elapsed_time": et, "expertise": exp, "knowledge": know,
                "window": win, "equipment": equip,
                "impact_safety": i_s, "impact_financial": i_f,
                "impact_operational": i_o, "impact_privacy": i_p,
                "attack_score": score, "max_impact": max_imp,
                "feasibility": feas, "stride": stride, "risk_level": risk_lvl,
            })

    return pd.DataFrame(records).sample(frac=1, random_state=seed).reset_index(drop=True)


# ── ML Pipeline class ────────────────────────────────────────────────────────

class TARAMLPipeline:
    """End-to-end sklearn ML pipeline for TARA threat analysis."""

    def __init__(self) -> None:
        self.df: pd.DataFrame | None = None
        self.stride_encoder = LabelEncoder()
        self.stride_model: Pipeline | None = None
        self.risk_model:   Pipeline | None = None
        self.stride_metrics: Dict[str, Any] = {}
        self.risk_metrics:   Dict[str, Any] = {}
        self.is_trained = False
        self.y_te_s:   np.ndarray | None = None
        self.y_pred_s: np.ndarray | None = None
        self.y_te_r:   np.ndarray | None = None
        self.y_pred_r: np.ndarray | None = None
        self.cv_s: np.ndarray | None = None
        self.cv_r: np.ndarray | None = None
        self.feat_importance: Dict[str, float] = {}

    def load_or_generate_dataset(
        self, csv_path: str | None = None, n_per_class: int = 150
    ) -> pd.DataFrame:
        if csv_path and os.path.exists(csv_path):
            self.df = pd.read_csv(csv_path)
        else:
            self.df = generate_synthetic_dataset(n_per_class=n_per_class)
            if csv_path:
                Path(csv_path).parent.mkdir(parents=True, exist_ok=True)
                self.df.to_csv(csv_path, index=False)
        return self.df

    def train(self) -> Dict[str, Dict[str, Any]]:
        """Train both classifiers. Returns evaluation metrics."""
        if self.df is None:
            self.load_or_generate_dataset()
        assert self.df is not None
        df = self.df

        # ── 1. STRIDE Classifier (RandomForest) ──────────────────────────────
        X_s = df[FEATURE_COLS_STRIDE].values
        y_s = self.stride_encoder.fit_transform(df["stride"].values)

        X_tr_s, X_te_s, y_tr_s, y_te_s = train_test_split(
            X_s, y_s, test_size=0.2, random_state=42, stratify=y_s
        )
        self.y_te_s = y_te_s

        self.stride_model = Pipeline([
            ("scaler", StandardScaler()),
            ("clf",    RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42)),
        ])
        self.stride_model.fit(X_tr_s, y_tr_s)
        self.y_pred_s = self.stride_model.predict(X_te_s)
        self.cv_s = cross_val_score(self.stride_model, X_s, y_s, cv=5, scoring="f1_weighted")

        self.feat_importance = dict(
            zip(FEATURE_COLS_STRIDE,
                self.stride_model.named_steps["clf"].feature_importances_)
        )
        labels = list(self.stride_encoder.classes_)
        self.stride_metrics = {
            "accuracy":           float(accuracy_score(y_te_s, self.y_pred_s)),
            "f1_weighted":        float(f1_score(y_te_s, self.y_pred_s, average="weighted")),
            "precision_weighted": float(precision_score(y_te_s, self.y_pred_s, average="weighted", zero_division=0)),
            "recall_weighted":    float(recall_score(y_te_s, self.y_pred_s, average="weighted", zero_division=0)),
            "cv_f1_mean":         float(self.cv_s.mean()),
            "cv_f1_std":          float(self.cv_s.std()),
            "confusion_matrix":   confusion_matrix(y_te_s, self.y_pred_s).tolist(),
            "class_labels":       labels,
            "classification_report": classification_report(
                y_te_s, self.y_pred_s, target_names=labels, output_dict=True
            ),
        }

        # ── 2. Risk Level Classifier (GradientBoosting) ──────────────────────
        X_r = df[FEATURE_COLS_RISK].values
        y_r = df["risk_level"].values

        X_tr_r, X_te_r, y_tr_r, y_te_r = train_test_split(
            X_r, y_r, test_size=0.2, random_state=42, stratify=y_r
        )
        self.y_te_r = y_te_r

        self.risk_model = Pipeline([
            ("scaler", StandardScaler()),
            ("clf",    GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)),
        ])
        self.risk_model.fit(X_tr_r, y_tr_r)
        self.y_pred_r = self.risk_model.predict(X_te_r)
        self.cv_r = cross_val_score(self.risk_model, X_r, y_r, cv=5, scoring="f1_weighted")

        risk_labels = [str(l) for l in sorted(np.unique(y_r))]
        self.risk_metrics = {
            "accuracy":    float(accuracy_score(y_te_r, self.y_pred_r)),
            "f1_weighted": float(f1_score(y_te_r, self.y_pred_r, average="weighted")),
            "cv_f1_mean":  float(self.cv_r.mean()),
            "cv_f1_std":   float(self.cv_r.std()),
            "confusion_matrix": confusion_matrix(y_te_r, self.y_pred_r).tolist(),
            "class_labels": risk_labels,
            "classification_report": classification_report(
                y_te_r, self.y_pred_r, output_dict=True
            ),
        }

        self.is_trained = True
        return {"stride": self.stride_metrics, "risk": self.risk_metrics}

    def predict_stride(self, features: List[float]) -> Tuple[str, Dict[str, float]]:
        """Predict STRIDE category and return per-class probabilities."""
        if not self.is_trained or self.stride_model is None:
            self.train()
        assert self.stride_model is not None
        proba = self.stride_model.predict_proba([features])[0]
        pred_idx = int(np.argmax(proba))
        label = self.stride_encoder.inverse_transform([pred_idx])[0]
        return label, dict(zip(self.stride_encoder.classes_, proba))

    def predict_risk(self, features: List[float]) -> int:
        """Predict ISO 21434 risk level (1–5)."""
        if not self.is_trained or self.risk_model is None:
            self.train()
        assert self.risk_model is not None
        return int(self.risk_model.predict([features])[0])

    def get_feature_importance(self) -> Dict[str, float]:
        return dict(sorted(self.feat_importance.items(), key=lambda x: x[1], reverse=True))


# ── Singleton accessor ───────────────────────────────────────────────────────

_pipeline: TARAMLPipeline | None = None


def get_ml_pipeline(reload: bool = False) -> TARAMLPipeline:
    """Return the trained singleton TARAMLPipeline (lazy init)."""
    global _pipeline
    if _pipeline is None or reload:
        _pipeline = TARAMLPipeline()
        dataset_path = str(
            Path(__file__).resolve().parent.parent.parent / "data" / "threat_training_data.csv"
        )
        _pipeline.load_or_generate_dataset(csv_path=dataset_path)
        _pipeline.train()
    return _pipeline
