from pydantic import BaseModel, ConfigDict


class StateCatalogItem(BaseModel):
    code: str
    name: str
    status: str
    model_config = ConfigDict(from_attributes=True)


class CatalogResponse(BaseModel):
    states: list[StateCatalogItem]