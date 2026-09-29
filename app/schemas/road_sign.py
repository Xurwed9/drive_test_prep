from pydantic import BaseModel


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

    model_config = {
        "from_attributes": True
    }