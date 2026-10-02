from fastapi import FastAPI


app = FastAPI(
    title="AI Knowledge & Action Platform",
    description="Backend platform for RAG, AI agents and knowledge-driven actions.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "AI Knowledge & Action Platform API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}