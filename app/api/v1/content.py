from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.content_version import ContentVersion
from app.models.state import State
from app.models.vehicle import Vehicle
from app.models.module import Module
from app.models.topic import Topic
from app.models.lesson import Lesson
from app.models.question import Question
from app.schemas.package import (
    ContentPackage,
    PackageQuestion,
    PackageQuestionOption,
    PackageLesson,
    PackageTopic,
    PackageQuestionTranslation,
)
from app.schemas.content import ManifestResponse, ContentUpdateItem
from app.services.package import (build_package_bytes, calculate_sha256,
                                  calculate_package_size)
from app.services.storage import storage
from app.services.publisher import build_content_package


router = APIRouter()


@router.get("/content/{state_code}/{vehicle_code}/manifest",
            response_model=ManifestResponse)
async def get_manifest(state_code: str, vehicle_code: str,
                       session: AsyncSession = Depends(get_db)):
    state_result = await session.execute(select(State).where(State.code == state_code))
    state = state_result.scalar_one_or_none()
    if state is None:
        raise HTTPException(status_code=404, detail="State not found")

    vehicle_result = await session.execute(select(Vehicle).where(Vehicle.code == vehicle_code))
    vehicle = vehicle_result.scalar_one_or_none()
    if vehicle is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    content_result = await session.execute(
    select(ContentVersion)
    .options(
        selectinload(ContentVersion.topics)
        .selectinload(Topic.lessons)
        .selectinload(Lesson.questions)
        .selectinload(Question.translations)
    )
    .where(
        ContentVersion.state_id == state.id,
        ContentVersion.vehicle_id == vehicle.id,
        ContentVersion.module_id.is_(None),
        ContentVersion.available.is_(True),
        ContentVersion.status == "published",
    )
)
    content_version = content_result.scalar_one_or_none()
    if content_version is None:
        raise HTTPException(status_code=404, detail="Content version not found")

    languages = {"en"}

    for topic in content_version.topics:
        for lesson in topic.lessons:
            for question in lesson.questions:
                for translation in question.translations:
                    languages.add(translation.language)
    return {
    "state": state.code,
    "vehicle": vehicle.code,
    "module": None,
    "content_version": content_version.version,
    "available": content_version.available,
    "languages": sorted(languages),
    "package_size_bytes": content_version.package_size,
    "checksum_sha256": content_version.checksum,
    "package_url": content_version.package_url,
    "minimum_app_version": content_version.minimum_app_version,
    "published_at": content_version.published_at,
}



@router.get(
    "/content/{state_code}/{vehicle_code}/{module_code}/manifest",
    response_model=ManifestResponse,
)
async def get_module_manifest(
    state_code: str,
    vehicle_code: str,
    module_code: str,
    session: AsyncSession = Depends(get_db),
):
    state_result = await session.execute(
        select(State).where(State.code == state_code)
    )
    state = state_result.scalar_one_or_none()

    if state is None:
        raise HTTPException(status_code=404, detail="State not found")

    vehicle_result = await session.execute(
        select(Vehicle).where(Vehicle.code == vehicle_code)
    )
    vehicle = vehicle_result.scalar_one_or_none()

    if vehicle is None:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found",
        )

    module_result = await session.execute(
        select(Module).where(
            Module.code == module_code,
            Module.vehicle_id == vehicle.id,
        )
    )
    module = module_result.scalar_one_or_none()

    if module is None:
        raise HTTPException(status_code=404, detail="Module not found")

    content_result = await session.execute(
    select(ContentVersion)
    .options(
        selectinload(ContentVersion.topics)
        .selectinload(Topic.lessons)
        .selectinload(Lesson.questions)
        .selectinload(Question.translations)
    )
    .where(
        ContentVersion.state_id == state.id,
        ContentVersion.vehicle_id == vehicle.id,
        ContentVersion.module_id == module.id,
        ContentVersion.available.is_(True),
        ContentVersion.status == "published",
    )
)
    content_version = content_result.scalar_one_or_none()

    if content_version is None:
        raise HTTPException(
            status_code=404,
            detail="Content version not found",
        )

    languages = {"en"}

    for topic in content_version.topics:
        for lesson in topic.lessons:
            for question in lesson.questions:
                for translation in question.translations:
                    languages.add(translation.language)
    return {
        "state": state.code,
        "vehicle": vehicle.code,
        "module": module.code,
        "content_version": content_version.version,
        "available": content_version.available,
        "languages": sorted(languages),
        "package_size_bytes": content_version.package_size,
        "checksum_sha256": content_version.checksum,
        "package_url": content_version.package_url,
        "minimum_app_version": content_version.minimum_app_version,
        "published_at": content_version.published_at,
    }



@router.get("/content/updates", response_model=list[ContentUpdateItem])
async def get_content_updates(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(ContentVersion).options(
        selectinload(ContentVersion.state),
        selectinload(ContentVersion.vehicle),
        selectinload(ContentVersion.module),
    ).where(
        ContentVersion.available.is_(True),
        ContentVersion.status == "published",
    ))
    content_versions = result.scalars().all()
    return [
        {"state": content_version.state.code,
         "vehicle": content_version.vehicle.code,
         "module": (
             content_version.module.code
             if content_version.module else None
         ),
         "content_version": content_version.version,}
         for content_version in content_versions
    ]




@router.get(
    "/content/{state_code}/{vehicle_code}/package",
    response_model=ContentPackage,
)
async def get_content_package(
    state_code: str,
    vehicle_code: str,
    session: AsyncSession = Depends(get_db),
):
    state_result = await session.execute(
        select(State).where(State.code == state_code)
    )
    state = state_result.scalar_one_or_none()

    if state is None:
        raise HTTPException(
            status_code=404,
            detail="State not found",
        )

    vehicle_result = await session.execute(
        select(Vehicle).where(Vehicle.code == vehicle_code)
    )
    vehicle = vehicle_result.scalar_one_or_none()

    if vehicle is None:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found",
        )

    result = await session.execute(
        select(ContentVersion)
.options(
    selectinload(ContentVersion.topics)
    .selectinload(Topic.lessons)
    .selectinload(Lesson.questions)
    .selectinload(Question.options),

    selectinload(ContentVersion.topics)
    .selectinload(Topic.lessons)
    .selectinload(Lesson.questions)
    .selectinload(Question.translations),

    selectinload(ContentVersion.topics)
    .selectinload(Topic.lessons)
    .selectinload(Lesson.questions)
    .selectinload(Question.source),

    selectinload(ContentVersion.exam_config),

    selectinload(ContentVersion.road_signs),

    selectinload(ContentVersion.official_samples),
)
        .where(
            ContentVersion.state_id == state.id,
            ContentVersion.vehicle_id == vehicle.id,
            ContentVersion.module_id.is_(None),
            ContentVersion.available.is_(True),
            ContentVersion.status == "published",
        )
    )

    content_version = result.scalar_one_or_none()

    if content_version is None:
        raise HTTPException(
            status_code=404,
            detail="Published content package not found",
        )

    topics = []

    for topic in content_version.topics:
        lessons = []

        for lesson in topic.lessons:
            questions = []

            for question in lesson.questions:
                options = [
                    PackageQuestionOption(
                        option_id=option.option_id,
                        text=option.text,
                    )
                    for option in question.options
                ]
                translations = [
                    PackageQuestionTranslation(
                        language=translation.language,
                        text=translation.text,
        )
        for translation in question.translations
    ]

                questions.append(
                    PackageQuestion(
                        id=question.id,
                        content_key=question.content_key,
                        text=question.text,
                        correct_option_id=question.correct_option_id,
                        options=options,
                        translations=translations,
                    )
                )

            lessons.append(
                PackageLesson(
                    id=lesson.id,
                    title=lesson.title,
                    description=lesson.description,
                    order=lesson.order,
                    questions=questions,
                )
            )

        topics.append(
            PackageTopic(
                id=topic.id,
                title=topic.title,
                lessons=lessons,
            )
        )

    languages = {"en"}

    for topic in content_version.topics:
        for lesson in topic.lessons:
            for question in lesson.questions:
                for translation in question.translations:
                    languages.add(translation.language)

    package = build_content_package(
    content_version=content_version,
    state=state,
    vehicle=vehicle,
)

    package_data = package.model_dump(mode="json")

    package_bytes = build_package_bytes(package_data)

    package_path = storage.save_package(
        package_bytes=package_bytes,
        state_code=state.code,
        vehicle_code=vehicle.code,
        version=content_version.version,
    )

    checksum_sha256, package_size_bytes = storage.get_file_integrity(
        package_path
    )

    package_url = storage.get_package_url(
        state_code=state.code,
        vehicle_code=vehicle.code,
        version=content_version.version,
    )

    package.package_size_bytes = package_size_bytes
    package.checksum_sha256 = checksum_sha256
    package.package_url = package_url

    return package




@router.get(
    "/content/{state_code}/{vehicle_code}/{module_code}/package",
    response_model=ContentPackage,
)
async def get_module_content_package(
    state_code: str,
    vehicle_code: str,
    module_code: str,
    session: AsyncSession = Depends(get_db),
):
    state_result = await session.execute(
        select(State).where(State.code == state_code)
    )

    state = state_result.scalar_one_or_none()

    if state is None:
        raise HTTPException(
            status_code=404,
            detail="State not found",
        )

    vehicle_result = await session.execute(
        select(Vehicle).where(Vehicle.code == vehicle_code)
    )

    vehicle = vehicle_result.scalar_one_or_none()

    if vehicle is None:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found",
        )

    module_result = await session.execute(
        select(Module).where(
            Module.code == module_code,
            Module.vehicle_id == vehicle.id,
        )
    )

    module = module_result.scalar_one_or_none()

    if module is None:
        raise HTTPException(
            status_code=404,
            detail="Module not found",
        )

    result = await session.execute(
    select(ContentVersion)
    .options(
        selectinload(ContentVersion.topics)
        .selectinload(Topic.lessons)
        .selectinload(Lesson.questions)
        .selectinload(Question.options),
        selectinload(ContentVersion.topics)
        .selectinload(Topic.lessons)
        .selectinload(Lesson.questions)
        .selectinload(Question.translations),
    )
    .where(
        ContentVersion.state_id == state.id,
        ContentVersion.vehicle_id == vehicle.id,
        ContentVersion.module_id == module.id,
        ContentVersion.available.is_(True),
        ContentVersion.status == "published",
    )
)

    content_version = result.scalar_one_or_none()

    if content_version is None:
        raise HTTPException(
            status_code=404,
            detail="Content version not found",
        )

    result = await session.execute(
        select(ContentVersion)
        .options(
            selectinload(ContentVersion.topics)
            .selectinload(Topic.lessons)
            .selectinload(Lesson.questions)
            .selectinload(Question.options),

            selectinload(ContentVersion.topics)
            .selectinload(Topic.lessons)
            .selectinload(Lesson.questions)
            .selectinload(Question.translations),
        )
        .where(
            ContentVersion.id == content_version.id,
        )
    )

    topics = []

    for topic in content_version.topics:
        lessons = []

        for lesson in topic.lessons:
            questions = []

            for question in lesson.questions:
                options = [
                    PackageQuestionOption(
                        option_id=option.option_id,
                        text=option.text,
                    )
                    for option in question.options
                ]
                translations = [
                    PackageQuestionTranslation(
                        language=translation.language,
                        text=translation.text,
                    )
                    for translation in question.translations
                ]

                questions.append(
                    PackageQuestion(
                        id=question.id,
                        text=question.text,
                        correct_option_id=question.correct_option_id,
                        content_key=question.content_key,
                        options=options,
                        translations=translations,
                    )
                )

            lessons.append(
                PackageLesson(
                    id=lesson.id,
                    title=lesson.title,
                    description=lesson.description,
                    order=lesson.order,
                    questions=questions,
                )
            )

        topics.append(
            PackageTopic(
                id=topic.id,
                title=topic.title,
                lessons=lessons,
            )
        )

    languages = {"en"}

    for topic in content_version.topics:
        for lesson in topic.lessons:
            for question in lesson.questions:
                for translation in question.translations:
                    languages.add(translation.language)

    package = build_content_package(
        content_version=content_version,
        state=state,
        vehicle=vehicle,
    )
    package.package_size_bytes = content_version.package_size
    package.checksum_sha256 = content_version.checksum
    package.package_url = content_version.package_url

    return package