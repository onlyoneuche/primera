"""Single-process API and self-hosted frontend; no request logging or persistence."""
from contextlib import asynccontextmanager
from html import escape
import hashlib
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from ml.config import ROOT
from app.messages import COPY, FACULTY_CONFIG, SUPPORT
from app.predict import Predictor
from app.schemas import CheckIn, Result

# Public build fingerprint: no cookies, user identifiers, or submitted values.
_public_files = sorted((ROOT / "app/static").rglob("*"))
_public_files += [ROOT / "config" / name for name in
                  ["copy.json", "faculty_groups.json", "support_contacts.json"]]
ASSET_VERSION = hashlib.sha256(b"".join(path.read_bytes() for path in _public_files
                                      if path.is_file())).hexdigest()[:16]

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; "
        "font-src 'self'; img-src 'self'; connect-src 'self'; base-uri 'none'; "
        "form-action 'self'; frame-ancestors 'none'; object-src 'none'",
}


@asynccontextmanager
async def lifespan(application):
    application.state.predictor = Predictor()
    yield
    del application.state.predictor


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)


@app.middleware("http")
async def private_responses(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception:
        # Do not log exceptions: they may contain parsed inputs or feature values.
        response = JSONResponse({"detail": COPY["errors"]["server"]}, status_code=500)
    response.headers.update(SECURITY_HEADERS)
    if request.url.path.rstrip("/") == "/predict":
        response.headers["Cache-Control"] = "no-store"
    elif request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache"
    return response


@app.exception_handler(RequestValidationError)
async def invalid_answers(request, exc):
    fields = {question["key"]: question["error"] for question in COPY["questions"]}
    errors = []
    for error in exc.errors():
        location = error.get("loc", ())
        field = location[1] if len(location) > 1 and location[1] in fields else None
        message = fields[field] if field else COPY["errors"]["unknown"] if error["type"] == "extra_forbidden" else COPY["errors"]["request"]
        item = {"field": field, "message": message}
        if item not in errors:
            errors.append(item)
    return JSONResponse({"detail": errors}, status_code=422)


@app.exception_handler(HTTPException)
async def http_error(request, exc):
    return JSONResponse({"detail": COPY["errors"]["request"]}, status_code=exc.status_code)


@app.get("/health")
def health(request: Request):
    return {"status": "ok", "model_loaded": hasattr(request.app.state, "predictor")}


@app.get("/api/config")
def config():
    return JSONResponse({"copy": COPY, "faculty_groups": FACULTY_CONFIG, "support_contacts": SUPPORT},
                        headers={"Cache-Control": "public, max-age=300"})


@app.post("/predict", response_model=Result)
def predict(answers: CheckIn, request: Request):
    return request.app.state.predictor.predict(answers)


@app.get("/")
def index():
    markup = (ROOT / "app/static/index.html").read_text()
    for key, value in {"APP_TITLE": COPY["app_title"], "LOADING": COPY["loading"],
                       "CONFIG_ERROR": COPY["errors"]["config"], "RETRY": COPY["controls"]["retry"],
                       "NOSCRIPT": COPY["javascript_required"], "ASSET_VERSION": ASSET_VERSION}.items():
        markup = markup.replace("__" + key + "__", escape(value))
    return HTMLResponse(markup, headers={"Cache-Control": "no-cache"})


app.mount("/static", StaticFiles(directory=ROOT / "app/static"), name="static")
