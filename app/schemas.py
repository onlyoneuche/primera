"""Strict request types; field errors are rendered separately without input values."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from ml.course_mapping import FACULTIES


class CheckIn(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", hide_input_in_errors=True)
    gender: Literal["female", "male"]
    age: int = Field(ge=16, le=60)
    faculty_group: str
    year: int = Field(ge=1, le=4)
    cgpa_band: Literal["0-1.99", "2.00-2.49", "2.50-2.99", "3.00-3.49", "3.50-4.00"]
    married: bool
    anxiety: bool
    panic: bool
    specialist: bool

    @field_validator("faculty_group")
    @classmethod
    def canonical_faculty(cls, value):
        if value not in FACULTIES:
            raise ValueError("Choose your faculty or course group.")
        return value


class Result(BaseModel):
    category: Literal["lower", "higher"]
    label: str
    title: str
    message: str
    disclaimer: str
    out_of_range_notes: list[str]
    model_note: str
