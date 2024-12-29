import datetime
from dateutil import relativedelta
import requests
import os

# Configuration
HEADERS = {'authorization': 'token '+ os.environ['ACCESS_TOKEN']}
USER_NAME = 'JpCurada'

def daily_readme(birthday):
    """Returns age in years, months, days format"""
    diff = relativedelta.relativedelta(datetime.datetime.today(), birthday)
    return '{} {}, {} {}, {} {}'.format(
        diff.years, 'year' + ('s' if diff.years != 1 else ''), 
        diff.months, 'month' + ('s' if diff.months != 1 else ''), 
        diff.days, 'day' + ('s' if diff.days != 1 else ''))

def github_api_query(query, variables=None):
    """Makes a GitHub GraphQL API request"""
    request = requests.post(
        'https://api.github.com/graphql',
        json={'query': query, 'variables': variables},
        headers=HEADERS
    )
    if request.status_code == 200:
        return request.json()
    raise Exception(f"API call failed: {request.status_code}")

def get_github_stats():
    """Fetches GitHub statistics"""
    query = '''
    query($login: String!) {
        user(login: $login) {
            repositories(first: 100, privacy: PUBLIC) {
                totalCount
                nodes {
                    stargazerCount
                }
            }
            followers {
                totalCount
            }
            contributionsCollection {
                totalCommitContributions
                restrictedContributionsCount
            }
        }
    }
    '''
    data = github_api_query(query, {'login': USER_NAME})['data']['user']
    
    return {
        'repositories': data['repositories']['totalCount'],
        'stars': sum(repo['stargazerCount'] for repo in data['repositories']['nodes']),
        'followers': data['followers']['totalCount'],
        'commits': data['contributionsCollection']['totalCommitContributions'] + 
                  data['contributionsCollection']['restrictedContributionsCount']
    }

def generate_readme(stats, age):
    """Generates README content"""
    return f"""<h1 align="center">Hi 👋, I'm John Paul Curada</h1>

<p align="center">
    <img src="https://readme-typing-svg.herokuapp.com?font=consolas&size=30&duration=4000&color=42047E&center=true&vCenter=true&width=550&height=75&lines=Computer+Science+Student;Software+Developer;Python+|+C+|+Go+Enthusiast">
</p>

## About Me
- 🎓 {age} old
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
        stats = get_github_stats()
        
        # Generate and save README
        readme_content = generate_readme(stats, age)
        with open('README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
            
        print("README.md updated successfully!")
        
    except Exception as e:
        print(f"Error updating README: {str(e)}")
        raise
