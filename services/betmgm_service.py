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
        if game:
            gameTeams = game.select(".participant-wrapper")
            if len(gameTeams) >= 2:
                for i in range(2):
                    participant = gameTeams[i].select_one(".participant")
                    team_dicts[i]["team_name"] = participant.text.strip() if participant and participant.text else None

        bets_wrapper = row.select_one(".grid-six-pack-wrapper")
        if bets_wrapper:
            bets = bets_wrapper.select("ms-option-group")
            if len(bets) >= 3:  # Ensure spread and moneyline exist
                spread_opts = bets[0].select("ms-option") if bets[0] else []
                for i in range(min(2, len(spread_opts))):
                    spread_el = spread_opts[i].select_one(".option-attribute")
                    spread_val = spread_el.text.strip() if spread_el and spread_el.text else None
                    team_dicts[i]["spread"] = parse_float(spread_val)

                    spread_line_el = spread_opts[i].select_one("ms-font-resizer span")
                    spread_line_val = spread_line_el.text.strip() if spread_line_el and spread_line_el.text else None
                    team_dicts[i]["spread_line"] = parse_int(spread_line_val)

                moneyline_opts = bets[2].select("ms-option") if bets[2] else []
                for i in range(min(2, len(moneyline_opts))):
                    ml_el = moneyline_opts[i].select_one("ms-font-resizer")
                    ml_val = ml_el.text.strip() if ml_el and ml_el.text else None
                    team_dicts[i]["moneyline"] = parse_int(ml_val)

        # Append safe results
        for t in team_dicts:
            data.append(OddsRow(**t))

    return data
