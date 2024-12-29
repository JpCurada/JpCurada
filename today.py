import datetime
from dateutil import relativedelta
import requests
import os
from xml.dom import minidom

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
                    languages(first: 10) {
                        nodes {
                            name
                        }
                    }
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

def update_svg(filename, stats, age):
    """Updates SVG file with current stats"""
    svg = minidom.parse(filename)
    tspans = svg.getElementsByTagName('tspan')
    
    # Update values in SVG
    # Note: These indices need to match your SVG file structure
    stats_map = {
        'age': age,
        'repos': str(stats['repositories']),
        'stars': str(stats['stars']),
        'commits': str(stats['commits']),
        'followers': str(stats['followers'])
    }
    
    # Update each tspan element
    for tspan in tspans:
        key = tspan.getAttribute('id')
        if key in stats_map:
            tspan.firstChild.data = stats_map[key]
    
    # Save updated SVG
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(svg.toxml())

if __name__ == '__main__':
    try:
        print("Fetching GitHub stats...")
        
        # Calculate age
        birth_date = datetime.datetime(2004, 10, 2)
        age = daily_readme(birth_date)
        
        # Fetch GitHub stats
        stats = get_github_stats()
        
        # Update SVGs
        update_svg('dark_mode.svg', stats, age)
        update_svg('light_mode.svg', stats, age)
        
        print("SVGs updated successfully!")
        
    except Exception as e:
        print(f"Error updating SVGs: {str(e)}")
        raise
