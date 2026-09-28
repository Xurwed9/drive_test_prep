from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.catalog import router as catalog_router
from app.api.v1.states import router as states_router
from app.api.v1.content import router as content_router
from app.api.v1.admin import router as admin_router

app = FastAPI()

app.mount(
    "/storage",
    StaticFiles(directory="storage"),
    name="storage",
)

app.include_router(catalog_router, prefix="/v1")
app.include_router(states_router, prefix="/v1")
app.include_router(content_router, prefix="/v1")
app.include_router(admin_router, prefix="/v1")