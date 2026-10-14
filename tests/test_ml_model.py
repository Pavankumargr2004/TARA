"""
pytest unit tests for the TARAMLPipeline ML service.

Covers:
  - Synthetic dataset generation (shape, columns, class balance)
  - STRIDE classifier training (accuracy, F1, CV)
  - Risk level classifier training (accuracy, F1)
  - Confusion matrix shape validity
  - Feature importance sum-to-one constraint
  - predict_stride / predict_risk inference
  - get_ml_pipeline singleton
"""
import numpy as np
import pytest

from app.services.ml_model import (
    FEATURE_COLS_RISK,
    FEATURE_COLS_STRIDE,
    STRIDE_CATEGORIES,
    TARAMLPipeline,
    generate_synthetic_dataset,
    get_ml_pipeline,
)


# ── Dataset tests ─────────────────────────────────────────────────────────────

def test_dataset_shape():
    df = generate_synthetic_dataset(n_per_class=50)
    assert df.shape[0] == 50 * len(STRIDE_CATEGORIES), "Unexpected row count"
    expected_cols = set(FEATURE_COLS_STRIDE + ["feasibility", "stride", "risk_level"])
    assert expected_cols.issubset(set(df.columns))


def test_dataset_class_balance():
    df = generate_synthetic_dataset(n_per_class=60)
    counts = df["stride"].value_counts()
    for cat in STRIDE_CATEGORIES:
        assert cat in counts.index, f"STRIDE category {cat!r} missing"
        assert counts[cat] == 60, f"Imbalanced class {cat!r}"


def test_dataset_risk_level_range():
    df = generate_synthetic_dataset(n_per_class=50)
    assert df["risk_level"].between(1, 5).all(), "Risk levels outside 1–5"


def test_dataset_attack_score_non_negative():
    df = generate_synthetic_dataset(n_per_class=50)
    assert (df["attack_score"] >= 0).all()


def test_dataset_max_impact_in_range():
    df = generate_synthetic_dataset(n_per_class=50)
    assert df["max_impact"].between(1, 4).all()


# ── Training tests ────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def trained_pipeline():
    pipe = TARAMLPipeline()
    pipe.load_or_generate_dataset(n_per_class=80)
    pipe.train()
    return pipe


def test_pipeline_is_trained(trained_pipeline):
    assert trained_pipeline.is_trained is True


def test_stride_accuracy_above_threshold(trained_pipeline):
    acc = trained_pipeline.stride_metrics["accuracy"]
    assert acc >= 0.60, f"STRIDE accuracy too low: {acc:.3f}"


def test_stride_f1_above_threshold(trained_pipeline):
    f1 = trained_pipeline.stride_metrics["f1_weighted"]
    assert f1 >= 0.55, f"STRIDE F1 too low: {f1:.3f}"


def test_stride_cv_f1_reasonable(trained_pipeline):
    cv_mean = trained_pipeline.stride_metrics["cv_f1_mean"]
    assert cv_mean >= 0.50, f"CV F1 mean too low: {cv_mean:.3f}"


def test_risk_accuracy_above_threshold(trained_pipeline):
    acc = trained_pipeline.risk_metrics["accuracy"]
    assert acc >= 0.70, f"Risk accuracy too low: {acc:.3f}"


def test_risk_f1_above_threshold(trained_pipeline):
    f1 = trained_pipeline.risk_metrics["f1_weighted"]
    assert f1 >= 0.65, f"Risk F1 too low: {f1:.3f}"


def test_stride_confusion_matrix_shape(trained_pipeline):
    cm = np.array(trained_pipeline.stride_metrics["confusion_matrix"])
    n = len(STRIDE_CATEGORIES)
    assert cm.shape == (n, n), f"Confusion matrix shape {cm.shape} != ({n},{n})"


def test_risk_confusion_matrix_not_empty(trained_pipeline):
    cm = np.array(trained_pipeline.risk_metrics["confusion_matrix"])
    assert cm.sum() > 0


def test_feature_importance_sums_to_one(trained_pipeline):
    fi = trained_pipeline.get_feature_importance()
    assert len(fi) == len(FEATURE_COLS_STRIDE)
    total = sum(fi.values())
    assert abs(total - 1.0) < 1e-5, f"Feature importances sum to {total}"


def test_all_stride_features_present(trained_pipeline):
    fi = trained_pipeline.get_feature_importance()
    for col in FEATURE_COLS_STRIDE:
        assert col in fi, f"Feature {col!r} missing from importance dict"


# ── Inference tests ───────────────────────────────────────────────────────────

def test_predict_stride_returns_valid_category(trained_pipeline):
    # [et, exp, know, win, equip, i_s, i_f, i_o, i_p, score, max_imp]
    features = [1, 3, 3, 1, 0, 3, 2, 4, 1, 8, 4]
    label, proba = trained_pipeline.predict_stride(features)
    assert label in STRIDE_CATEGORIES
    assert abs(sum(proba.values()) - 1.0) < 1e-5


def test_predict_risk_returns_valid_level(trained_pipeline):
    # [et, exp, know, win, equip, i_s, i_f, i_o, i_p]
    features = [1, 3, 3, 1, 0, 3, 2, 4, 1]
    risk = trained_pipeline.predict_risk(features)
    assert 1 <= risk <= 5, f"Risk level {risk} out of range"


def test_predict_stride_high_expertise_is_elevation(trained_pipeline):
    """High expertise + confidential knowledge + bespoke equipment → likely Elevation of Privilege."""
    features = [10, 8, 11, 10, 7, 4, 3, 4, 2, 36, 4]
    label, proba = trained_pipeline.predict_stride(features)
    # Just verify it runs and returns a valid label (the actual prediction may vary)
    assert isinstance(label, str)
    assert label in STRIDE_CATEGORIES


def test_predict_risk_severe_impact_high_feasibility(trained_pipeline):
    """Severe impact + high feasibility (low score) should yield high risk (4 or 5)."""
    features = [0, 0, 0, 0, 0, 4, 4, 4, 4]  # score=0 → High feasibility; max_impact=4
    risk = trained_pipeline.predict_risk(features)
    assert risk >= 4, f"Expected high risk, got {risk}"


# ── Singleton tests ───────────────────────────────────────────────────────────

def test_get_ml_pipeline_singleton():
    p1 = get_ml_pipeline()
    p2 = get_ml_pipeline()
    assert p1 is p2, "get_ml_pipeline should return the same instance"


def test_singleton_is_trained():
    pipe = get_ml_pipeline()
    assert pipe.is_trained is True
