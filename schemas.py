from typing import Literal
from pydantic import BaseModel

RoleType = Literal["R", "A", "C", "I", "V", "S"]


class FunctionCreate(BaseModel):
    name: str
    parent_id: int | None = None
    description: str = ""
    aim: str = ""
    emergency_rep_id: int | None = None


class TaskCreate(BaseModel):
    title: str
    description: str = ""


class AssignmentCreate(BaseModel):
    function_id: int
    task_id: int
    role: RoleType
    r_subcategory: str | None = None
