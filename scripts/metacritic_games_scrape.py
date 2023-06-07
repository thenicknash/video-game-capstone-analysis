from bs4 import BeautifulSoup as bs
import requests
import sys, getopt
import pandas as pd

VGCHARTZ_URL = 'https://www.vgchartz.com/games/games.php?name=&keyword=&console=&region=All&developer=&publisher=&goty_year=&genre=&boxart=Both&banner=Both&ownership=Both&showmultiplat=No&results=50&order=Sales&showtotalsales=0&showtotalsales=1&showpublisher=0&showpublisher=1&showvgchartzscore=0&showvgchartzscore=1&shownasales=0&shownasales=1&showdeveloper=0&showdeveloper=1&showcriticscore=0&showcriticscore=1&showpalsales=0&showpalsales=1&showreleasedate=0&showreleasedate=1&showuserscore=0&showuserscore=1&showjapansales=0&showjapansales=1&showlastupdate=0&showlastupdate=1&showothersales=0&showothersales=1&showshipped=0&showshipped=1'

def validate_command_line_arguments():
    ''' Handles the command line arguments.

        - First argument: debug or not
            - Shows the game data as it is being scraped
        - Second argument: platform
            - The platform to scrape game data from
        - Third argument: limit
            - The number of games to scrape in one iteration
    '''
    args = sys.argv[1:]
    # short_options = 'd'
    long_options = ['debug', 'platform=', 'limit=']

    options, values = getopt.getopt(args, '', long_options)

    platform = None
    limit = None
    debug = False

    for option, value in options:
        print(f'Option: {option}, Value: {value}')
        if option == '--platform': platform = value
        if option == '--limit': limit = value
        if option == '--debug': debug = True

    if debug == True: print('\n> Debug mode enabled')

def get_game_data(game_url):
    ''' Retrieves the game data from the game url. '''
    
def retrieve_game_search_data_table(page_url):
    ''' Retrieves the page data from the page url. '''
    response = requests.get(page_url)
    content = response.content
    soup = bs(content, 'html.parser')

    # Get table
    table = soup.find('div', id='generalBody').findChildren('table')[0]

    rows = table.findChildren('tr')

    return table

def convert_soup_to_pandas(game_rows):
    ''' Converts the game rows into a pandas dataframe. '''
    data = []

    for index, row in enumerate(game_rows):
        if index in [0, 1, 2, 3]: continue

        print(row)

        game_row_dict = {
            'rank': row.findChildren('td')[0].text,
        }

        print(game_row_dict)

        break

if __name__ == '__main__':
    debug = False
    platform = None
    limit = None

    validate_command_line_arguments()

    # Getting the gaming platform's data
    vgchartz_games_soup = retrieve_game_search_data_table(VGCHARTZ_URL)
    
    # print(vgchartz_games_soup)

    # Converting the data into a pandas dataframe
    vgchartz_games_df = convert_soup_to_pandas(vgchartz_games_soup)