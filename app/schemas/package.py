from datetime import datetime

from pydantic import BaseModel


class PackageQuestionOption(BaseModel):
    option_id: str
    text: str


class PackageQuestionTranslation(BaseModel):
    language: str
    text: str

    
class PackageQuestion(BaseModel):
    id: int
    content_key: str
    text: str
    correct_option_id: str
    options: list[PackageQuestionOption]
    translations: list[PackageQuestionTranslation]


class PackageLesson(BaseModel):
    id: int
    title: str
    description: str | None
    order: int
    questions: list[PackageQuestion]


class PackageTopic(BaseModel):
    id: int
    title: str
    lessons: list[PackageLesson]


class PackageExamConfig(BaseModel):
    question_count: int
    passing_score: int
    time_limit_minutes: int | None
    max_mistakes: int | None
    is_active: bool


class PackageRoadSign(BaseModel):
    id: int
    title: str
    description: str | None
    image_url: str | None


class PackageOfficialSample(BaseModel):
    id: int
    title: str
    description: str | None
    url: str | None


class ContentPackage(BaseModel):
    schema_version: int

    state: str
    vehicle_type: str
    module: str | None

    content_version: str
    available: bool

    languages: list[str]

    package_size_bytes: int | None
    checksum_sha256: str | None
    package_url: str | None
    minimum_app_version: str | None
    published_at: datetime | None
    topics: list[PackageTopic]
    exam_config: PackageExamConfig | None
    road_signs: list[PackageRoadSign]
    official_samples: list[PackageOfficialSample]