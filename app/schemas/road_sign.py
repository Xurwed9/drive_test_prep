from pydantic import BaseModel, ConfigDict


class RoadSignTranslationBase(BaseModel):
    language: str
    title: str
    description: str | None = None


class RoadSignTranslationCreate(RoadSignTranslationBase):
    road_sign_id: int


class RoadSignTranslationUpdate(BaseModel):
    language: str | None = None
    title: str | None = None
    description: str | None = None
    review_status: str | None = None


class RoadSignTranslationResponse(RoadSignTranslationBase):
    id: int
    road_sign_id: int
    review_status: str

    model_config = ConfigDict(from_attributes=True)


class RoadSignCreate(BaseModel):
    content_version_id: int
    title: str
    description: str | None = None
    image_url: str | None = None
    source_id: int | None = None


class RoadSignUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    image_url: str | None = None
    source_id: int | None = None


class RoadSignResponse(BaseModel):
    id: int
    content_version_id: int
    title: str
    description: str | None
    image_url: str | None
    source_id: int| None
    translations: list[RoadSignTranslationResponse]

    model_config = {
        "from_attributes": True
    }