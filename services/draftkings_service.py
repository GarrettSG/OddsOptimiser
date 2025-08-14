from typing import List, Optional
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from ..models.schemas import OddsRow

def parse_float(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    try:
        cleaned = text.strip().replace("+", "").replace("−", "-").replace("\u2212", "-")
        return float(cleaned)
    except (ValueError, AttributeError):
        return None

def parse_int(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    try:
        cleaned = text.strip().replace("+", "").replace("−", "-").replace("\u2212", "-")
        return int(cleaned)
    except (ValueError, AttributeError):
        return None

DRAFTKINGS_URLS = {
    "nfl": "https://sportsbook.draftkings.com/leagues/football/nfl",
    "mlb": "https://sportsbook.draftkings.com/leagues/baseball/mlb",
    "nba": "https://sportsbook.draftkings.com/leagues/basketball/nba",
    "ncaaf": "https://sportsbook.draftkings.com/leagues/football/ncaaf",
}

def scrape_draftkings_blocking(league: str) -> List[OddsRow]:
    league = league.lower()
    if league not in DRAFTKINGS_URLS:
        raise ValueError(f"Invalid league: {league}")

    url = DRAFTKINGS_URLS[league]

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url, timeout=45_000)
            page.wait_for_timeout(3500)
            html = page.content()
            context.close()
            browser.close()
    except PlaywrightTimeoutError as e:
        raise RuntimeError(f"Playwright timeout while loading {url}: {e}")
    except Exception as e:
        raise RuntimeError(f"Playwright error while scraping {url}: {e}")

    soup = BeautifulSoup(html, "html.parser")
    data: List[OddsRow] = []

    parlay_cards = soup.select(".parlay-card-10-a")
    for card in parlay_cards:
        rows = card.select("tbody tr")
        for row in rows:
            columns = row.select(".sportsbook-table__column-row")
            if len(columns) < 4:
                continue

            # Team name
            team_name_el = columns[0].select_one(".event-cell__name-text")
            team_name = team_name_el.text.strip() if team_name_el else None

            # Spread
            spread_el = columns[1].select_one(".sportsbook-outcome-cell__line")
            spread = parse_float(spread_el.text.strip() if spread_el and spread_el.text else None)

            # Spread line
            spread_line_el = columns[1].select_one(".sportsbook-outcome-cell__element span")
            spread_line = parse_int(spread_line_el.text.strip() if spread_line_el and spread_line_el.text else None)

            # Moneyline
            money_line_el = columns[3].select_one(".sportsbook-outcome-cell__element span")
            moneyline = parse_int(money_line_el.text.strip() if money_line_el and money_line_el.text else None)

            data.append(
                OddsRow(
                    sportsbook="DraftKings",
                    team_name=team_name,
                    spread=spread,
                    spread_line=spread_line,
                    moneyline=moneyline,
                )
            )

    return data
