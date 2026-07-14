from fastapi import FastAPI, HTTPException

# 1.create an instance of FastAPI
app = FastAPI()

# 2. create in memory database to store tasks

tasks = [
    {'id': 1, 'title': 'Task 1', 'description': 'This is task 1', 'completed': False},
    {'id': 2, 'title': 'Task 2', 'description': 'This is task 2', 'completed': False}, 
    {'id': 3, 'title': 'Task 3', 'description': 'This is task 3', 'completed': False}
]

# route (GET /)
@app.get("/")
def get_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

#  health check route (GET /health)
@app.get("/health")
def get_health():
    return {
        "status": "ok"
    }

#   Stage 2 endpoints: read tasks 

# route (GET /tasks) : get all tasks list 
@app.get("/tasks")
def get_tasks():
    return tasks

# route (GET /tasks/{task_id}) : get a specific task by id
@app.get("/tasks/{task_id}")
def get_specific_task(task_id: int ):
    for task in tasks:
        if task['id'] == task_id:
            return task
    # return {"error": "Task not found"}

    raise HTTPException(
        status_code=404,
          detail="Task not found")