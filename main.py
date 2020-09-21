# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring
import uuid

from typing import Optional, Dict

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field


# pylint: disable=too-few-public-methods
class Task(BaseModel):
    description: Optional[str] = Field(
        'no description',
        title='Task description',
        max_length=1024,
    )
    completed: Optional[bool] = Field(
        False,
        title='Shows whether the task was completed',
    )

    class Config:
        schema_extra = {
            'example': {
                'description': 'Buy baby diapers',
                'completed': False,
            }
        }


tags_metadata = [
    {
        'name': 'task',
        'description': 'Operations related to tasks.',
    },
]

app = FastAPI(
    title='Task list',
    description='Task-list project for the **Megadados** course',
    openapi_tags=tags_metadata,
)

class DBSession:
    tasks = {}
    def __init__(self):
        self.tasks = DBSession.tasks
        
def get_db():
    return DBSession()


@app.get(
    '/task',
    tags=['task'],
    summary='Reads task list',
    description='Reads the whole task list.',
    response_model=Dict[uuid.UUID, Task],
)
async def read_tasks(completed: bool = None, db: DBSession = Depends(get_db)):
    if completed is None:
        return db.tasks
    return {
        uuid_: item
        for uuid_, item in db.tasks.items() if item.completed == completed
    }


@app.post(
    '/task',
    tags=['task'],
    summary='Creates a new task',
    description='Creates a new task and returns its UUID.',
    response_model=uuid.UUID,
)
async def create_task(item: Task, db: DBSession = Depends(get_db)):
    uuid_ = uuid.uuid4()
    db.tasks[uuid_] = item
    return uuid_


@app.get(
    '/task/{uuid_}',
    tags=['task'],
    summary='Reads task',
    description='Reads task from UUID.',
    response_model=Task,
)
async def read_task(uuid_: uuid.UUID, db: DBSession = Depends(get_db)):
    try:
        return db.tasks[uuid_]
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='Task not found',
        ) from exception


@app.put(
    '/task/{uuid_}',
    tags=['task'],
    summary='Replaces a task',
    description='Replaces a task identified by its UUID.',
)
async def replace_task(uuid_: uuid.UUID, item: Task, db: DBSession = Depends(get_db)):
    try:
        db.tasks[uuid_] = item
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='Task not found',
        ) from exception


@app.patch(
    '/task/{uuid_}',
    tags=['task'],
    summary='Alters task',
    description='Alters a task identified by its UUID',
)
async def alter_task(uuid_: uuid.UUID, item: Task, db: DBSession = Depends(get_db)):
    try:
        update_data = item.dict(exclude_unset=True)
        db.tasks[uuid_] = db.tasks[uuid_].copy(update=update_data)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='Task not found',
        ) from exception


@app.delete(
    '/task/{uuid_}',
    tags=['task'],
    summary='Deletes task',
    description='Deletes a task identified by its UUID',
)
async def remove_task(uuid_: uuid.UUID, db: DBSession = Depends(get_db)):
    try:
        del db.tasks[uuid_]
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='Task not found',
        ) from exception