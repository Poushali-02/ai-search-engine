import requests

class users_gtihub:
    def get_issues_of_user(self, username:str, access_token):
        if not username or not access_token:
            return "GitHub credentials not found. Please log in with GitHub."
        url = f"https://api.github.com/search/issues?q=assignee:{username}+is:open"
        headers = {
            "Authorization" : f"token {access_token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "AISearchEngine/1.0"
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                issues_data = response.json()
                issues = issues_data.get("items", [])
                if issues:
                    issue_list = [f"- {issue['title']} (#{issue['number']})" for issue in issues]
                    return "\n".join(issue_list)
                else:
                    return "no issues are assigned to you currently! You're free!"
            else:
                print(f"Error response: {response.text}")
                return f"Error: Error fetcxhing issues: {response.text}"
        except Exception as e:
            return f"Error fetching issues: {str(e)}"
        
    def get_user_pr(self, username, access_token):
        if not username or not access_token:
            return "GitHub credentials not found. Please log in with GitHub."
        url = f"https://api.github.com/search/issues?q=author:{username}+is:open+type:pr"
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "AISearchEngine/1.0"
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                pr_data = response.json()
                pull_requests = pr_data.get("items", [])
                if pull_requests:
                    pr_list = [f"- {pr['title']} (#{pr['number']}) in {pr['repository_url'].split('/')[-1]}" for pr in pull_requests]
                    return "Here are your open pull requests:\n" + "\n".join(pr_list)
                else:
                    return "You don't have any open pull requests at the moment."
            else:
                print(f"Error response: {response.status_code} - {response.text}")
                return f"Error fetching pull requests: {response.status_code} - {response.text}"
        except requests.exceptions.RequestException as e:
            return f"Error fetching pull requests: {str(e)}"

    def get_user_repo(self, username, access_token):
        if not username or not access_token:
            return "GitHub credentials not found. Please log in with GitHub."
        headers = {'Authorization': f'token {access_token}',
                'Accept': 'application/vnd.github+json',
                'User-Agent': 'AISearchEngine/1.0'}
        try:
            response = requests.get(f'https://api.github.com/users/{username}/repos', headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching GitHub repos: {e}")
            return None

