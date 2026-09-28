from datetime import datetime
from pydantic import BaseModel


class ManifestResponse(BaseModel):
    state: str
    vehicle: str
    module: str | None
    content_version: str
    available: bool
    languages: list[str]
    package_size_bytes: int | None
    checksum_sha256: str | None
    package_url: str | None
    minimum_app_version: str | None
    published_at: datetime | None


class ContentUpdateItem(BaseModel):
    state: str
    vehicle: str
    module: str | None
    content_version: str