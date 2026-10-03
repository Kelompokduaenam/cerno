from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.analysis.api import router as analysis_router
from app.analysis.history_api import router as history_router
from app.auth.api import router as auth_router
from app.db import SessionLocal
from app.config import settings


def error_response(status: int, title: str, detail: str, instance: str | None = None) -> JSONResponse:
    body = {"type": "about:blank", "title": title, "status": status, "detail": detail}
    if instance:
        body["instance"] = instance
    return JSONResponse(body, status_code=status, media_type="application/problem+json")


app = FastAPI(title="CERNO API", version="0.1.0", description="API penilaian risiko CERNO. Skor tahap awal berasal dari aturan yang dapat dijelaskan.")
if not settings.production:
    app.add_middleware(CORSMiddleware, allow_origins=[settings.allowed_origin], allow_credentials=True, allow_methods=["GET", "POST", "DELETE"], allow_headers=["Content-Type", "X-Access-Token", "X-CSRF-Token", "X-Reporter-Token"])


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        title = exc.detail.get("title", "Permintaan gagal")
        detail = exc.detail.get("detail", title)
    else:
        title = "Permintaan gagal"
        detail = str(exc.detail)
    return error_response(exc.status_code, title, detail, request.url.path)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return error_response(422, "Input tidak valid", "Periksa tipe dan nilai field yang dikirim.", request.url.path)


@app.middleware("http")
async def protection_middleware(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/healthz", include_in_schema=False)
def healthz() -> dict:
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception:
        return JSONResponse({"status": "unavailable"}, status_code=503)


app.include_router(auth_router)
app.include_router(analysis_router)
app.include_router(history_router)

from app.ocr.api import router as ocr_router
from app.community.api import router as community_router

app.include_router(ocr_router)
app.include_router(community_router)
