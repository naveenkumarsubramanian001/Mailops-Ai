def calculate_trust_score(checks: dict) -> dict:
    score = 0
    reasons = []

    if checks["has_doctor"]:
        score += 25
    else:
        reasons.append("Doctor name missing")

    if checks["has_date"]:
        score += 25
    else:
        reasons.append("Date missing")

    if checks["has_hospital"]:
        score += 25
    else:
        reasons.append("Hospital name missing")

    if checks["sufficient_length"]:
        score += 25
    else:
        reasons.append("Document content too short")

    verdict = (
        "Likely Genuine" if score >= 75 else
        "Suspicious" if score >= 40 else
        "Likely Forged"
    )

    return {
        "trust_score": score,
        "verdict": verdict,
        "reasons": reasons
    }
