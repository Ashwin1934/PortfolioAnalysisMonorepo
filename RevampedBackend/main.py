from fastapi import FastAPI

# Create an instance of the FastAPI app
app = FastAPI()

# Define a basic endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to my FastAPI server!"}

@app.get("/greet/{name}")
async def greet(name: str):
    return {"message": f"Hello, {name}!"}
