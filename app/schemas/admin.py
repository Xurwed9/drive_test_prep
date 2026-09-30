from pydantic import BaseModel
from typing import Literal
from app.models.translation import Translation
from datetime import datetime



class ContentVersionStatusUpdate(BaseModel):
    status: Literal[
        "draft",
        "source_verified",
        "translation_pending",
        "translation_completed",
        "native_review",
        "approved",
        "published",
    ]


class ContentVersionCreate(BaseModel):
    state_id: int
    vehicle_id: int
    module_id: int | None = None
    version: str



class TranslationStatusUpdate(BaseModel):
    status: str


class TopicCreate(BaseModel):
    content_version_id: int
    title: str


class LessonCreate(BaseModel):
    topic_id: int
    title: str
    description: str | None = None
    order: int


class QuestionCreate(BaseModel):
    lesson_id: int
    content_key: str
    text: str
    correct_option_id: str
    question_type: str = "multiple_choice"
    is_official: bool = False
    source_id: int | None = None


class QuestionOptionCreate(BaseModel):
    question_id: int
    option_id: str
    text: str
    order: int


class TranslationCreate(BaseModel):
    question_id: int
    language: str
    text: str
    review_status: str = "draft"



class SourceCreate(BaseModel):
    title: str
    url: str | None = None
    version: str | None = None
    page: str | None = None
    chapter: str | None = None
    section: str | None = None
    verified_at: datetime | None = None


class SourceUpdate(BaseModel):
    title: str | None = None
    url: str | None = None
    version: str | None = None
    page: str | None = None
    chapter: str | None = None
    section: str | None = None
    verified_at: datetime | None = None



class AdminLogin(BaseModel):
    username: str
    password: str


class AdminUserCreate(BaseModel):
    username: str
    password: str
    role: str = "editor"


class AdminUserUpdate(BaseModel):
    role: str


class TopicUpdate(BaseModel):
    title: str | None = None


class LessonUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    order: int | None = None



class QuestionUpdate(BaseModel):
    content_key: str | None = None
    text: str | None = None
    correct_option_id: str | None = None
    question_type: str | None = None
    is_official: bool | None = None
    source_id: int | None = None


class QuestionOptionUpdate(BaseModel):
    option_id: str | None = None
    text: str | None = None
    order: int | None = None


class TranslationUpdate(BaseModel):
    language: str | None = None
    text: str | None = None


class StateCreate(BaseModel):
    code: str
    name: str
    status: str = "coming_soon"


class StateUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    status: str | None = None


class StateResponse(BaseModel):
    id: int
    code: str
    name: str
    status: str

    model_config = {"from_attributes": True}



class VehicleCreate(BaseModel):
    code: str
    name: str


class VehicleUpdate(BaseModel):
    code: str | None = None
    name: str | None = None


class VehicleResponse(BaseModel):
    id: int
    code: str
    name: str

    model_config = {"from_attributes": True}



class ModuleCreate(BaseModel):
    vehicle_id: int
    code: str
    name: str


class ModuleUpdate(BaseModel):
    vehicle_id: int | None = None
    code: str | None = None
    name: str | None = None


class ModuleResponse(BaseModel):
    id: int
    vehicle_id: int
    code: str
    name: str

    model_config = {"from_attributes": True}