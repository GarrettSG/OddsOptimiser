# main.py
from typing import List, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import asyncio

# -------------------------
# Pydantic models
# -------------------------
class SportChoice(BaseModel):
    league: str  # "nfl", "mlb", "nba", "ncaaf"

class OddsRow(BaseModel):
    sportsbook: str
    team_name: Optional[str]
    spread: Optional[float]
    spread_line: Optional[int]
    moneyline: Optional[int]

class ScrapeResponse(BaseModel):
    results: List[OddsRow]

# -------------------------
# FastAPI app + CORS (frontend friendly)
# -------------------------
app = FastAPI(title="DraftKings Scraper API (Playwright + FastAPI)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Helpers: safe parsers
# -------------------------
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

# -------------------------
# DraftKings URLs
# -------------------------
DRAFTKINGS_URLS = {
    "nfl": "https://sportsbook.draftkings.com/leagues/football/nfl",
    "mlb": "https://sportsbook.draftkings.com/leagues/baseball/mlb",
    "nba": "https://sportsbook.draftkings.com/leagues/basketball/nba",
    "ncaaf": "https://sportsbook.draftkings.com/leagues/football/ncaaf",
}

# -------------------------
# Scraper (blocking) using Playwright (sync) — now takes 'league' instead of sport_id
# -------------------------
def scrape_draftkings_blocking(league: str) -> List[OddsRow]:
    league = league.lower()
    if league not in DRAFTKINGS_URLS:
        raise ValueError(f"Invalid league: {league}")

    url = DRAFTKINGS_URLS[league]
    html = None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
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

            team_name_el = columns[0].select_one(".event-cell__name-text")
            team_name = team_name_el.text.strip() if team_name_el else None

            spread_el = columns[1].select_one(".sportsbook-outcome-cell__line")
            spread = parse_float(spread_el.text if spread_el else None)

            spread_line_el = columns[1].select_one(".sportsbook-outcome-cell__element span")
            spread_line = parse_int(spread_line_el.text if spread_line_el else None)

            money_line_el = columns[3].select_one(".sportsbook-outcome-cell__element span")
            moneyline = parse_int(money_line_el.text if money_line_el else None)

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

# -------------------------
# BetMGM URLS
# -------------------------
BETMGM_URLS = {
    "nfl": "https://sports.co.betmgm.com/en/sports/football-11/betting/usa-9/nfl-35",
    "mlb": "https://sports.co.betmgm.com/en/sports/baseball-23/betting/usa-9/mlb-75",
    "nba": "https://sports.co.betmgm.com/en/sports/basketball-7/betting/usa-9/nba-6004",
    "ncaaf": "https://sports.co.betmgm.com/en/sports/football-11/betting/usa-9/college-football-211",
}

# -------------------------
# BetMGM scraper
# -------------------------
def scrape_betmgm_blocking(league: str) -> List[OddsRow]:
    league = league.lower()
    if league not in BETMGM_URLS:
        raise ValueError(f"Invalid league: {league}")

    url = BETMGM_URLS[league]
    html = None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()
            page.goto(url, timeout=45_000)
            page.wait_for_selector("ms-six-pack-event", timeout=10_000)
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

        # Team names
        game = row.select_one(".participants-pair-game")
        gameTeams = game.select(".participant-wrapper")
        team_dicts[0]["team_name"] = gameTeams[0].select_one(".participant").text.strip()
        team_dicts[1]["team_name"] = gameTeams[1].select_one(".participant").text.strip()

        bets = row.select_one(".grid-six-pack-wrapper").select("ms-option-group")
        spread = bets[0]
        moneyline = bets[2]

        # Spreads + Spread Lines
        spread_opts = spread.select("ms-option")
        for i in range(2):
            spread_val = spread_opts[i].select_one(".option-attribute").text.strip()
            team_dicts[i]["spread"] = parse_float(spread_val)
            spread_line_val = spread_opts[i].select_one("ms-font-resizer span").text.strip()
            team_dicts[i]["spread_line"] = parse_int(spread_line_val)

        # Moneylines
        moneyline_opts = moneyline.select("ms-option")
        for i in range(2):
            ml_val = moneyline_opts[i].select_one("ms-font-resizer").text.strip()
            team_dicts[i]["moneyline"] = parse_int(ml_val)

        # Add both teams to final list
        for t in team_dicts:
            data.append(OddsRow(**t))

    return data

# -------------------------
# Async endpoint: run blocking scraper off the loop
# -------------------------
@app.post("/scrape-draftkings", response_model=ScrapeResponse)
async def scrape_draftkings_api(choice: SportChoice):
    try:
        results = await asyncio.to_thread(scrape_draftkings_blocking, choice.league)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    return ScrapeResponse(results=results)

@app.post("/scrape-betmgm", response_model=ScrapeResponse)
async def scrape_betmgm_api(choice: SportChoice):
    try:
        results = await asyncio.to_thread(scrape_betmgm_blocking, choice.league)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")
    return ScrapeResponse(results=results)