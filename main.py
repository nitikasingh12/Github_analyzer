import sys
import json
from github_api import get_user, get_repos
from feature_extractor import extract_features
from scoring import calculate_score
from feedback import generate_feedback
from ml_model import predict_profile

def main(username):
    with open("config.json") as f:
        config = json.load(f)
    weights = config["weights"]

    print("Fetching GitHub data...")
    user = get_user(username)
    repos = get_repos(username)

    if not repos:
        print("No public repositories found.")
        return

    print("Extracting features...")
    features = extract_features(username, repos)

    print("Calculating score...")
    score_data = calculate_score(features, weights)

    print("Generating feedback...")
    feedback = generate_feedback(features)

    print("Running ML classification...")
    ml_prediction = predict_profile(features)

    print("\n==============================")
    print("GitHub Recruiter Evaluation")
    print("==============================")
    print(f"Username: {username}")
    print(f"Total Score: {score_data['total_score']} / 100\n")

    score = score_data["total_score"]

    if score >= 85:
        tier = "Elite Engineering Profile"
    elif score >= 70:
        tier = "Strong Engineering Profile"
    elif score >= 50:
        tier = "Developing Engineering Profile"
    else:
        tier = "Needs Significant Improvement"

    print(f"Profile Tier: {tier}")
    print(f"ML Model Classification: {ml_prediction}\n")

    print("Breakdown:")
    for k, v in score_data["breakdown"].items():
        print(f"{k}: {v}")

    print("\nSignal Summary:")
    print(f"- Total Repositories: {features['total_repos']}")
    print(f"- Original Repositories: {features['original_repos']}")
    print(f"- Total Stars: {features['total_stars']}")
    print(f"- Active Repositories (Last Year): {features['active_repos']}")
    print()

    print("Strengths:")
    for s in feedback["strengths"]:
        print("-", s)

    print("\nRed Flags:")
    for r in feedback["red_flags"]:
        print("-", r)

    print("\nRecommendations:")
    for rec in feedback["recommendations"]:
        print("-", rec)

    with open("report.json", "w") as f:
        json.dump({
            "username": username,
            "score": score_data,
            "tier": tier,
            "ml_classification": ml_prediction,
            "features": features,
            "feedback": feedback
        }, f, indent=4)

    print("\nReport exported to report.json")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <github_username>")
    else:
        main(sys.argv[1])
