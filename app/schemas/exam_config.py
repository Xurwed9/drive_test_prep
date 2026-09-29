from pydantic import BaseModel


class ExamConfigCreate(BaseModel):
    content_version_id: int
    question_count: int
    passing_score: int
    time_limit_minutes: int | None = None
    max_mistakes: int | None = None
    is_active: bool = True


class ExamConfigUpdate(BaseModel):
    question_count: int | None = None
    passing_score: int | None = None
    time_limit_minutes: int | None = None
    max_mistakes: int | None = None
    is_active: bool | None = None


class ExamConfigResponse(BaseModel):
    id: int
    content_version_id: int
    question_count: int
    passing_score: int
    time_limit_minutes: int | None
    max_mistakes: int | None
    is_active: bool

    model_config = {"from_attributes": True}