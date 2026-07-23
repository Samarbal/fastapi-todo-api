from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from sqlmodel import Field, SQLModel, create_engine, Session, select 
from typing import Optional, List 

# ORM (Object relational mapper ): converts python classes to tables in the data base 



#  Define database schema --> tasks table 
class Task(SQLModel, table= True):
    id:Optional[int] = Field(default = None, primary_key= True)
    title: str
    done:bool =  False

# classes ro check api model (pydantic models )
class TaskCreate(BaseModel):
    title:str

class TaskUpdate(BaseModel):
    title: str
    done: bool 


#  connect with database : SQLite  , and will create a database file 
sqlite_file_name= 'tasks.db'
sqlite_url =f'sqlite:///{sqlite_file_name}'

# connect arguments (nessary with fastapi with sqlite )
engine = create_engine(sqlite_url, connect_args = {"check_same_thread": False})

#  function to create the table and initial data when the server starts.

def create_db_and_tables():
    # create table if not exist 
    SQLModel.metadata.create_all(engine)

    __tablename__ = "tasks"

    #  if the table is empty , we add these 3tasks 
    with Session(engine) as session: 
        statement = select(Task)
        results = session.exec(statement).first()

        if results is None :
            task1 = Task(title="Buy groceries", done=False)
            task2 = Task(title="Finish FastAPI assignment", done=False)
            task3 = Task(title="Read a programming book", done=True)
            
            session.add(task1)
            session.add(task2)
            session.add(task3)
            session.commit()


# FastAPI application with initialization function triggered at startup (Lifespan event)

app = FastAPI(title="To-Do List API with SQLite")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# 1.create an instance of FastAPI
# app = FastAPI()

# 2. create in memory database to store tasks

# tasks = [
#     {'id': 1, 'title': 'University Studies',  'completed': False},
#     {'id': 2, 'title': 'Data Analysis Course ',  'completed': False}, 
#     {'id': 3, 'title': 'Tableau Project', 'completed': False}
# ]

# 3. create a Pydantic model for task creation
# class Task(BaseModel):
#     title: str


#  4. validation  for the edit tasks, 
#  expect to recieve the title and completed status in the request body
# class TaskUpdate(BaseModel):
#     title: str 
#     completed: bool


# stage 1 endpoints: root and health check

# route (GET /)
@app.get("/", description="Get metadata and description of the Task API.")
def get_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

#  health check route (GET /health)
@app.get("/health", description="Check if the server is healthy and alive.")
def get_health():
    return {
        "status": "ok"
    }

#   Stage 2 endpoints: read tasks 

# route (GET /tasks) : get all tasks list from database 
@app.get("/tasks",response_model=List[Task], description="Get a list of all tasks.")
def get_tasks():
    with Session(engine) as session :
        # SELECT * FROM tasks
        statement = select(Task)
        tasks = session.exec(statement).all()
        return tasks

# route (GET /tasks/{task_id}) : get a specific task by id from database 
@app.get("/tasks/{task_id}", description="Get a specific task by its ID.")
def get_specific_task(task_id: int ):
    with Session(engine) as session:
        # search in db by id
        task = session.get(Task, task_id)

        if not task:
            raise HTTPException(
                status_code= status.HTTP_404_NOT_FOUND, 
                detail=f"Task {task_id} not found"
            )

        return task




#  stage 3 endpoints: create a new task
#  and store in database 

# route (POST /tasks) : create a new task
@app.post("/tasks", 
          status_code=status.HTTP_201_CREATED, 
          description="Create a new task and persist it to the SQLite database.")
def create_task(task_data: TaskCreate):

    # validate the title is not empty or whitespace
    if not task_data.title or not task_data.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title cannot be empty or contain only whitespace"
        )
    
    # create a new task with a unique id and add it to the database 
    with Session(engine) as session: 
        new_task = Task(title=task_data.title.strip(), done= False)

        session.add(new_task)
        session.commit()
        session.refresh(new_task)

    # prepare the new task dictionary
    # new_task = {
    #     'id': new_task_id,
    #     'title': clean_title,
    #     'completed': False
    # }

    # # add the new task to the tasks list
    # tasks.append(new_task)



#  return the new task as a response
    return new_task


# Stage 4 endpoints: update and delete 

# update and delete in the database 

# edit rout (PUT /tasks/{task_id}) : update a specific task by id
@app.put("/tasks/{task_id}",
         response_model=Task, 
          description="Update the title or done status of an existing task by its ID.")

def update_task(task_id : int, updated_data: TaskUpdate):

    # check clean data
    if not updated_data.title or not updated_data.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task title cannot be empty or contain only whitespace"
        )

    with Session(engine) as session:
        # search for the task on the databse 
        task = session.get(Task, task_id)

        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found")

        # update the values 
        task.title = updated_data.title.strip()
        task.done = updated_data.done

        # save the edited in the databse 
        session.add(task)
        session.commit()
        session.refresh(task)

        return task 

            


# #  search for the task to edit by id in the tasks list
#     for task in tasks:
#         if task['id'] == task_id:
#             # update the task with new data
#             task['title'] = clean_title
#             task['completed'] = task_data.completed
#             return task   # 200 by default 
        
#     raise HTTPException(
#         status_code=status.HTTP_404_NOT_FOUND,
#         detail="Task not found"
#     )



#  delete route (DELETE /tasks/{task_id}) : delete a specific task by id in the databses 
@app.delete("/tasks/{task_id}",
             status_code=status.HTTP_204_NO_CONTENT,
             description="Delete a task from the list using its unique ID.")


def delete_task(task_id: int):
    with Session(engine) as session:
        #search for the task in the db 
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )

        #delete and commit 
        session.delete(task)
        session.commit()

        return None

