import requests

BASE_URL = "https://api.github.com"

def get_user(username):
    """Fetch GitHub user data (public only)."""
    url = f"{BASE_URL}/users/{username}"
    response = requests.get(url)  # No token
    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.json()}")
    return response.json()

def get_repos(username):
    """Fetch public repositories of a user."""
    url = f"{BASE_URL}/users/{username}/repos?per_page=100"
    response = requests.get(url)  # No token
    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.json()}")
    return response.json()

def get_commit_count(username, repo_name):
    """Count commits in public repo (default branch)."""
    url = f"{BASE_URL}/repos/{username}/{repo_name}/commits?per_page=1"
    response = requests.get(url)
    if response.status_code == 409:
        # Empty repository
        return 0
    if response.status_code != 200:
        return 0  # skip repos that fail
    # GitHub API returns the commit count in the 'Link' header for paginated results
    if 'Link' in response.headers:
        # Example: <https://api.github.com/repositories/xyz/commits?page=2>; rel="last"
        links = response.headers['Link']
        try:
            last_link = [l for l in links.split(',') if 'rel="last"' in l][0]
            last_page = int(last_link.split('page=')[1].split('>')[0])
            return last_page
        except:
            return 1
    return len(response.json())
