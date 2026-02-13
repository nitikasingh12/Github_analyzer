# scoring.py

def calculate_score(features, weights):
    """
    Calculate a GitHub profile score based on extracted features and configured weights.

    Parameters:
    - features: dict, output from feature_extractor.py
    - weights: dict, loaded from config.json

    Returns:
    - dict: {"total_score": float, "breakdown": dict}
    """

    # Depth score: number of repos
    depth_score = min(features.get("total_repos", 0) * 2, 30)

    # Impact score: total stars
    impact_score = min(features.get("total_stars", 0) / 1000, 25)

    # Consistency score: active repos last year
    consistency_score = min(features.get("active_repos", 0) * 2, 25)

    # Quality score: large repos
    quality_score = min(features.get("large_repos", 0) * 2, 20)

    # Penalty: single commit repos (default to 0 if missing)
    penalty_weight = weights.get("penalty", 0)
    penalty = penalty_weight * features.get("single_commit_repos", 0)

    # Total score capped between 0 and 100
    total_score = depth_score + impact_score + consistency_score + quality_score - penalty
    total_score = max(min(total_score, 100), 0)

    breakdown = {
        "depth_score": depth_score,
        "impact_score": impact_score,
        "consistency_score": consistency_score,
        "quality_score": quality_score,
        "penalty": penalty
    }

    return {"total_score": total_score, "breakdown": breakdown}
