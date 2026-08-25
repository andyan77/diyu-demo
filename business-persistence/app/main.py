from fastapi import FastAPI

from app.api import content, identity, knowledge, operations, publish, tasks

app = FastAPI(title="diyu M2 business-persistence", version="0.1.0")

app.include_router(identity.router)
app.include_router(operations.router)
app.include_router(tasks.router)
app.include_router(content.router)
app.include_router(publish.router)
app.include_router(knowledge.router)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
