from fastapi import FastAPI

app = FastAPI()

@app.get("/hello-world")
def hello_world():
    return {"message": "Hello, world"}

@app.get("/health")
def health():
    return {"status": "health"}

