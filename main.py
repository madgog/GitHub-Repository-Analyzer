import sys
import requests
from datetime import datetime, timedelta, timezone

from ActivityLevel import ActivityLevel
from Statuses import DeadStatus, LiveStatus, StagnantStatus


def parse_github_url(url):
    if "github.com" in url:
        return url.replace("https://github.com/", "https://api.github.com/repos/")
    else:
        print("Invalid GitHub URL")
        return None

def setup_headers(github_token):
    if github_token:
        return {"Authorization": f"Bearer {github_token}"}
    else:
        return {}

def get_repo_data(url, headers):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print("Repository not found!")
            return None
        else:
            print(f"Error fetching data: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def get_contributors(url, headers):
    try:
        response = requests.get(url + "/contributors", params={"per_page": 5}, headers=headers)
        if response.status_code == 200:
            contributors_data = response.json()
            return [(contributor['login'], contributor['contributions']) for contributor in contributors_data]
        else:
            print(f"Error fetching contributors: {response.status_code}")
            return []
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []

def get_recent_commits(url, headers):
    try:
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        commits_list = []

        for page in range(1,100):
            response = requests.get(url + "/commits", 
                                    params={"since": seven_days_ago, "per_page": 100, "page": page}, 
                                    headers=headers)
            if response.status_code == 200:
                commits = response.json()
                if not commits:
                    break
                commits_list.extend(commits)
            else:
                print(f"Error fetching commits: {response.status_code}")
                return 0
        return len(commits_list)
    
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return 0

def get_maintainer_activity(url, headers):
    try:
        response = requests.get(
            url + "/issues",
            params={"state": "all", "per_page": 100, "sort": "updated"},
            headers=headers
        )

        if response.status_code != 200:
            print(f"Error fetching issues: {response.status_code}")
            return None

        issues = response.json()
        
        for issue in issues:
            if issue.get('comments', 0) > 0:
                comments_url = issue['comments_url']
                comments_response = requests.get(comments_url, headers=headers)
                
                if comments_response.status_code == 200:
                    comments = comments_response.json()
                    
                    for comment in comments:
                        comment_date = datetime.fromisoformat(
                            comment['created_at'].replace('Z', '+00:00')
                        )
                        
                        if comment['author_association'] in ['OWNER', 'MEMBER', 'COLLABORATOR']:
                            for activity in ActivityLevel:
                                if comment_date > activity.value:
                                    return activity.name
        
        return None
        
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def parse_arguments():
    if len(sys.argv) < 2:
        print("Usage: python main.py <github_repo_url> [options]")
        print("Options:")
        print("  -t <token>         GitHub token for authentication")
        return None, None
    
    repo_url = sys.argv[1]
    github_token = None
    
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ['-t', '--token']:
            if i + 1 < len(sys.argv):
                github_token = sys.argv[i + 1]
                i += 1  # Skip next argument since it's the token
            else:
                print("Error: -t flag requires a token value")
                return None, None
        i += 1
    
    return repo_url, github_token

def print_results(repo_data, contributors, recent_commits_count, status):
    print(f"\nGitHub Repository Analysis")

    print(f"\nName: {repo_data['name']}")
    print(f"Description: {repo_data.get('description', 'No description available')}")
    print(f"Stars: {repo_data['stargazers_count']:,}")
    print(f"Forks: {repo_data['forks_count']:,}")
    print(f"Open Issues: {repo_data['open_issues_count']:,}")
    
    print(f"\nTop 5 Contributors:")
    if contributors:
        for i, (login, contributions) in enumerate(contributors, 1):
            print(f"  {i}. {login} ({contributions:,} commits)")
    else:
        print("  No contributors")
    
    print(f"\nCommits in last 7 days: {recent_commits_count}")
    
    print(f"\nRepository Status: {status}\n")

def main():
    repo_url, github_token = parse_arguments()
    if not repo_url:
        return
    
    api_url = parse_github_url(repo_url)
    if not api_url:
        return
    
    headers = setup_headers(github_token)
    
    print(f"Analyzing repository: {repo_url}")

    repo_data = get_repo_data(api_url, headers)
    if not repo_data:
        return
    
    contributors = get_contributors(api_url, headers)
    recent_commits_count = get_recent_commits(api_url, headers)
    maintainer_activity = get_maintainer_activity(api_url, headers)
    status = "";

    status_checks = [
            DeadStatus(),
            LiveStatus(),
            StagnantStatus(),
        ]
    
    for status_check in status_checks:
        if status_check.matches(repo_data, recent_commits_count, maintainer_activity):
            status = status_check.get_status_name()
    
    print_results(repo_data, contributors, recent_commits_count, status)

if __name__ == "__main__":
    main()