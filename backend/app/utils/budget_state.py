"""Budget usage state thresholds (single source of truth).

Spec: <75% = Healthy (safe); 75-89% = Warning; 90-99% = Critical; >=100% = Exceeded (over).
"""

# The percentage at which each state begins (ascending exclusive bounds).
THRESHOLD_WARNING = 75
THRESHOLD_CRITICAL = 90
THRESHOLD_OVER = 100


def get_budget_state(percentage_used: float) -> str:
    """Map a budget usage percentage to its state.

    Returns one of ``safe`` / ``warning`` / ``critical`` / ``over`` so the
    threshold logic stays identical across every consumer.
    """
    if percentage_used >= THRESHOLD_OVER:
        return "over"
    if percentage_used >= THRESHOLD_CRITICAL:
        return "critical"
    if percentage_used >= THRESHOLD_WARNING:
        return "warning"
    return "safe"