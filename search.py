import google.generativeai as genai
import os
from dotenv import load_dotenv
import sys
import requests
from bs4 import BeautifulSoup
from github import users_gtihub

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API KEY NOT FOUND")
    sys.exit(1)

genai.configure(api_key=api_key)
print(f"api_keY {api_key}")
def duckduckgo(query, max_results=3):
    url = "https://html.duckduckgo.com/html"
    params = {
        "q":query
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        res.raise_for_status()
    except requests.RequestException as e:
        print(f"Error querying DuckDuckGo: {e}")
        return []
    soup = BeautifulSoup(res.text, "html.parser")
    results = []
    for result in soup.find_all("div", class_="result"):
        title_tag = result.find("h2")
        snippet_tag = result.find("a", class_="result__snippet")
        if title_tag and title_tag.a:
            title = title_tag.a.get_text()
            href = title_tag.a.get("href", "")
            snippet = snippet_tag.get_text().strip() if snippet_tag else ""
            results.append((title, snippet, href))
        if len(results) >= max_results:
            break
    return results

git = users_gtihub()
                
def search(input, user, access_token):
    if not input:
        return "Please enter a valid input"
    
    tool_box = {
        "user's github issue data" : git.get_issues_of_user(user, access_token),
        "user's repositories" :  git.get_user_repo(user, access_token),
        "user's opened pull reqeuests" : git.get_user_pr(user, access_token),
        "search" : duckduckgo(input)
    }
    
    ddg_results = duckduckgo(input, 3)
    if not ddg_results:
        print("No search results found.")
        return
    context = ""
    for title, snippet, url in ddg_results:
        context += f"Title: {title}\nSnippet: {snippet}\nLink: {url}\n\n"
    prompt = (
        f'''
            You are the personalised AI assistant of {user};
            You respond to there question on {context} in 3-6 lines concisely;
            user asked this {input}.
            Answer concisely (3-6 lines) in plain text.
            Address them with their name {user} except the numbers, and answer.
            You can use tools from {tool_box} to perform github or search work.
            Address to them if you face any problem
        '''
    )
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return
    answer = response.text.strip()
    return answer