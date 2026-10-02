from pydantic import BaseModel, ConfigDict


class ExamConfigTranslationBase(BaseModel):
    language: str
    title: str
    description: str | None = None


class ExamConfigTranslationCreate(
    ExamConfigTranslationBase
):
    exam_config_id: int


class ExamConfigTranslationUpdate(BaseModel):
    language: str | None = None
    title: str | None = None
    description: str | None = None
    review_status: str | None = None


class ExamConfigTranslationResponse(
    ExamConfigTranslationBase
):
    id: int
    exam_config_id: int
    review_status: str

    model_config = ConfigDict(from_attributes=True)


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
    translations: list[ExamConfigTranslationResponse] = []

    model_config = {"from_attributes": True}