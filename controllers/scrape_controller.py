from fastapi import APIRouter, HTTPException
import asyncio
from ..models.schemas import SportChoice, ScrapeResponse
from ..services.draftkings_service import scrape_draftkings_blocking
from ..services.betmgm_service import scrape_betmgm_blocking

router = APIRouter()

@router.post("/scrape-draftkings", response_model=ScrapeResponse)
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

@router.post("/scrape-betmgm", response_model=ScrapeResponse)
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
