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

url = 'https://play.ballybet.com/sports#sports-hub/baseball/mlb'

driver = webdriver.Chrome()
driver.get(url)
time.sleep(8)
page_source = driver.page_source


# save html from FanDuel page into fanduel_page.txt
save_html(page_source, 'ballybet.txt')

from bs4 import BeautifulSoup

html = open_html('ballybet.txt')
soup = BeautifulSoup(html, "html.parser")

events = soup.find_all("li", class_="KambiBC-sandwich-filter__event-list-item")

from bs4 import BeautifulSoup

html = open_html('ballybet.txt')
soup = BeautifulSoup(html, "html.parser")

events = soup.find_all("li", class_="KambiBC-sandwich-filter__event-list-item")

data = []

for event in events:
    # Extract team names
    team_divs = event.find_all("div", class_="KambiBC-event-participants__name-participant-name")
    teams = [t.get_text(strip=True).replace("@ ", "") for t in team_divs]

    if len(teams) != 2:
        continue  # skip malformed events

    team_away = {'team_name': teams[0], 'sportbook': 'bally'}
    team_home = {'team_name': teams[1], 'sportbook': 'bally'}

    # --- Moneyline ---
    moneyline_section = event.find("div", class_="KambiBC-bet-offer--onecrosstwo")
    moneyline_buttons = moneyline_section.find_all("button") if moneyline_section else []

    if len(moneyline_buttons) == 2:
        for btn, team in zip(moneyline_buttons, [team_away, team_home]):
            aria_label = btn.get("aria-label", "")
            # Extract moneyline odds from aria-label
            if " at " in aria_label:
                odds = aria_label.split(" at ")[-1].strip()
                # Store as int if possible, else string
                try:
                    team['moneyline'] = int(odds.replace('+', '').replace('−', '-'))
                except ValueError:
                    team['moneyline'] = odds
            else:
                team['moneyline'] = None
    else:
        team_away['moneyline'] = None
        team_home['moneyline'] = None

    # --- Spread (Run line) ---
    spread_section = event.find("div", class_="KambiBC-bet-offer--handicap")
    spread_buttons = spread_section.find_all("button") if spread_section else []

    # Initialize
    team_away['spread'] = None
    team_away['spread_line'] = None
    team_home['spread'] = None
    team_home['spread_line'] = None

    for btn in spread_buttons:
        label = btn.get("aria-label", "")

        if "Run Line" in label:
            parts = label.split(" - ")
            # parts example: ['Bet on PHI Phillies @ CIN Reds', 'Run Line', 'PHI Phillies +1.5 at -195']
            if len(parts) >= 3:
                team_and_spread = parts[2]  # e.g. 'PHI Phillies +1.5 at -195'

                # Split from right on ' at ' to separate odds
                if " at " in team_and_spread:
                    team_spread_part, odds_str = team_and_spread.rsplit(" at ", 1)
                    odds_str = odds_str.strip()

                    # Now split team_spread_part by spaces, last token should be spread, rest is team name
                    tokens = team_spread_part.split()
                    spread_val = tokens[-1]  # '+1.5' or '-1.5'
                    team_name = " ".join(tokens[:-1])  # 'PHI Phillies'

                    print(f"Team: {team_name}, Spread: {spread_val}, Odds: {odds_str}")

                    # Now you can assign these to the right team's dict
                    # Example logic:
                    if team_name == team_away['team_name']:
                        team_away['spread'] = float(spread_val.replace('+', '').replace('−', '-'))
                        team_away['spread_line'] = int(odds_str.replace('+', '').replace('−', '-'))
                    elif team_name == team_home['team_name']:
                        team_home['spread'] = float(spread_val.replace('+', '').replace('−', '-'))
                        team_home['spread_line'] = int(odds_str.replace('+', '').replace('−', '-'))

    data.append(team_away)
    data.append(team_home)

# Now data contains one dict per team, matching your BetMGM style
for team_data in data:
    print(team_data)