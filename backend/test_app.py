from fastapi import FastAPI

app = FastAPI(title="IntelliMoney-Test")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"app": "IntelliMoney-Test"}
