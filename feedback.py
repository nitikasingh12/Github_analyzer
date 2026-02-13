def generate_feedback(features):
    strengths = []
    red_flags = []
    recommendations = []

    if features["original_repos"] > 5:
        strengths.append("Strong number of original repositories.")
    if features["total_stars"] > 50:
        strengths.append("Profile shows external validation through stars.")
    if features["active_repos"] > 0:
        strengths.append("Consistent development activity.")

    if features["single_commit_repos"] > 2:
        red_flags.append("Several repositories with only one commit.")
    if features["fork_ratio"] > 0.7:
        red_flags.append("Too many forked repositories relative to originals.")

    if features["single_commit_repos"] > 0:
        recommendations.append("Consider adding more commits to existing repos.")
    if features["original_repos"] < 5:
        recommendations.append("Consider creating more original projects.")

    return {
        "strengths": strengths,
        "red_flags": red_flags,
        "recommendations": recommendations
    }
