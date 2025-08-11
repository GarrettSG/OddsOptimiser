import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


# takes html input of string and saves it is a file pth
def save_html(html, path):
    with open(path, 'w') as f:
        f.write(html)


# opens the path file
def open_html(path):
    with open(path, 'r') as f:
        return f.read()


# Opens the given sport books websites and obtains html. Stores html in txt files in webpages folder
# returns nothing
def get_pages():
    print("What sport do you want to bet on?\n" +
          "1. NFL\n" +
          "2. MLB\n" +
          "3. NBA\n" +
          "4. NCAA Football")
    user_choice = int(input("Type your choice here: "))

    driver = webdriver.Chrome()

    # Open FanDuel website and retrieve html
    if (user_choice == 1):
        fanduel_url = 'https://sportsbook.fanduel.com/navigation/nfl'
    elif (user_choice == 2):
        fanduel_url = 'https://sportsbook.fanduel.com/navigation/mlb'
    elif (user_choice == 3):
        fanduel_url = 'https://sportsbook.fanduel.com/navigation/nba'
    elif (user_choice == 4):
        fanduel_url = 'https://sportsbook.fanduel.com/navigation/ncaaf'

    driver.get(fanduel_url)
    time.sleep(2)
    page_source = driver.page_source

    # save html from FanDuel page into fanduel_page.txt
    save_html(page_source, './webpages/fanduel_page.txt')

    # Open DraftKings website and retrieve html
    if (user_choice == 1):
        draftkings_url = 'https://sportsbook.draftkings.com/leagues/football/nfl'
    elif (user_choice == 2):
        draftkings_url = 'https://sportsbook.draftkings.com/leagues/baseball/mlb'
    elif (user_choice == 3):
        draftkings_url = 'https://sportsbook.draftkings.com/leagues/basketball/nba'
    elif (user_choice == 4):
        draftkings_url = 'https://sportsbook.draftkings.com/leagues/football/ncaaf'
    driver.get(draftkings_url)
    time.sleep(4)
    page_source = driver.page_source

    # save html from DraftKings page into draftkings_page.txt
    save_html(page_source, './webpages/draftkings_page.txt')

    # Open BetMGM website and retrieve html
    if (user_choice == 1):
        betMGM_url = 'https://sports.az.betmgm.com/en/sports/football-11/betting/usa-9/nfl-35'
    elif (user_choice == 2):
        betMGM_url = 'https://sports.az.betmgm.com/en/sports/baseball-23/betting/usa-9/mlb-75'
    elif (user_choice == 3):
        betMGM_url = 'https://sports.az.betmgm.com/en/sports/basketball-7/betting/usa-9/nba-6004'
    elif (user_choice == 4):
        betMGM_url = 'https://sports.az.betmgm.com/en/sports/football-11/betting/usa-9/college-football-211'
    driver.get(betMGM_url)
    time.sleep(4)
    page_source = driver.page_source

    # save html from BetMGM page into betmgm_page.txt
    save_html(page_source, './webpages/betmgm_page.txt')

    # ESPN Sportbook
    ESPN_url = 'https://www.espn.com/mlb/odds'

    driver.get(betMGM_url)
    time.sleep(4)
    page_source = driver.page_source

    # save html from BetMGM page into betmgm_page.txt
    save_html(page_source, './webpages/ESPN_page.txt')

    # close Chrome webdriver
    driver.quit()

    return


# Uses html from './webpages/draftkings_page.txt'
# Returns a list of dictionaries for each team on site containing { team_name , spread , spread_line , money_line }
def get_Draft_Kings():
    # create an empty return list
    data = []

    # creates parser for DraftKing html
    soup = BeautifulSoup(open_html('./webpages/draftkings_page.txt'), 'html.parser')

    # each player card contains the games for a day
    parlayCards = soup.select('.parlay-card-10-a')

    for parlayCard in parlayCards:

        # rows is a list containing the individual game html
        rows = parlayCard.select('tbody tr')

        for row in rows:

            d = dict()

            d['sportbook'] = "DraftKings"

            columns = row.select('.sportsbook-table__column-row')
            name_column = columns[0]  # contains html for team name
            spread_column = columns[1]  # contains html for spread and spread line
            total_column = columns[2]  # contains html for over under
            money_line_column = columns[3]  # contains html for moneyline

            # obtains the team_name value and stores it in the dictionary
            team_name = name_column.select_one('.event-cell__name-text').text.strip()
            team_name = team_name.split()
            d['team_name'] = team_name[-1]

            # obtains spread value and stores it in 'spread'. if no spread is offered 'spread' = None
            spread = spread_column.select_one('.sportsbook-outcome-cell__line')
            if (spread != None):
                spread = spread.text.strip()
                spread = spread.replace('+', '')
                d['spread'] = float(spread.replace('−', '-'))
            else:
                d['spread'] = None

            # obtains the spread line value and stores it in 'spread_line' as an int. if no spread is offered spread_line = None
            spread_line = spread_column.select_one('.sportsbook-outcome-cell__element span')
            if (spread_line != None):
                spread_line = spread_line.text.strip()
                spread_line = spread_line.replace('+', '')
                d['spread_line'] = int(spread_line.replace('−', '-'))
            else:
                d['spread_line'] = None

            # obtains the moneyline value and stores it in 'moneyline' as an int. if not moneyline is offereed moenyline = None
            money_line = money_line_column.select_one('.sportsbook-outcome-cell__element span')
            if (money_line != None):
                money_line = money_line.text.strip()
                money_line = money_line.replace('+', '')
                d['moneyline'] = int(money_line.replace('−', '-'))
            else:
                d['moneyline'] = None

            # Adds teams dictionary to the list data
            data.append(d)

    # returns the list of dictionaries
    return data


def get_FanDuel():
    data = []

    soup = BeautifulSoup(open_html('./webpages/fanduel_page.txt'), 'html.parser')

    table = soup.select_one('main')
    table = table.select('ul')

    rows = table[2].select('li')

    test1 = rows[3].select('span')

    print(test1[0].text.strip())

    '''
    game1 = rows[4].select_one('div')
    game1 = game1.select_one('div')
    game1 = game1.select_one('div')

    print(game1)

    test = game1.select('div', class_='v.w.xy.bu.cd.t.h')
    print()
    print(test)

    name_column = game1.select_one('a')
    test = name_column.select('span')

    print(test[0].text.strip())
    print(test[1].text.strip())
    '''

    # print(team_name)

    for x in range(2, len(rows) - 1):
        team_1 = dict()
        team_2 = dict()

        data.append(team_1)
        data.append(team_2)

    return data


# Uses html from './webpages/betmgm.txt'
# Returns a list of dictionaries for each team on site containing { team_name , spread , spread_line , money_line }
def get_BetMGM():
    # Opens the webpage text file and uses Beautiful soup to parse file
    soup = BeautifulSoup(open_html('./webpages/betmgm_page.txt'), 'html.parser')

    # the table of games is kept in grid
    grid = soup.select('ms-six-pack-event')

    data = []

    # Since rows are stored in games rather than teams, each transversal stores information for 2 teams
    for row in grid:

        # team_1 and team_2 are dictionaires that will be added to data to be returned in a list
        team_1 = dict()
        team_2 = dict()

        team_1['sportbook'] = "BetMGM"
        team_2['sportbook'] = "BetMGM"

        # Retrieves names of team playing in game and adds it to dictionary
        game = row.select_one('.participants-pair-game')
        gameTeams = game.select('.participant-wrapper')
        team_1['team_name'] = gameTeams[0].select_one('.participant').text.strip()
        team_2['team_name'] = gameTeams[1].select_one('.participant').text.strip()

        bets = row.select_one('.grid-six-pack-wrapper')
        bets = bets.select('ms-option-group')

        # Each list is a column of the betting lines for the game
        spread = bets[0]  # first column of lines for spread
        over_under = bets[1]  # column for O/U
        moneyline = bets[2]  # column for moneyline

        # Retrieves sprea value and stores it in dictionaries as a float value for team_1 and team_2
        spread = spread.select('ms-option')
        team_1_spread = spread[0].select_one('.option-attribute').text.strip()
        if (team_1_spread != None):
            team_1_spread = team_1_spread.replace('+', '')
            team_1['spread'] = float(team_1_spread.replace('−', '-'))
        else:
            team_1['spread'] = None

        team_2_spread = spread[1].select_one('.option-attribute').text.strip()
        if (team_2_spread != None):
            team_2_spread = team_2_spread.replace('+', '')
            team_2['spread'] = float(team_2_spread.replace('−', '-'))
        else:
            team_2['spread'] = None

        # Retrieves spread line value and stores it in dictionaries as a int value for team_1 and team_2
        team_1_spread_line = spread[0].select_one('ms-font-resizer span').text.strip()
        if (team_1_spread_line != 0):
            team_1_spread_line = team_1_spread_line.replace('+', '')
            team_1['spread_line'] = int(team_1_spread_line.replace('−', '-'))
        else:
            team_1['spread_line'] = None

        team_2_spread_line = spread[1].select_one('ms-font-resizer span').text.strip()
        if (team_2_spread_line != 0):
            team_2_spread_line = team_2_spread_line.replace('+', '')
            team_2['spread_line'] = int(team_2_spread_line.replace('−', '-'))
        else:
            team_2['spread_line'] = None

        # Retrieves moneyline value and stores it in dictionaries as a int value for team_1 and team_2
        moneyline_column = moneyline.select('ms-option')
        team_1_moneyline = moneyline_column[0].select_one('ms-font-resizer').text.strip()
        if (team_1_moneyline != None):
            team_1_moneyline = team_1_moneyline.replace('+', '')
            team_1['moneyline'] = int(team_1_moneyline.replace('−', '-'))
        else:
            team_1['moneyline'] = None

        team_2_moneyline = moneyline_column[1].select_one('ms-font-resizer').text.strip()
        if (team_2_moneyline != None):
            team_2_moneyline = team_2_moneyline.replace('+', '')
            team_2['moneyline'] = int(team_2_moneyline.replace('−', '-'))
        else:
            team_2['moneyline'] = None

        # print(team_1)
        # print(team_2)

        # adds each of the teams to the data list
        data.append(team_1)
        data.append(team_2)

    # returns the list containing all the team dictionaries
    return data


def Print_Lines(Sportbooks):
    for sportbook in Sportbooks:
        for teams in sportbook:
            print(teams)
        print()
    return


def Print_Lines_By_Team(Sportbooks, team_name):
    for sportbook in Sportbooks:
        for game in sportbook:
            if game['team_name'] == team_name:
                print(game)
                break
    print()


def Print_Best_Line_Moneyline_By_Team(Sportbooks, team_name):
    best_bet = None
    best_line = -999999
    for sportbook in Sportbooks:
        for game in sportbook:
            if (game['team_name'] == team_name):
                if (game['moneyline'] > best_line):
                    best_bet = game
                    best_line = game['moneyline']
                    break

    print(best_bet)
    print()


# Print_Lines(Sportbooks)
# Print_Lines_By_Team(Sportbooks, 'Chiefs')
# Print_Best_Line_Moneyline_By_Team(Sportbooks, 'Chiefs')

print("\nWelcome to Garrett's Sportbetting Program!!\n")
while (quit != 'q'):
    get_pages()
    print()

    BetMGM_lines = get_BetMGM()

    # FanDuel_lines = get_FanDuel()

    Draft_Kings_lines = get_Draft_Kings()

    Sportbooks = [BetMGM_lines, Draft_Kings_lines]

    Print_Lines(Sportbooks)

    print()

    Print_Best_Line_Moneyline_By_Team(Sportbooks, 'Diamondbacks')

    quit = input("Enter 'q' to quit: ")
    print()