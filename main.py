from fastapi import FastAPI

# 1.create an instance of FastAPI
app = FastAPI()

# 2. main route (GET /)
@app.get("/")
def get_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

# 3. health check route (GET /health)
@app.get("/health")
def get_health():
    return {
        "status": "ok"
    }