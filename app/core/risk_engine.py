"""
Deterministic ISO/SAE 21434 Risk Engine.
Pure mathematical functions — zero LLM dependency for regulatory scoring.
"""

# --- Attack Potential Factor Value Maps ---
ELAPSED_TIME_MAP = {
    "< 1 Month": 0,
    "<= 3 Months": 1,
    "<= 6 Months": 4,
    "> 6 Months": 10,
}

EXPERTISE_MAP = {
    "Layman": 0,
    "Proficient": 3,
    "Expert": 6,
    "Multiple Experts": 8,
}

KNOWLEDGE_MAP = {
    "Public": 0,
    "Restricted": 3,
    "Confidential": 7,
    "Strictly Confidential": 11,
}

WINDOW_MAP = {
    "Unrestricted": 0,
    "Easy": 1,
    "Moderate": 4,
    "Difficult": 10,
}

EQUIPMENT_MAP = {
    "Standard": 0,
    "Specialized": 4,
    "Bespoke": 7,
}

IMPACT_LABEL_MAP = {
    "Negligible": 1,
    "Moderate": 2,
    "Major": 3,
    "Severe": 4,
}

# --- ISO 21434 Risk Lookup Matrix (Annex G) ---
# Rows = impact (4=Severe .. 1=Negligible), Cols = feasibility
RISK_MATRIX = {
    4: {"Very Low": 2, "Low": 3, "Medium": 4, "High": 5},
    3: {"Very Low": 2, "Low": 3, "Medium": 4, "High": 4},
    2: {"Very Low": 1, "Low": 2, "Medium": 3, "High": 3},
    1: {"Very Low": 1, "Low": 1, "Medium": 1, "High": 1},
}


def calculate_attack_potential(
    elapsed_time: int,
    expertise: int,
    knowledge: int,
    window: int,
    equipment: int,
) -> str:
    """
    Sum the five attack-potential factors and return a feasibility label.

    Parameters are raw integer scores (not labels).
    """
    total_score = elapsed_time + expertise + knowledge + window + equipment
    if total_score <= 9:
        return "High"
    elif total_score <= 13:
        return "Medium"
    elif total_score <= 19:
        return "Low"
    else:
        return "Very Low"


def calculate_impact(
    safety: int,
    financial: int,
    operational: int,
    privacy: int,
) -> int:
    """Return the maximum impact score across all four dimensions."""
    return max(safety, financial, operational, privacy)


def impact_label_to_int(label: str) -> int:
    """Convert a human-readable impact label to its integer score."""
    return IMPACT_LABEL_MAP.get(label, 1)


def lookup_risk(impact_level: int, feasibility: str) -> int:
    """Look up ISO 21434 risk level from impact (1-4) and feasibility label."""
    return RISK_MATRIX.get(impact_level, {}).get(feasibility, 1)


def parse_selectbox_value(label: str) -> int:
    """
    Extract the integer score from a Streamlit selectbox label.
    E.g. '< 1 Month (0)' -> 0, 'Expert (6)' -> 6
    """
    try:
        return int(label.rsplit("(", 1)[1].rstrip(")"))
    except (IndexError, ValueError):
        return 0
