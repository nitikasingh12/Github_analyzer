from github_api import get_commit_count
from datetime import datetime

def extract_features(username, repos):
    total_stars = 0
    total_forks = 0
    original_repos = 0
    forked_repos = 0
    active_repos = 0
    large_repos = 0
    single_commit_repos = 0

    current_year = datetime.now().year

    for repo in repos:
        total_stars += repo.get("stargazers_count", 0)
        total_forks += repo.get("forks_count", 0)

        if repo.get("fork", False):
            forked_repos += 1
        else:
            original_repos += 1

        if repo.get("size", 0) > 500:
            large_repos += 1

        updated_at = repo.get("updated_at")
        if updated_at:
            updated_year = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ").year
            if updated_year >= current_year - 1:
                active_repos += 1

        try:
            commits = get_commit_count(username, repo["name"])
            if commits <= 1:
                single_commit_repos += 1
        except:
            pass  # Ignore repos with API errors

    fork_ratio = forked_repos / len(repos) if repos else 0

    return {
        "total_repos": len(repos),
        "total_stars": total_stars,
        "total_forks": total_forks,
        "original_repos": original_repos,
        "fork_ratio": fork_ratio,
        "active_repos": active_repos,
        "large_repos": large_repos,
        "single_commit_repos": single_commit_repos
    }
