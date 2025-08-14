from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers import scrape_controller

app = FastAPI(title="Sportsbook Scraper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scrape_controller.router)
