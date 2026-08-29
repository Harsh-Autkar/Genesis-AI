from fastapi import FastAPI

from .api.papers import router as papers_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Genesis-AI API",
        version="0.1.0",
        description="Backend API for the Genesis-AI research intelligence platform.",
    )

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    app.include_router(papers_router)

    return app


app = create_app()