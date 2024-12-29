import datetime
from dateutil import relativedelta
import requests
import os
import time

# Configuration
HEADERS = {'authorization': 'token '+ os.environ['ACCESS_TOKEN']}
USER_NAME = 'JpCurada'
QUERY_COUNT = {'user_getter': 0, 'follower_getter': 0, 'graph_commits': 0}

def daily_readme(birthday):
    """
    Returns the length of time since birth date
    e.g. 'XX years, XX months, XX days'
    """
    diff = relativedelta.relativedelta(datetime.datetime.today(), birthday)
    return '{} {}, {} {}, {} {}'.format(
        diff.years, 'year' + ('s' if diff.years != 1 else ''), 
        diff.months, 'month' + ('s' if diff.months != 1 else ''), 
        diff.days, 'day' + ('s' if diff.days != 1 else ''))

def simple_request(func_name, query, variables):
    """
    Makes a GitHub GraphQL API request
    """
    try:
        request = requests.post(
            'https://api.github.com/graphql', 
            json={'query': query, 'variables': variables}, 
            headers=HEADERS
        )
        
        if request.status_code == 200:
            return request
            
        print(f"Request failed with status {request.status_code}")
        print("Response:", request.text)
        raise Exception(f"{func_name} failed: {request.status_code} {request.text}")
        
    except Exception as e:
        print(f"Error in {func_name}: {str(e)}")
        raise

def graph_commits(start_date, end_date):
    """
    Fetches total commit count using GitHub's GraphQL API
    """
    query_count('graph_commits')
    query = '''
    query($start_date: DateTime!, $end_date: DateTime!, $login: String!) {
        user(login: $login) {
            contributionsCollection(from: $start_date, to: $end_date) {
                totalCommitContributions
                restrictedContributionsCount
            }
        }
    }'''
    variables = {
        'start_date': start_date,
        'end_date': end_date,
        'login': USER_NAME
    }
    request = simple_request(graph_commits.__name__, query, variables)
    data = request.json()
    
    # Add error handling and debugging
    if data.get('data') is None or data.get('data').get('user') is None:
        print("API Response:", data)
        return 0  # Return 0 if no data is found
        
    contributions = data['data']['user']['contributionsCollection']
    return contributions['totalCommitContributions'] + contributions['restrictedContributionsCount']

def follower_getter():
    """
    Fetches follower count using GitHub's GraphQL API
    """
    query_count('follower_getter')
    query = '''
    query($login: String!) {
        user(login: $login) {
            followers {
                totalCount
            }
            repositories(first: 100, privacy: PUBLIC) {
                totalCount
                nodes {
                    stargazerCount
                }
            }
        }
    }'''
    request = simple_request(follower_getter.__name__, query, {'login': USER_NAME})
    data = request.json()['data']['user']
    stars = sum(repo['stargazerCount'] for repo in data['repositories']['nodes'])
    return {
        'followers': data['followers']['totalCount'],
        'repositories': data['repositories']['totalCount'],
        'stars': stars
    }

def query_count(funct_id):
    """
    Tracks API call counts
    """
    global QUERY_COUNT
    QUERY_COUNT[funct_id] += 1

def generate_ascii_art():
    """
    Returns ASCII art for the profile
    """
    return """
    ╱|、
   (˚ˎ 。7  
    |、˜〵          
    じしˍ,)ノ
    """

def generate_readme(stats):
    """
    Generates README content
    """
    return f"""<h1 align="center">Hi 👋, I'm John Paul Curada</h1>

{generate_ascii_art()}

<p align="center">
    <img src="https://readme-typing-svg.herokuapp.com?font=consolas&size=30&duration=4000&color=42047E&center=true&vCenter=true&width=550&height=75&lines=Computer+Science+Student;Software+Developer;Python+|+C+|+Go+Enthusiast">
</p>

## About Me
- 🎓 {stats['age']} old
- 📚 BS Computer Science student at Polytechnic University of the Philippines
- 💻 Currently in my 2nd year
- 🌱 Learning Python, C, Go, SQL, and Web Development

## GitHub Stats
- 📊 Public Repositories: {stats['repositories']}
- ⭐ Total Stars Earned: {stats['stars']}
- 👥 Followers: {stats['followers']}
- 🔥 Total Commits: {stats['commits']}

## Tech Stack
- Languages: Python, C, Go, SQL
- Web Development: HTML/CSS
- Tools: Git, VS Code

## 🤝 Connect With Me
- 📧 Email: johncurada.02@gmail.com
- 🔗 LinkedIn: [JpCurada](https://www.linkedin.com/in/jpcurada/)
- 🐱 GitHub: [JpCurada](https://github.com/JpCurada)

---
<p align="center">Last updated: {datetime.datetime.now().strftime('%B %d, %Y')}</p>
"""

if __name__ == '__main__':
    try:
        print("Fetching GitHub stats...")
        
        # Calculate age
        birth_date = datetime.datetime(2004, 10, 2)
        age = daily_readme(birth_date)
        
        # Fetch GitHub stats
        social_stats = follower_getter()
        commits = graph_commits('2020-01-01T00:00:00Z', 
                              datetime.datetime.now().isoformat())
        
        # Compile stats
        stats = {
            'age': age,
            'commits': commits,
            'repositories': social_stats['repositories'],
            'stars': social_stats['stars'],
            'followers': social_stats['followers']
        }
        
        # Generate and save README
        readme_content = generate_readme(stats)
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
            
        print("README.md updated successfully!")
        print(f"API calls made: {sum(QUERY_COUNT.values())}")
        
    except Exception as e:
        print(f"Error updating README: {str(e)}")
        raise
