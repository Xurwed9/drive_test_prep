from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.content_version import ContentVersion
from app.schemas.admin import (
    ContentVersionStatusUpdate,
    ContentVersionCreate,
    TranslationStatusUpdate,
    TopicCreate,
    LessonCreate,
    QuestionCreate,
    QuestionOptionCreate,
    TranslationCreate,
    SourceCreate,
    AdminLogin,AdminUserCreate,AdminUserUpdate,TopicUpdate,LessonUpdate,
    QuestionUpdate, QuestionOptionUpdate, TranslationUpdate,SourceUpdate,
)
from app.schemas.road_sign import RoadSignCreate, RoadSignUpdate, RoadSignResponse
from app.models.publication import PublicationAudit
from app.models.topic import Topic
from app.models.lesson import Lesson
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.models.translation import Translation
from app.models.source import Source
from app.services.publisher import (
    build_content_package,
    save_content_package,
)
from app.models.translation import Translation
from app.models.admin_user import AdminUser

from app.core.security import verify_password, hash_password
from app.core.auth import create_access_token, get_current_user, require_role
from app.services.content_validator import validate_content_version
from app.models.state import State
from app.models.vehicle import Vehicle
from app.models.module import Module
from app.models.road_sign import RoadSign
from app.models.official_sample import OfficialSample
from app.models.exam_config import ExamConfig

from app.schemas.official_sample import (
    OfficialSampleCreate,
    OfficialSampleUpdate,
    OfficialSampleResponse,)
from app.schemas.exam_config import ExamConfigCreate, ExamConfigResponse, ExamConfigUpdate
from sqlalchemy import func
from fastapi import Query



router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/content-versions")
async def create_content_version(
    data: ContentVersionCreate,
    curren_user: dict = Depends(require_role("admin", "editor")),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(ContentVersion).where(
            ContentVersion.state_id == data.state_id,
            ContentVersion.vehicle_id == data.vehicle_id,
            ContentVersion.module_id == data.module_id,
            ContentVersion.version == data.version,
        )
    )

    existing = result.scalar_one_or_none()

    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail="Content version already exists",
        )

    content_version = ContentVersion(
        state_id=data.state_id,
        vehicle_id=data.vehicle_id,
        module_id=data.module_id,
        version=data.version,
        available=False,
        status="draft",
    )

    session.add(content_version)

    await session.commit()
    await session.refresh(content_version)

    return {
        "id": content_version.id,
        "state_id": content_version.state_id,
        "vehicle_id": content_version.vehicle_id,
        "module_id": content_version.module_id,
        "version": content_version.version,
        "status": content_version.status,
        "available": content_version.available,
    }



@router.get("/content-versions")
async def get_content_versions(
    state: str | None = None,
    vehicle: str | None = None,
    module: str | None = None,
    status: str | None = None,
    search: str | None = None,
    language: str | None = None,
    source: str | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    query = (
        select(ContentVersion)
        .join(ContentVersion.state)
        .join(ContentVersion.vehicle)
        .outerjoin(ContentVersion.module)
    )
    if state:
        query = query.where(State.code == state)
    if vehicle:
        query = query.where(Vehicle.code == vehicle)
    if module:
        query = query.where(Module.code == module)
    if status:
        query = query.where(ContentVersion.status == status)
    if search:
        query = query.where(
            State.code.ilike(f"%{search}%")
            | State.name.ilike(f"%{search}%")
            | Vehicle.code.ilike(f"%{search}%")
            | Vehicle.name.ilike(f"%{search}%")
            | Module.code.ilike(f"%{search}%")
            | Module.name.ilike(f"%{search}%")
            | ContentVersion.version.ilike(f"%{search}%")
    )
    if language:
        query = query.where(
            ContentVersion.topics.any(
                Topic.lessons.any(
                    Lesson.questions.any(
                        Question.translations.any(
                            Translation.language == language
                        )
                    )
                )
            )
        )
    if source:
        query = query.where(
            ContentVersion.topics.any(
                Topic.lessons.any(
                    Lesson.questions.any(
                        Question.source.has(
                            Source.title.ilike(f"%{source}%")
                        )
                    )
                )
            )
        )

    query = query.order_by(ContentVersion.id.desc())
    query = query.options(
    selectinload(ContentVersion.state),
    selectinload(ContentVersion.vehicle),
    selectinload(ContentVersion.module),
)
    result = await session.execute(query)

    count_query = select(func.count()).select_from(query.subquery())
    count_result = await session.execute(count_query)
    total = count_result.scalar_one()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size)
    content_versions = result.scalars().all()

    return {
        "items": [
            {
                "id": item.id,
                "state": item.state.code,
                "state_name": item.state.name,
                "vehicle": item.vehicle.code,
                "vehicle_name": item.vehicle.name,
                "module": item.module.code if item.module else None,
                "module_name": item.module.name if item.module else None,
                "version": item.version,
                "status": item.status,
                "available": item.available,
                "published_at": item.published_at,
            }
            for item in content_versions
        ],
        "total": total,
        "page": page,
        "size": size,
    }



@router.get("/content-versions/{content_version_id}")
async def get_content_version_detail(
    content_version_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    result = await session.execute(
        select(ContentVersion)
        .options(
            selectinload(ContentVersion.state),
            selectinload(ContentVersion.vehicle),
            selectinload(ContentVersion.module),
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
        )
        .where(ContentVersion.id == content_version_id)
    )

    content_version = result.scalar_one_or_none()

    if content_version is None:
        raise HTTPException(
            status_code=404,
            detail="Content version not found",
        )

    return {
        "id": content_version.id,
        "state": content_version.state.code,
        "state_name": content_version.state.name,
        "vehicle": content_version.vehicle.code,
        "vehicle_name": content_version.vehicle.name,
        "module": (
            content_version.module.code
            if content_version.module
            else None
        ),
        "module_name": (
            content_version.module.name
            if content_version.module
            else None
        ),
        "version": content_version.version,
        "status": content_version.status,
        "available": content_version.available,
        "package_url": content_version.package_url,
        "checksum": content_version.checksum,
        "package_size": content_version.package_size,
        "minimum_app_version": content_version.minimum_app_version,
        "published_at": content_version.published_at,
        "topics": [
            {
                "id": topic.id,
                "title": topic.title,
                "lessons": [
                    {
                        "id": lesson.id,
                        "title": lesson.title,
                        "description": lesson.description,
                        "order": lesson.order,
                        "questions": [
                            {
                                "id": question.id,
                                "content_key": question.content_key,
                                "text": question.text,
                                "correct_option_id": question.correct_option_id,
                                "question_type": question.question_type,
                                "is_official": question.is_official,
                                "options": [
                                    {
                                        "option_id": option.option_id,
                                        "text": option.text,
                                        "order": option.order,
                                    }
                                    for option in question.options
                                ],
                                "translations": [
                                    {
                                        "language": translation.language,
                                        "text": translation.text,
                                        "review_status": translation.review_status,
                                    }
                                    for translation in question.translations
                                ],
                                "source": (
                                    {
                                        "id": question.source.id,
                                        "title": question.source.title,
                                        "url": question.source.url,
                                        "version": question.source.version,
                                        "page": question.source.page,
                                        "verified_at": question.source.verified_at,
                                    }
                                    if question.source
                                    else None
                                ),
                            }
                            for question in lesson.questions
                        ],
                    }
                    for lesson in topic.lessons
                ],
            }
            for topic in content_version.topics
        ],
    }



@router.get("/content-versions/{content_version_id}/audit")
async def get_content_version_audit(
    content_version_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    result = await session.execute(
        select(PublicationAudit)
        .where(
            PublicationAudit.content_version_id == content_version_id
        )
        .order_by(PublicationAudit.created_at.desc())
    )

    audits = result.scalars().all()

    return [
        {
            "id": audit.id,
            "action": audit.action,
            "user_id": audit.user_id,
            "created_at": audit.created_at,
            "notes": audit.notes,
        }
        for audit in audits
    ]



@router.patch("/content-versions/{content_version_id}/status")
async def update_content_version_status(
    content_version_id: int,
    data: ContentVersionStatusUpdate,
    current_user: dict = Depends(
    require_role("admin", "editor")),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(ContentVersion).where(
            ContentVersion.id == content_version_id
        )
    )

    content_version = result.scalar_one_or_none()

    if content_version is None:
        raise HTTPException(
            status_code=404,
            detail="Content version not found",
        )

    if content_version.status == "published" and data.status != "published":
        raise HTTPException(status_code=400, detail="Published content version is immutable")
    allowed_statuses = {
    "draft",
    "source_verified",
    "translation_pending",
    "translation_completed",
    "native_review",
    "approved",
    "published",
}

    if data.status not in allowed_statuses:
        raise HTTPException(
        status_code=400,
        detail="Invalid content version status",
    )

    allowed_transitions = {
    "draft": {"source_verified"},
    "source_verified": {"translation_pending"},
    "translation_pending": {"translation_completed"},
    "translation_completed": {"native_review"},
    "native_review": {"approved"},
    "approved": {"published"},
    "published": set(),
}

    if data.status not in allowed_transitions[content_version.status]:
        raise HTTPException(
        status_code=400,
        detail=(
            f"Invalid content version transition: "
            f"{content_version.status} -> {data.status}"
        ),
    )

    if data.status == "published":
        print("CURRENT USER:", current_user)
        if current_user["role"] != "admin":
            raise HTTPException(status_code=403, detail="Only admin can published content")
        if content_version.status != "approved":
            raise HTTPException(
                status_code=400,
                detail="Only approved content versions can be published",
            )

        content_result = await session.execute(
    select(ContentVersion)
    .options(
        selectinload(ContentVersion.state),
        selectinload(ContentVersion.vehicle),
        selectinload(ContentVersion.module),

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
    .where(ContentVersion.id == content_version_id)
)

        content_version = content_result.scalar_one()


        result = await session.execute(
            select(ContentVersion).where(
                ContentVersion.state_id == content_version.state_id,
                ContentVersion.vehicle_id == content_version.vehicle_id,
                ContentVersion.module_id == content_version.module_id,
                ContentVersion.available.is_(True),
                ContentVersion.id != content_version.id,
            )
        )

        active_versions = result.scalars().all()
        errors = validate_content_version(content_version)

        if errors:
            raise HTTPException(
                status_code=400,
                detail={
            "message": "Content validation failed",
            "errors": errors,
        },
    )


        package = build_content_package(
        content_version=content_version,
        state=content_version.state,
        vehicle=content_version.vehicle,
        module=content_version.module,
    )

        await save_content_package(
        package_data=package.model_dump(mode="json"),
        content_version=content_version,
        state_code=content_version.state.code,
        vehicle_code=content_version.vehicle.code,
        version=content_version.version,
        session=session,
        module_code=content_version.module.code if content_version.module else None,
        )
        for old_version in active_versions:
                    old_version.available = False

        content_version.available = True
        content_version.status = "published"
        content_version.published_at = datetime.now(timezone.utc)

        audit = PublicationAudit(
            content_version_id=content_version.id,
            action="published",
            user_id=current_user["user_id"],
            created_at=datetime.now(timezone.utc),
            notes="Content version published and activated",
        )

        session.add(audit)

    else:
        content_version.status = data.status

        if data.status != "published":
            content_version.published_at = None

    await session.commit()
    await session.refresh(content_version)

    return {
        "id": content_version.id,
        "status": content_version.status,
        "available": content_version.available,
        "published_at": content_version.published_at,
    }



@router.post("/content-versions/{current_version_id}/rollback/{target_version_id}")
async def rollback_content_version(current_version_id: int, target_version_id: int,
                                   session: AsyncSession = Depends(get_db),
                                   current_user: dict = Depends(require_role("admin", "editor"))):

    current_version = await session.get(ContentVersion, current_version_id)
    if current_version is None:
        raise HTTPException(status_code=404, detail="Current content version not found")
    target_version = await session.get(ContentVersion, target_version_id)
    if target_version is None:
        raise HTTPException(status_code=404, detail="Target content version not found")

    if (current_version.state_id != target_version.state_id
        or current_version.vehicle_id != target_version.vehicle_id
        or current_version.module_id != target_version.module_id):
        raise HTTPException(status_code=400, 
                            detail="Versions belong to different content scopes")
    if target_version.status != "published":
        raise HTTPException(status_code=400, detail="Target content version must be published")

    if current_version.available:
        current_version.available = False
    target_version.available = True

    audit = PublicationAudit(content_version_id=target_version.id,
                             action="rollback",
                             user_id=current_user["user_id"],
                             created_at=datetime.now(timezone.utc),
                             notes=(
                                 f"Rolled back from content version"
                                 f"{current_version.version} to {target_version.version}"
                             ))
    session.add(audit)
    await session.commit()
    return {
        "message": "Content version rolled back successfully",
        "active_version_id": target_version.id,
        "active_version": target_version.version,
    }


@router.post("/content-version/{target_id}/clone-from/{source_id}")
async def clone_content_version(target_id: int, source_id: int,
                                current_user: dict = Depends(
        require_role("admin", "editor")
    ),
                                 session: AsyncSession = Depends(get_db)):
    if target_id == source_id:
        raise HTTPException(status_code=404, detail="Source and target versions must be different")
    result = await session.execute(select(ContentVersion).where(ContentVersion.id == source_id)
                                   .options(
                                       selectinload(ContentVersion.topics)
                                       .selectinload(Topic.lessons)
                                       .selectinload(Lesson.questions)
                                       .selectinload(Question.options),

                                       selectinload(ContentVersion.topics)
                                       .selectinload(Topic.lessons)
                                       .selectinload(Lesson.questions)
                                       .selectinload(Question.translations),
                                   ))
    source_version = result.scalar_one_or_none()
    if source_version is None:
        raise HTTPException(status_code=404, detail="Source content version not found")
    result = await session.execute(select(ContentVersion).where(ContentVersion.id == target_id))
    target_version = result.scalar_one_or_none()
    if target_version is None:
        raise HTTPException(status_code=404, detail="Target content version not found")

    if target_version.status != "draft":
        raise HTTPException(status_code=400, detail="Target version must be draft")

    if target_version.available:
        raise HTTPException(status_code=400, detail="Target version must not be available")

    for source_topic in source_version.topics:
        new_topic = Topic(
            content_version_id=target_version.id,
            title=source_topic.title,
        )
        session.add(new_topic)
        await session.flush()
        for source_lesson in source_topic.lessons:
            new_lesson = Lesson(
                topic_id=new_topic.id,
                title=source_lesson.title,
                description=source_lesson.description,
                order=source_lesson.order,
            )
            session.add(new_lesson)
            await session.flush()
            for source_question in source_lesson.questions:

                new_question = Question(
                    lesson_id=new_lesson.id,
                    content_key=source_question.content_key,
                    text=source_question.text,
                    correct_option_id=source_question.correct_option_id,
                    question_type=source_question.question_type,
                    is_official=source_question.is_official,
                    source_id=source_question.source_id,
                )
                session.add(new_question)
                await session.flush()

                for source_option in source_question.options:

                    new_option = QuestionOption(
                        question_id=new_question.id,
                        option_id=source_option.option_id,
                        text=source_option.text,
                        order=source_option.order,
                    )

                    session.add(new_option)

                for source_translation in source_question.translations:

                    new_translation = Translation(
                        question_id=new_question.id,
                        language=source_translation.language,
                        text=source_translation.text,
                        review_status=source_translation.review_status,
                    )

                    session.add(new_translation)
    await session.commit()

    return {
        "message": "Content version cloned successfully",
        "source_version_id": source_version.id,
        "target_version_id": target_version.id,
    }


@router.post("/content-version/{content_version_id}/validate")
async def validate_content(
    content_version_id: int,
    current_user: dict = Depends(
        require_role("admin", "editor")
    ),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(select(ContentVersion).options(
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
    ).where(ContentVersion.id == content_version_id))
    content_version = result.scalar_one_or_none()

    if content_version is None:
        raise HTTPException(status_code=404, detail="Content version not found")

    errors = validate_content_version(content_version)
    return {
        "content_version_id": content_version.id,
        "valid": len(errors) == 0,
        "errors": errors,
    }



@router.get("/content-version/{content_version_id}/preview")
async def preview_content_versions(
    content_version_id: int, current_user: dict = Depends(require_role("admin", "editor")),
    session: AsyncSession = Depends(get_db)):

    result = await session.execute(select(ContentVersion).options(
        selectinload(ContentVersion.state),
        selectinload(ContentVersion.vehicle),
        selectinload(ContentVersion.module),

        selectinload(ContentVersion.exam_config),
        selectinload(ContentVersion.road_signs),
        selectinload(ContentVersion.official_samples),

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
    ).where(ContentVersion.id == content_version_id))
    content_version = result.scalar_one_or_none()
    if content_version is None:
        raise HTTPException(status_code=404, detail="Content version not found")
    errors = validate_content_version(content_version)
    package = build_content_package(
        content_version=content_version,
        state=content_version.state,
        vehicle=content_version.vehicle,
        module=content_version.module,
    )
    return {
        "content_version_id": content_version.id,
        "valid": len(errors) == 0,
        "errors": errors,
        "package": package.model_dump(mode="json")
    }



@router.get("/content-version/{content_version_id}/translation_check")
async def check_translations(
    content_version_id: int, languages: str = Query("en, tg"),
    current_user: dict = Depends(require_role("admin", "editor")),
    session: AsyncSession = Depends(get_db)):

    result = await session.execute(select(ContentVersion).options(
        selectinload(ContentVersion.topics)
        .selectinload(Topic.lessons)
        .selectinload(Lesson.questions)
        .selectinload(Question.translations),
    ).where(ContentVersion.id == content_version_id))
    content_version = result.scalar_one_or_none()
    if content_version is None:
        raise HTTPException(status_code=404, detail="Content version not found")
    required_languages = [
        language.strip()
        for language in languages.split(",")
        if language.strip() and language.strip() != "en"
    ]
    missing = []
    for topic in content_version.topics:
        for lesson in topic.lessons:
            for question in lesson.questions:
                existing_languages = {
                    translation.language
                    for translation in question.translations
                }

                missing_languages = [
                    language
                    for language in required_languages
                    if language not in existing_languages
                ]

                if missing_languages:
                    missing.append(
                        {
                            "question_id": question.id,
                            "content_key": question.content_key,
                            "missing_languages": missing_languages,
                        }
                    )
    return {
        "content_version_id": content_version.id,
        "required_languages": required_languages,
        "missing_translations": missing,
        "valid": len(missing) == 0,
    }


@router.get("/content-version/{content_version_id}/duplicate-check")
async def check_duplicate(
    content_version_id: int,
    current_user: dict = Depends(require_role("admin", "editor")),
    session: AsyncSession = Depends(get_db)):

    result = await session.execute(select(ContentVersion).options(
        selectinload(ContentVersion.topics)
        .selectinload(Topic.lessons)
        .selectinload(Lesson.questions),
    ).where(ContentVersion.id == content_version_id))
    content_version = result.scalar_one_or_none()
    if content_version is None:
        raise HTTPException(
            status_code=404, detail="Content version not found"
        )
    content_key_counts: dict[str, int] = {}
    for topic in content_version.topics:
        for lesson in topic.lessons:
            for question in lesson.questions:
                content_key_counts[question.content_key] = (
                    content_key_counts.get(question.content_key, 0) + 1
                )
    duplicates = [
        {
            "content_key": content_key,
            "count": count,
        }
        for content_key, count in content_key_counts.items()
        if count > 1
    ]
    return {
        "content_version_id": content_version.id,
        "duplicates": duplicates,
        "valid": len(duplicates) == 0,
    }


@router.patch("/translations/{translation_id}/status")
async def update_translation_status(
    translation_id: int,
    data: TranslationStatusUpdate,
    current_user: dict = Depends(require_role("admin", "editor")),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Translation).where(
            Translation.id == translation_id
        )
    )

    translation = result.scalar_one_or_none()

    if translation is None:
        raise HTTPException(
            status_code=404,
            detail="Translation not found",
        )

    allowed_statuses = {
        "draft",
        "translation_completed",
        "native_review",
        "approved",
    }

    if data.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid translation status",
        )
    allowed_transitions = {
    "draft": {"translation_completed"},
    "translation_completed": {"native_review"},
    "native_review": {"approved"},
    "approved": set(),
}

    if data.status not in allowed_transitions[translation.review_status]:
        raise HTTPException(
        status_code=400,
        detail=(
            f"Invalid translation transition: "
            f"{translation.review_status} -> {data.status}"
        ),
    )

    translation.review_status = data.status

    await session.commit()
    await session.refresh(translation)

    return {
        "id": translation.id,
        "question_id": translation.question_id,
        "language": translation.language,
        "review_status": translation.review_status,
    }



@router.get("/topics")
async def get_topics(
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    result = await session.execute(
        select(Topic).order_by(Topic.id)
    )

    topics = result.scalars().all()

    return [
        {
            "id": topic.id,
            "content_version_id": topic.content_version_id,
            "title": topic.title,
        }
        for topic in topics
    ]



@router.post("/topics")
async def create_topic(
    data: TopicCreate,
    current_user: dict = Depends(
        require_role("admin", "editor")
    ),
    session: AsyncSession = Depends(get_db)
):
    result = await session.execute(
        select(ContentVersion).where(
            ContentVersion.id == data.content_version_id
        )
    )
    content_version = result.scalar_one_or_none()
    if content_version is None:
        raise HTTPException(status=404, detail="Content version not found")

    topic = Topic(content_version_id=data.content_version_id,title=data.title)
    session.add(topic)
    await session.commit()
    await session.refresh(topic)
    return {
        "id": topic.id,
        "content_version_id": topic.content_version_id,
        "title": topic.title,
    }


@router.get("/topics/{topic_id}")
async def get_topic(
    topic_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    topic = await session.get(Topic, topic_id)

    if topic is None:
        raise HTTPException(
            status_code=404,
            detail="Topic not found",
        )

    return {
        "id": topic.id,
        "content_version_id": topic.content_version_id,
        "title": topic.title,
    }



@router.patch("/topics/{topic_id}")
async def update_topic(
    topic_id: int,
    data: TopicUpdate,
    current_user: dict = Depends(require_role("admin", "editor")),
    session: AsyncSession = Depends(get_db),
):
    topic = await session.get(Topic, topic_id)

    if topic is None:
        raise HTTPException(
            status_code=404,
            detail="Topic not found",
        )

    if data.title is not None:
        topic.title = data.title

    await session.commit()
    await session.refresh(topic)

    return {
        "id": topic.id,
        "content_version_id": topic.content_version_id,
        "title": topic.title,
    }



@router.delete("/topics/{topic_id}")
async def delete_topic(
    topic_id: int,
    current_user: dict = Depends(require_role("admin")),
    session: AsyncSession = Depends(get_db),
):
    topic = await session.get(Topic, topic_id)

    if topic is None:
        raise HTTPException(
            status_code=404,
            detail="Topic not found",
        )

    await session.delete(topic)
    await session.commit()

    return {
        "message": "Topic deleted successfully",
        "id": topic_id,
    }



@router.get("/lessons")
async def get_lessons(
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    result = await session.execute(
        select(Lesson).order_by(Lesson.id)
    )

    lessons = result.scalars().all()

    return [
        {
            "id": lesson.id,
            "topic_id": lesson.topic_id,
            "title": lesson.title,
            "description": lesson.description,
            "order": lesson.order,
        }
        for lesson in lessons
    ]



@router.post("/lessons")
async def create_lesson(
    data: LessonCreate,
    current_user: dict = Depends(
        require_role("admin", "editor")
    ),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Topic).where(Topic.id == data.topic_id)
    )

    topic = result.scalar_one_or_none()

    if topic is None:
        raise HTTPException(
            status_code=404,
            detail="Topic not found",
        )

    lesson = Lesson(
        topic_id=data.topic_id,
        title=data.title,
        description=data.description,
        order=data.order,
    )

    session.add(lesson)
    await session.commit()
    await session.refresh(lesson)

    return {
        "id": lesson.id,
        "topic_id": lesson.topic_id,
        "title": lesson.title,
        "description": lesson.description,
        "order": lesson.order,
    }


@router.get("/lessons/{lesson_id}")
async def get_lesson(
    lesson_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    lesson = await session.get(Lesson, lesson_id)

    if lesson is None:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found",
        )

    return {
        "id": lesson.id,
        "topic_id": lesson.topic_id,
        "title": lesson.title,
        "description": lesson.description,
        "order": lesson.order,
    }


@router.patch("/lessons/{lesson_id}")
async def update_lessons(lesson_id: int, data: LessonUpdate, current_user: dict = Depends(require_role("admin", "editor")),
                        session: AsyncSession = Depends(get_db)):
    lesson = await session.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    if data.title is not None:
        lesson.title = data.title

    if data.description is not None:
        lesson.description = data.description

    if data.order is not None:
        lesson.order = data.order

    await session.commit()
    await session.refresh(lesson)
    return {
        "id": lesson.id,
        "topic_id": lesson.topic_id,
        "title": lesson.title,
        "description": lesson.description,
        "order": lesson.order,
    }



@router.delete("/lessons/{lesson_id}")
async def delete_lesson(
    lesson_id: int,
    current_user: dict = Depends(require_role("admin")),
    session: AsyncSession = Depends(get_db),
):
    lesson = await session.get(Lesson, lesson_id)

    if lesson is None:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found",
        )

    await session.delete(lesson)
    await session.commit()

    return {
        "message": "Lesson deleted successfully",
        "id": lesson_id,
    }


@router.get("/questions")
async def get_questions(
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    result = await session.execute(
        select(Question).order_by(Question.id)
    )

    questions = result.scalars().all()

    return [
        {
            "id": question.id,
            "content_key": question.content_key,
            "lesson_id": question.lesson_id,
            "text": question.text,
            "correct_option_id": question.correct_option_id,
            "question_type": question.question_type,
            "is_official": question.is_official,
            "source_id": question.source_id,
        }
        for question in questions
    ]



@router.post("/questions")
async def create_question(
    data: QuestionCreate,
    current_user: dict = Depends(
        require_role("admin", "editor")
    ),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Lesson).where(
            Lesson.id == data.lesson_id
        )
    )

    lesson = result.scalar_one_or_none()

    if lesson is None:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found",
        )

    question = Question(
        lesson_id=data.lesson_id,
        content_key=data.content_key,
        text=data.text,
        correct_option_id=data.correct_option_id,
        question_type=data.question_type,
        is_official=data.is_official,
        source_id=data.source_id,
    )

    session.add(question)
    await session.commit()
    await session.refresh(question)

    return {
        "id": question.id,
        "content_key": question.content_key,
        "lesson_id": question.lesson_id,
    }


@router.get("/questions/{question_id}")
async def get_question(
    question_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    question = await session.get(Question, question_id)

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found",
        )

    return {
        "id": question.id,
        "content_key": question.content_key,
        "lesson_id": question.lesson_id,
        "text": question.text,
        "correct_option_id": question.correct_option_id,
        "question_type": question.question_type,
        "is_official": question.is_official,
        "source_id": question.source_id,
    }


@router.patch("/questions/{question_id}")
async def update_question(
    question_id: int,
    data: QuestionUpdate,
    current_user: dict = Depends(require_role("admin", "editor")),
    session: AsyncSession = Depends(get_db),
):
    question = await session.get(Question, question_id)

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found",
        )

    if data.content_key is not None:
        question.content_key = data.content_key

    if data.text is not None:
        question.text = data.text

    if data.correct_option_id is not None:
        question.correct_option_id = data.correct_option_id

    if data.question_type is not None:
        question.question_type = data.question_type

    if data.is_official is not None:
        question.is_official = data.is_official

    if data.source_id is not None:
        question.source_id = data.source_id

    await session.commit()
    await session.refresh(question)

    return {
        "id": question.id,
        "content_key": question.content_key,
        "lesson_id": question.lesson_id,
        "text": question.text,
        "correct_option_id": question.correct_option_id,
        "question_type": question.question_type,
        "is_official": question.is_official,
        "source_id": question.source_id,
    }



@router.delete("/questions/{question_id}")
async def delete_question(
    question_id: int,
    current_user: dict = Depends(require_role("admin")),
    session: AsyncSession = Depends(get_db),
):
    question = await session.get(Question, question_id)

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found",
        )

    await session.delete(question)
    await session.commit()

    return {
        "message": "Question deleted successfully",
        "id": question_id,
    }



@router.get("/question-options")
async def get_question_options(
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    result = await session.execute(
        select(QuestionOption).order_by(QuestionOption.id)
    )

    options = result.scalars().all()

    return [
        {
            "id": option.id,
            "question_id": option.question_id,
            "option_id": option.option_id,
            "text": option.text,
            "order": option.order,
        }
        for option in options
    ]



@router.post("/question-options")
async def create_question_option(
    data: QuestionOptionCreate,
    current_user: dict = Depends(
        require_role("admin", "editor")
    ),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Question).where(
            Question.id == data.question_id
        )
    )

    question = result.scalar_one_or_none()

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found",
        )

    option = QuestionOption(
        question_id=data.question_id,
        option_id=data.option_id,
        text=data.text,
        order=data.order,
    )

    session.add(option)
    await session.commit()
    await session.refresh(option)

    return {
        "id": option.id,
        "question_id": option.question_id,
        "option_id": option.option_id,
        "text": option.text,
        "order": option.order,
    }



@router.get("/question-options/{option_id}")
async def get_question_option(
    option_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    option = await session.get(QuestionOption, option_id)

    if option is None:
        raise HTTPException(
            status_code=404,
            detail="Question option not found",
        )

    return {
        "id": option.id,
        "question_id": option.question_id,
        "option_id": option.option_id,
        "text": option.text,
        "order": option.order,
    }



@router.patch("/question-options/{option_id}")
async def update_question_option(
    option_id: int,
    data: QuestionOptionUpdate,
    current_user: dict = Depends(require_role("admin", "editor")),
    session: AsyncSession = Depends(get_db),
):
    option = await session.get(QuestionOption, option_id)

    if option is None:
        raise HTTPException(
            status_code=404,
            detail="Question option not found",
        )

    option.option_id = data.option_id
    option.text = data.text
    option.order = data.order

    await session.commit()
    await session.refresh(option)

    return {
        "id": option.id,
        "question_id": option.question_id,
        "option_id": option.option_id,
        "text": option.text,
        "order": option.order,
    }



@router.delete("/question-options/{option_id}")
async def delete_question_option(
    option_id: int,
    current_user: dict = Depends(require_role("admin")),
    session: AsyncSession = Depends(get_db),
):
    option = await session.get(QuestionOption, option_id)

    if option is None:
        raise HTTPException(
            status_code=404,
            detail="Question option not found",
        )

    await session.delete(option)
    await session.commit()

    return {
        "message": "Question option deleted successfully",
        "id": option_id,
    }


@router.get("/translations")
async def get_translations(
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    result = await session.execute(
        select(Translation).order_by(Translation.id)
    )

    translations = result.scalars().all()

    return [
        {
            "id": translation.id,
            "question_id": translation.question_id,
            "language": translation.language,
            "text": translation.text,
            "review_status": translation.review_status,
        }
        for translation in translations
    ]


@router.post("/translations")
async def create_translation(
    data: TranslationCreate,
    current_user: dict = Depends(
        require_role("admin", "editor")
    ),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Question).where(
            Question.id == data.question_id
        )
    )

    question = result.scalar_one_or_none()

    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found",
        )

    translation = Translation(
        question_id=data.question_id,
        language=data.language,
        text=data.text,
        review_status=data.review_status,
    )

    session.add(translation)
    await session.commit()
    await session.refresh(translation)

    return {
        "id": translation.id,
        "question_id": translation.question_id,
        "language": translation.language,
        "review_status": translation.review_status,
    }



@router.get("/translations/{translation_id}")
async def get_translation(
    translation_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    translation = await session.get(Translation, translation_id)

    if translation is None:
        raise HTTPException(
            status_code=404,
            detail="Translation not found",
        )

    return {
        "id": translation.id,
        "question_id": translation.question_id,
        "language": translation.language,
        "text": translation.text,
        "review_status": translation.review_status,
    }



@router.patch("/translations/{translation_id}")
async def update_translation(
    translation_id: int,
    data: TranslationUpdate,
    current_user: dict = Depends(require_role("admin", "editor")),
    session: AsyncSession = Depends(get_db),
):
    translation = await session.get(Translation, translation_id)

    if translation is None:
        raise HTTPException(
            status_code=404,
            detail="Translation not found",
        )

    translation.language = data.language
    translation.text = data.text

    await session.commit()
    await session.refresh(translation)

    return {
        "id": translation.id,
        "question_id": translation.question_id,
        "language": translation.language,
        "text": translation.text,
        "review_status": translation.review_status,
    }



@router.delete("/translations/{translation_id}")
async def delete_translation(
    translation_id: int,
    current_user: dict = Depends(require_role("admin")),
    session: AsyncSession = Depends(get_db),
):
    translation = await session.get(Translation, translation_id)

    if translation is None:
        raise HTTPException(
            status_code=404,
            detail="Translation not found",
        )

    await session.delete(translation)
    await session.commit()

    return {
        "message": "Translation deleted successfully",
        "id": translation_id,
    }


@router.post("/source")
async def create_source(data: SourceCreate,
                        current_user: dict = Depends(
        require_role("admin", "editor")
    ),
                         session: AsyncSession = Depends(get_db)):
    source = Source(
    title=data.title,
    url=data.url,
    version=data.version,
    page=data.page,
    chapter=data.chapter,
    section=data.section,
    verified_at=data.verified_at,
)
    session.add(source)
    await session.commit()
    await session.refresh(source)
    return source



@router.get("/sources")
async def get_sources(
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Source).order_by(Source.id)
    )

    return result.scalars().all()



@router.patch("/source/{source_id}")
async def update_source(
    source_id: int,
    data: SourceUpdate,
    current_user: dict = Depends(
        require_role("admin", "editor")
    ),
    session: AsyncSession = Depends(get_db),
):
    source = await session.get(Source, source_id)

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="Source not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(source, field, value)

    await session.commit()
    await session.refresh(source)

    return source


@router.patch("/question/{question_id}/source/{source_id}")
async def attach_source_to_question(question_id:int, source_id: int,
                                    current_user: dict = Depends(
                                    require_role("admin", "editor")),
                                    session: AsyncSession = Depends(get_db)):
    
    question = await session.get(Question, question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    source = await session.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    question.source_id = source_id
    await session.commit()
    await session.refresh(question)
    return {"message": "Source attached successfully",
            "question_id": question.id,
            "source_id": question.source_id}



@router.put("/source/{source_id}")
async def update_source(source_id: int, data: SourceCreate,
                        current_user: dict = Depends(
                        require_role("admin", "editor")),                        
                        session: AsyncSession = Depends(get_db)):
    source = await session.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")

    source.title = data.title
    source.url = data.url
    source.version = data.version
    source.page = data.page
    source.verified_at = data.verified_at

    await session.commit()
    await session.refresh(source)
    return source



@router.post("/login")
async def admin_login(data: AdminLogin, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(AdminUser).where(AdminUser.username == data.username))

    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(user_id=user.id, role=user.role)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role": user.role, 
    }


@router.post("/users")
async def create_admin_user(data: AdminUserCreate, session: AsyncSession = Depends(get_db),
                            current_user: dict = Depends(require_role("admin"))):

    user = AdminUser(username=data.username,
                     password_hash=hash_password(data.password),role=data.role)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
    }



@router.get("/users")
async def get_admin_users(session: AsyncSession = Depends(get_db),
                          current_user: dict = Depends(require_role("admin"))):
    
    result = await session.execute(select(AdminUser).order_by(AdminUser.id))
    users = result.scalars().all()
    return [
        {
            "id": user.id,
            "username": user.username,
            "role": user.role,
        }
        for user in users
    ]



@router.patch("/users/{user_id}")
async def update_admin_user(user_id: int, data: AdminUserUpdate,
                            session: AsyncSession = Depends(get_db),
                            current_user: dict = Depends(require_role("admin"))):
    
    result = await session.execute(
    select(AdminUser).where(
        AdminUser.id == user_id))
    
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if data.role not in {"admin", "editor"}:
        raise HTTPException(status_code=404, detail="Invalid role")
    user.role = data.role
    await session.commit()
    await session.refresh(user)
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
    }



@router.delete("/users/{user_id}")
async def delete_admin_user(user_id: int,
                            session: AsyncSession = Depends(get_db),
                            current_user: dict = Depends(require_role("admin"))):

    result = await session.execute(
        select(AdminUser).where(
            AdminUser.id == user_id))
        
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404,detail="User not found")
    if user.id == current_user["user_id"]:
        raise HTTPException(status_code=404, detail="You cannot delete yourself")
    await session.delete(user)
    await session.commit()
    return {
        "message": "User deleted successfully",
        "user_id": user_id,
    }


@router.post("/road-signs", response_model=RoadSignResponse)
async def create_road_sign(data: RoadSignCreate,
                           current_user: dict = Depends(require_role("admin", "editor")),
                           session: AsyncSession = Depends(get_db)):

    road_sign = RoadSign(**data.model_dump())
    session.add(road_sign)
    await session.commit()
    await session.refresh(road_sign)
    return road_sign


@router.get("/road-signs", response_model=list[RoadSignResponse])
async def get_road_signs(current_user: dict = Depends(require_role("admin", "editor")),
                         session: AsyncSession = Depends(get_db)):

    result = await session.execute(select(RoadSign).order_by(RoadSign.id))
    return result.scalars().all()



@router.patch("/road-signs/{road_sign_id}")
async def update_road_sign(road_sign_id: int, data: RoadSignUpdate,
                           current_user: dict = Depends(require_role("admin", "editor")),
                           session: AsyncSession = Depends(get_db)):

    result = await session.execute(select(RoadSign).where(RoadSign.id == road_sign_id))
    road_sign = result.scalar_one_or_none()
    if road_sign is None:
        raise HTTPException(status_code=404, detail="Road sign not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(road_sign, field, value)

    await session.commit()
    await session.refresh(road_sign)
    return road_sign



@router.delete("/road-signs/{road_sign_id}")
async def delete_road_sign(
    road_sign_id: int,
    current_user: dict = Depends(require_role("admin", "editor")),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(RoadSign).where(RoadSign.id == road_sign_id)
    )

    road_sign = result.scalar_one_or_none()

    if road_sign is None:
        raise HTTPException(
            status_code=404,
            detail="Road sign not found",
        )

    await session.delete(road_sign)
    await session.commit()

    return {
        "message": "Road sign deleted successfully"
    }


@router.post(
    "/official-samples",
    response_model=OfficialSampleResponse,
)
async def create_official_sample(
    data: OfficialSampleCreate,
    current_user: dict = Depends(require_role("admin", "editor")),
    session: AsyncSession = Depends(get_db),
):
    official_sample = OfficialSample(**data.model_dump())

    session.add(official_sample)
    await session.commit()
    await session.refresh(official_sample)

    return official_sample



@router.get(
    "/official-samples",
    response_model=list[OfficialSampleResponse],
)
async def get_official_samples(
    current_user: dict = Depends(require_role("admin", "editor")),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(OfficialSample).order_by(OfficialSample.id)
    )

    return result.scalars().all()



@router.patch(
    "/official-samples/{official_sample_id}",
    response_model=OfficialSampleResponse,
)
async def update_official_sample(
    official_sample_id: int,
    data: OfficialSampleUpdate,
    current_user: dict = Depends(require_role("admin", "editor")),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(OfficialSample).where(
            OfficialSample.id == official_sample_id
        )
    )

    official_sample = result.scalar_one_or_none()

    if official_sample is None:
        raise HTTPException(
            status_code=404,
            detail="Official sample not found",
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(official_sample, field, value)

    await session.commit()
    await session.refresh(official_sample)

    return official_sample



@router.get(
    "/official-samples/{official_sample_id}",
    response_model=OfficialSampleResponse,
)
async def get_official_sample(
    official_sample_id: int,
    current_user: dict = Depends(require_role("admin", "editor")),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(OfficialSample).where(
            OfficialSample.id == official_sample_id
        )
    )

    official_sample = result.scalar_one_or_none()

    if official_sample is None:
        raise HTTPException(
            status_code=404,
            detail="Official sample not found",
        )

    return official_sample



@router.delete("/official-samples/{official_sample_id}")
async def delete_official_sample(
    official_sample_id: int,
    current_user: dict = Depends(require_role("admin", "editor")),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(OfficialSample).where(
            OfficialSample.id == official_sample_id
        )
    )

    official_sample = result.scalar_one_or_none()

    if official_sample is None:
        raise HTTPException(
            status_code=404,
            detail="Official sample not found",
        )

    await session.delete(official_sample)
    await session.commit()

    return {
        "message": "Official sample deleted successfully"
    }



@router.post(
    "/exam-config",
    response_model=ExamConfigResponse,
)
async def create_exam_config(
    data: ExamConfigCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    content_version = await db.get(
        ContentVersion,
        data.content_version_id,
    )

    if content_version is None:
        raise HTTPException(
            status_code=404,
            detail="Content version not found",
        )

    existing = await db.scalar(
        select(ExamConfig).where(
            ExamConfig.content_version_id == data.content_version_id
        )
    )

    if existing is not None:
        raise HTTPException(
            status_code=400,
            detail="Exam config already exists for this content version",
        )

    exam_config = ExamConfig(**data.model_dump())

    db.add(exam_config)
    await db.commit()
    await db.refresh(exam_config)

    return exam_config



@router.get(
    "/exam-configs",
    response_model=list[ExamConfigResponse],
)
async def get_exam_configs(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    result = await db.scalars(
        select(ExamConfig)
    )

    return result.all()



@router.get(
    "/exam-configs/{exam_config_id}",
    response_model=ExamConfigResponse,
)
async def get_exam_config(
    exam_config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    exam_config = await db.get(
        ExamConfig,
        exam_config_id,
    )

    if exam_config is None:
        raise HTTPException(
            status_code=404,
            detail="Exam config not found",
        )

    return exam_config



@router.patch(
    "/exam-configs/{exam_config_id}",
    response_model=ExamConfigResponse,
)
async def update_exam_config(
    exam_config_id: int,
    data: ExamConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    exam_config = await db.get(
        ExamConfig,
        exam_config_id,
    )

    if exam_config is None:
        raise HTTPException(
            status_code=404,
            detail="Exam config not found",
        )

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(exam_config, field, value)

    await db.commit()
    await db.refresh(exam_config)

    return exam_config



@router.delete(
    "/exam-configs/{exam_config_id}",
)
async def delete_exam_config(
    exam_config_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin", "editor")),
):
    exam_config = await db.get(
        ExamConfig,
        exam_config_id,
    )

    if exam_config is None:
        raise HTTPException(
            status_code=404,
            detail="Exam config not found",
        )

    await db.delete(exam_config)
    await db.commit()

    return {
        "message": "Exam config deleted successfully"
    }