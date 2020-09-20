from typing import Optional, List, Dict

from fastapi import FastAPI, Path, Body, Query
from pydantic import BaseModel, Field


global last_id
last_id = 3
app = FastAPI()

class Task(BaseModel):
    id : int = Field(title="ID of the task", example="3", description="The id is what identifies the task, it's an unique number assigned to each task")
    name: str = Field(title="Name of the task", example="APS - Big Data", description="The name is what allows the person to identify what's the task")
    description: str = Field(title="Description of the task", example="Learn to make a CRUD using FastAPI", description="The description is what allows the person to know what's the task about")
    status: str = Field(title="Status of the task", example="On going", description="The status is what allows the person to know if the task is done or not")
    class Config:
        schema_extra = {
            "example": {
                "name": "APS - Big Data",
                "description": "Learn to make a CRUD using FastAPI",
                "status": "On Going"
            }
        }

class TaskEdit(BaseModel):
    description: str = Field(title="Description of the task", example="Learn to make a CRUD using FastAPI", description="The description is what allows the person to know what's the task about")
    status: str = Field(title="Status of the task", example="On going", description="The status is what allows the person to know if the task is done or not")
    class Config:
        schema_extra = {
            "example": {
                "description": "Learn to make a CRUD using FastAPI",
                "status": "On Going"
            }
        }

class TaskAdd(BaseModel):
    name: str = Field(title="Name of the task", example="APS - Big Data", description="The name is what allows the person to identify what's the task")
    description: str = Field(title="Description of the task", example="Learn to make a CRUD using FastAPI", description="The description is what allows the person to know what's the task about")
    class Config:
        schema_extra = {
            "example": {
                "name": "APS - Big Data",
                "description": "Learn to make a CRUD using FastAPI"
            }
        }

tasks = {
    0: {"id": 0, "name": "APS - Cloud", "description":"Complete the handout", "status": "Done"},
    1: {"id": 1, "name": "Quiz - Design", "description": "Study past classes", "status": "On Going"},
    2: {"id": 2, "name": "Video - Redes", "description":"Watch the video for the next class", "status": "On Going"},
}

@app.get("/tasks", response_model=List[Task], response_description="List containing the tasks", tags=["Tasks"], description="Get a list containing tasks. If you want to get all tasks, you don't need a query parameter. If you want to filter the tasks based on status, you need a query parameter.", summary="Get tasks")
async def find_tasks(q : Optional[str] = Query(
    None, 
    alias="status", 
    title="Filter of tasks", 
    example="Examples: done, ongoing",
    description="If you want to get only the finished tasks, the value must be 'done'. To get the on going tasks, the value must be 'ongoing'. For every other value, all tasks will be returned."
)):
    if q:
        d = {}
        if q == "done":
            for i in range(0, last_id):
                if tasks[i]["status"] == "Done":
                    d.update({i: tasks[i]})
            return [d[i] for i in d]
        if q == "ongoing":
            for i in range(0, last_id):
                if tasks[i]["status"] != "Done":
                    d.update({i: tasks[i]})
            return [d[j] for j in d]
    return [tasks[t] for t in tasks]

@app.post("/createtask", response_model = Task, tags=["Tasks"],  response_description="Returns the created task", description="Create a new task, adding a name and a description. The status is initiated automatically as 'On Going', and can be changed in the /updatetasks.", summary="Create a new task")
async def add_task(task: TaskAdd = Body(...)):
    global last_id
    t = Task
    t = {"id": last_id, "name": "", "description":"", "status": "On Going"}
    t["name"] = task.name
    t["description"] = task.description
    tasks.update({last_id: t})
    last_id+=1
    return t

@app.put("/updatetask/{id_task}", response_model = Task,  response_description="Returns the updated task", tags=["Tasks"], description="Update a task, changing the description or the status. If you want to edit just one of the parameters, leave the ' ' of the other empty.", summary="Update a task")
async def update_task(task : Optional[TaskEdit] = None, *, id_task: int = Path(..., description="The ID of the task you want to update.", example= "Examples: 0, 1, 2", ge=0)):
    if task.description:
        tasks[id_task]["description"] = task.description
    if task.status:
        tasks[id_task]["status"] = task.status
    return tasks[id_task]

@app.delete("/deletetask/{id_task}", response_model=List[Task], response_description="Returns a list containing the remaining tasks", tags=["Tasks"], description="Delete an existing task, passing the ID as an argument.", summary="Delete a task")
async def delete_task(*,id_task: int = Path(..., description="The ID of the task you want to delete.", example= "Examples: 0, 1, 2", ge=0)):
    global last_id
    for i in range (id_task, last_id-1):
        tasks[i] = tasks[i + 1]
        tasks[i]["id"] = tasks[i]["id"]-1
    last_id-=1

    del tasks[last_id]
    {k: v for k, v in sorted(tasks.items(), key=lambda item: item[0])}
    return [tasks[t] for t in tasks]
