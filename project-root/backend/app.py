from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from config import settings
import data_analysis

logger = logging.getLogger("Stocktimum")
logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def error_payload(message, details=None):
    return {"error": {"message": message, "details": details}}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_payload(str(exc.detail)),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content=error_payload("Internal Server Error"),
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        duration_ms = (time.perf_counter() - start_time) * 1000
        status_code = response.status_code if response else 500
        logger.info(
            "%s %s - %s in %.2fms",
            request.method,
            request.url.path,
            status_code,
            duration_ms,
        )


@app.get("/")
async def home():
    return {
        "message": "Stocktimum API",
        "docs": "/docs",
    }


@app.get("/api/data")
async def api_data(
    ticker: str = "AAPL",
    closing_price: bool = True,
    period: str = "10y",
    interval: str = "1d",
    force: bool = False,
):
    return data_analysis.fetch_data(ticker, period, interval, force=force)


@app.get("/api/hello")
async def api_hello():
    return {
        "message": "Hello from Stocktimum",
        "cache_ttl_seconds": settings.cache_ttl_seconds,
        "data_dir": settings.data_dir,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
