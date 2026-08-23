from fastapi import FastAPI

app = FastAPI(
    title="Genesis-AI API",
    version="0.1.0",
    description="Backend API for the Genesis-AI research intelligence platform.",
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
