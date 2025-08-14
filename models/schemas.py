from typing import List, Optional
from pydantic import BaseModel

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
