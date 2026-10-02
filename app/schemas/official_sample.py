from pydantic import BaseModel, ConfigDict


class OfficialSampleTranslationBase(BaseModel):
    language: str
    title: str
    description: str | None = None


class OfficialSampleTranslationCreate(OfficialSampleTranslationBase):
    official_sample_id: int


class OfficialSampleTranslationUpdate(BaseModel):
    language: str | None = None
    title: str | None = None
    description: str | None = None
    review_status: str | None = None


class OfficialSampleTranslationResponse(BaseModel):
    id: int
    official_sample_id: int
    language: str
    title: str
    description: str | None
    review_status: str

    model_config = ConfigDict(from_attributes=True)



class OfficialSampleCreate(BaseModel):
    content_version_id: int
    title: str
    description: str | None = None
    url: str | None = None
    source_id: int | None = None


class OfficialSampleUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    url: str | None = None
    source_id: int | None = None



class OfficialSampleResponse(BaseModel):
    id: int
    content_version_id: int
    title: str
    description: str | None
    url: str | None
    source_id: int | None

    translations: list[OfficialSampleTranslationResponse] = []

    model_config = ConfigDict(from_attributes=True)