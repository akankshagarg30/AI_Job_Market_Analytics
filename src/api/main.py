from fastapi import FastAPI

app = FastAPI(
    title="AI Job Market Analytics API",
    description="REST API for the AI Job Market Analytics Platform",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "AI Job Market Analytics API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }