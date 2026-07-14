from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

# 1.create an instance of FastAPI
app = FastAPI()

# 2. create in memory database to store tasks

tasks = [
    {'id': 1, 'title': 'University Studies',  'completed': False},
    {'id': 2, 'title': 'Data Analysis Course ',  'completed': False}, 
    {'id': 3, 'title': 'Tableau Project', 'completed': False}
]

# 3. create a Pydantic model for task creation
class Task(BaseModel):
    title: str

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


#  stage 3 endpoints: create a new task

# route (POST /tasks) : create a new task
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_data: Task):

    # validate the title is not empty or whitespace
    clean_title = task_data.title.strip()
    if not clean_title:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty or whitespace"
        )
    
    # create a new task with a unique id
    # the last task id in the list + 1
    new_task_id = tasks[-1]['id'] + 1 if tasks else 1

    # prepare the new task dictionary
    new_task = {
        'id': new_task_id,
        'title': clean_title,
        'completed': False
    }

    # add the new task to the tasks list
    tasks.append(new_task)
#  return the new task as a response
    return new_task