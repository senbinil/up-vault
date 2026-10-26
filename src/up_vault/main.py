from fastapi import FastAPI

from up_vault.api.routes.query import router as query_router

app = FastAPI(title="up-vault", version="0.1.0")
app.include_router(query_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
