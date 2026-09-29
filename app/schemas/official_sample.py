from pydantic import BaseModel


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

    model_config = {
        "from_attributes": True
    }