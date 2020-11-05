# pylint: disable=missing-module-docstring,missing-class-docstring
from typing import Optional

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


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
    username: Optional[str] = Field(
        'no username',
        title='Name of the user in charge of the task',
        max_length=1024,
    )

    class Config:
        schema_extra = {
            'example': {
                'description': 'Buy baby diapers',
                'completed': False,
                'username': 'giovanna',
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
