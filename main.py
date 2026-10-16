from typing import List
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS: lets the grader's web page call your API from the browser
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

# ---- The four layers (lowest -> highest priority) ----
DEFAULTS = {"port": 8000, "workers": 1, "debug": "false",
            "log_level": "info", "api_key": "default-secret-000"}

YAML_LAYER = {"port": 8178, "workers": 7, "debug": "false"}

DOTENV_RAW = {"NUM_WORKERS": "7", "APP_DEBUG": "true",
              "APP_LOG_LEVEL": "debug", "APP_API_KEY": "key-d00ryvxaie"}

OS_ENV_RAW = {"APP_WORKERS": "9", "APP_LOG_LEVEL": "warning",
              "APP_API_KEY": "key-pm0toqqyef"}


def clean_keys(raw):
    """Turn APP_LOG_LEVEL -> log_level, and NUM_WORKERS -> workers (alias)."""
    out = {}
    for k, v in raw.items():
        if k == "NUM_WORKERS":
            k = "workers"
        elif k.startswith("APP_"):
            k = k[4:]
        out[k.lower()] = v
    return out


def to_bool(v):
    return str(v).strip().lower() in ("true", "1", "yes", "on")


def coerce(key, value):
    if key in ("port", "workers"):
        return int(value)
    if key == "debug":
        return to_bool(value)
    return str(value)


@app.get("/effective-config")
def effective_config(set: List[str] = Query(default=[])):
    merged = {}
    merged.update(DEFAULTS)
    merged.update(YAML_LAYER)
    merged.update(clean_keys(DOTENV_RAW))
    merged.update(clean_keys(OS_ENV_RAW))

    # CLI overrides: "port=9000" -> split at the FIRST "=" only
    for item in set:
        if "=" in item:
            k, v = item.split("=", 1)
            merged[k.strip().lower()] = v

    result = {k: coerce(k, v) for k, v in merged.items()}
    result["api_key"] = "****"   # always masked
    return result
