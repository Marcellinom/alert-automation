from fastapi import FastAPI, Request
app = FastAPI()

@app.get("/")
async def run_task(request: Request):
    body = await request.body()
    return {body}