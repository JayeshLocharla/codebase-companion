import os
import requests
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}


def fetch_repo_contents(repo_full_name, branch="main"):
    """
    Fetch top-level contents of a GitHub repo.
    Example: repo_full_name = "psf/requests"
    """
    url = f"https://api.github.com/repos/{repo_full_name}/contents/"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"GitHub API Error: {response.status_code} - {response.text}")


if __name__ == "__main__":
    repo = input("Enter repo (e.g., psf/requests): ")
    contents = fetch_repo_contents(repo)
    for item in contents:
        print(f"{item['type'].capitalize()}: {item['name']}")
