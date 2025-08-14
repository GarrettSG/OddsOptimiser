from typing import List, Optional
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from ..models.schemas import OddsRow
from .draftkings_service import parse_float, parse_int  # reuse helpers

BETMGM_URLS = {
    "nfl": "https://sports.co.betmgm.com/en/sports/football-11/betting/usa-9/nfl-35",
    "mlb": "https://sports.co.betmgm.com/en/sports/baseball-23/betting/usa-9/mlb-75",
    "nba": "https://sports.co.betmgm.com/en/sports/basketball-7/betting/usa-9/nba-6004",
    "ncaaf": "https://sports.co.betmgm.com/en/sports/football-11/betting/usa-9/college-football-211",
}

def scrape_betmgm_blocking(league: str) -> List[OddsRow]:
    league = league.lower()
    if league not in BETMGM_URLS:
        raise ValueError(f"Invalid league: {league}")

    url = BETMGM_URLS[league]

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url, timeout=45_000)
            page.wait_for_selector("ms-six-pack-event", timeout=10_000)
            page.wait_for_timeout(1000)
            html = page.content()
            context.close()
            browser.close()
    except PlaywrightTimeoutError as e:
        raise RuntimeError(f"Playwright timeout while loading {url}: {e}")
    except Exception as e:
        raise RuntimeError(f"Playwright error while scraping {url}: {e}")

    soup = BeautifulSoup(html, "html.parser")
    grid = soup.select("ms-six-pack-event")
    data: List[OddsRow] = []

    for row in grid:
        team_dicts = [{"sportsbook": "BetMGM"}, {"sportsbook": "BetMGM"}]

        game = row.select_one(".participants-pair-game")
        gameTeams = game.select(".participant-wrapper")
        team_dicts[0]["team_name"] = gameTeams[0].select_one(".participant").text.strip()
        team_dicts[1]["team_name"] = gameTeams[1].select_one(".participant").text.strip()

        bets = row.select_one(".grid-six-pack-wrapper").select("ms-option-group")
        spread = bets[0]
        moneyline = bets[2]

        spread_opts = spread.select("ms-option")
        for i in range(2):
            spread_val = spread_opts[i].select_one(".option-attribute").text.strip()
            team_dicts[i]["spread"] = parse_float(spread_val)
            spread_line_val = spread_opts[i].select_one("ms-font-resizer span").text.strip()
            team_dicts[i]["spread_line"] = parse_int(spread_line_val)

        moneyline_opts = moneyline.select("ms-option")
        for i in range(2):
            ml_val = moneyline_opts[i].select_one("ms-font-resizer").text.strip()
            team_dicts[i]["moneyline"] = parse_int(ml_val)

        for t in team_dicts:
            data.append(OddsRow(**t))

    return data
