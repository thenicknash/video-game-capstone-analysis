from bs4 import BeautifulSoup as bs
import os
import requests
import sys, getopt
import pandas as pd

# Data terminology:
# - PAL is a term used to refer to the region of Europe, most of Asia (minus Japan, South Korea, Taiwan and the Philippines), Africa, most of South America, and Australia

CSV_FILE_PATH = '../data/vgchartz_games_webscrape.csv'
DEFAULT_TOTAL_PAGES = 315
RESULTS_PER_PAGE = 200
VGCHARTZ_URL = f'https://www.vgchartz.com/games/games.php?name=&keyword=&console=&region=All&developer=&publisher=&goty_year=&genre=&boxart=Both&banner=Both&ownership=Both&showmultiplat=No&results={RESULTS_PER_PAGE}&order=Sales&showtotalsales=0&showtotalsales=1&showpublisher=0&showpublisher=1&showvgchartzscore=0&showvgchartzscore=1&shownasales=0&shownasales=1&showdeveloper=0&showdeveloper=1&showcriticscore=0&showcriticscore=1&showpalsales=0&showpalsales=1&showreleasedate=0&showreleasedate=1&showuserscore=0&showuserscore=1&showjapansales=0&showjapansales=1&showlastupdate=0&showlastupdate=1&showothersales=0&showothersales=1&showshipped=0&showshipped=1'


def validate_command_line_arguments():
    ''' Handles the command line arguments.

        - First argument: debug
            - Shows the game data as it is being scraped
        - Second argument: platform
            - The platform to scrape game data from
        - Third argument: page_limit
            - The number of pages to scrape in one iteration
    '''
    args = sys.argv[1:]
    long_options = ['debug', 'platform=', 'page_limit=']

    options, values = getopt.getopt(args, '', long_options)

    debug = False
    platform = None
    page_limit = None

    for option, value in options:
        print(f'Option: {option}, Value: {value}')
        if option == '--platform': platform = value
        if option == '--page_limit': page_limit = value
        if option == '--debug': debug = True

    if debug == True: print('> Debug mode enabled')

    return debug, platform, page_limit

def retrieve_game_search_data_table(page_url, page_number):
    ''' Retrieves the page data from the page url. '''
    specific_page_url = f'{page_url}&page={page_number}'
    response = requests.get(specific_page_url)
    content = response.content
    soup = bs(content, 'html.parser')

    game_table = soup.find('div', id='generalBody').findChildren('table')[0]

    return game_table

def convert_game_soup_to_list(game_rows):
    ''' Converts the game rows into a list of dictionaries. '''
    data = []

    for index, row in enumerate(game_rows):
        # This is necessary in order to skip some consistent bad data rows
        if index in [0, 1, 2, 3]: continue

        game_row_dict = {
            'rank': row.findChildren('td')[0].text,
            'game': row.findChildren('td')[2].findChildren('a')[0].text,
            'platform': row.findChildren('td')[3].findChildren('img')[0]['alt'],
            'publisher': row.findChildren('td')[4].text,
            'developer': row.findChildren('td')[5].text,
            'vgchartz_score': row.findChildren('td')[6].text,
            'critic_score': row.findChildren('td')[7].text,
            'user_score': row.findChildren('td')[8].text,
            'total_shipped': row.findChildren('td')[9].text,
            'total_sales': row.findChildren('td')[10].text,
            'north_america_sales': row.findChildren('td')[11].text,
            'pal_sales': row.findChildren('td')[12].text, 
            'japan_sales': row.findChildren('td')[13].text,
            'other_sales': row.findChildren('td')[14].text,
            'release_date': row.findChildren('td')[15].text,
            'last_update_date': row.findChildren('td')[16].text
        }

        data.append(game_row_dict)

    if debug == True: print(f'> {RESULTS_PER_PAGE} games have been scraped...')

    return data

def write_game_data_to_csv(game_data, file_exists):
    ''' Writes the game data (list of dictionaries) to a csv file. '''
    if file_exists:
        df = pd.read_csv(CSV_FILE_PATH)
        combined_df = pd.concat([df, pd.DataFrame(game_data)])
        # df = pd.concat(game_data)
        combined_df.to_csv(CSV_FILE_PATH, index=False)
    else:
        df = pd.DataFrame(game_data)
        df.to_csv(CSV_FILE_PATH, index=False)

def check_previous_scraped_data():
    ''' Checks if we have already scraped the data into a file previously. '''
    file_exists = False
    page_counter = 0

    # Check if the CSV file exists
    # If it doesn't, start scraping from page 1
    # If it does, check how many pages we have scraped

    if os.path.isfile(CSV_FILE_PATH) == False:
        if debug == True: print(f'> No previous scraped data found. Starting from page 1...')
    elif os.path.isfile(CSV_FILE_PATH) == True:
        if debug == True: print(f'> Previous scraped data found. Continuing from last page scraped...')

        file_exists = True

        try:
            df = pd.read_csv(CSV_FILE_PATH)
        except pd.errors.EmptyDataError:
            print('> Previous scraped data found but it is empty. Starting from page 1...')
            return file_exists, page_counter

        page_counter = df.shape[0] // RESULTS_PER_PAGE

    return file_exists, page_counter

if __name__ == '__main__':
    # TODO: Add command line argument validation
    debug, platform, page_limit = validate_command_line_arguments()

    n_pages_to_scrape = DEFAULT_TOTAL_PAGES
    if page_limit != None:
        n_pages_to_scrape = int(page_limit)

    if debug == True: print(f'> Beginning to scrape game data from VGChartz. Will scrape {n_pages_to_scrape} pages...')

    # Determine if we have already scraped the data and if so, how many pages we have scraped
    file_exists, pages_scraped = check_previous_scraped_data()

    page_counter = pages_scraped

    vgchartz_games_array = []
    while True:
        if page_counter >= n_pages_to_scrape + pages_scraped:
            break

        if page_counter > DEFAULT_TOTAL_PAGES:
            break

        page_counter += 1

        if debug == True: print(f'> Scraping game data from page {page_counter}...')
        vgchartz_games_soup = retrieve_game_search_data_table(VGCHARTZ_URL, page_counter)
    
        if debug == True: print(f'> Converting the scraped game data into a list of dictionaries...')
        page_game_data = convert_game_soup_to_list(vgchartz_games_soup)

        if debug == True: print(f'> Appending the game list data...')
        vgchartz_games_array.extend(page_game_data)

    if debug == True: print(f'> Writing scraped game data to \'..\\data\\vgchartz_games_webscrape.csv\'...')
    write_game_data_to_csv(vgchartz_games_array, file_exists)

    if debug == True: print(f'> Webscraping complete!')
