import os
from app.utils.github import download_github_repo
from app.chains.review_chain import run_pipeline

def main():
    print("🤖 Codebase Companion")
    repo_url = input("🔗 Enter a full GitHub repo URL (e.g. https://github.com/psf/requests): ").strip()

    try:
        local_path = download_github_repo(repo_url)
        run_pipeline(repo_path=local_path, max_files=3)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
