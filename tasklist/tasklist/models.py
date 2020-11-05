# pylint: disable=missing-module-docstring,missing-class-docstring
from typing import Optional
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module
import uuid

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
    user_uuid: uuid.UUID = Field(
        title="UUID of the user in charge of the task",
    )

    class Config:
        schema_extra = {
            'example': {
                'description': 'Buy baby diapers',
                'completed': False,
                'user_uuid': '3668e9c9-df18-4ce2-9bb2-82f907cf110c',
            }
        }

class User(BaseModel):

    name: Optional[str] = Field(
        'no name',
        title='Name of the user',
        max_length=1024,
    )

    class Config:
        schema_extra = {
            'example': {
                'name': 'giovanna',
            }
        }
