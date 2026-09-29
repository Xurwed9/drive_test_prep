from app.services.package import build_package_bytes
from app.services.storage import storage
from app.models.content_version import ContentVersion
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.package import (
    ContentPackage,
    PackageQuestionOption,
    PackageQuestionTranslation,
    PackageQuestion,
    PackageLesson,
    PackageTopic,
    PackageExamConfig,
    PackageOfficialSample,
    PackageRoadSign,
)


def build_content_package(
    content_version: ContentVersion,
    state,
    vehicle,
    module=None,
):
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
    exam_config = None

    if content_version.exam_config:
        exam_config = PackageExamConfig(
            question_count=content_version.exam_config.question_count,
            passing_score=content_version.exam_config.passing_score,
            time_limit_minutes=content_version.exam_config.time_limit_minutes,
            max_mistakes=content_version.exam_config.max_mistakes,
            is_active=content_version.exam_config.is_active,
        )

    road_signs = [
    PackageRoadSign(
        id=sign.id,
        title=sign.title,
        description=sign.description,
        image_url=sign.image_url,
    )
    for sign in content_version.road_signs
    ]

    official_samples = [
        PackageOfficialSample(
            id=sample.id,
            title=sample.title,
            description=sample.description,
            url=sample.url,
        )
        for sample in content_version.official_samples
    ]

    return ContentPackage(
        schema_version=1,
        state=state.code,
        vehicle_type=vehicle.code,
        module=module.code if module else None,
        content_version=content_version.version,
        available=content_version.available,
        languages=sorted(languages),
        package_size_bytes=None,
        checksum_sha256=None,
        package_url=None,
        minimum_app_version=content_version.minimum_app_version,
        published_at=None,
        topics=topics,
        exam_config=exam_config,
        road_signs=road_signs,
        official_samples=official_samples,
    )


async def save_content_package(
    package_data: dict,
    content_version: ContentVersion,
    state_code: str,
    vehicle_code: str,
    version: str,
    session: AsyncSession,
    module_code: str | None = None,
):
    package_bytes = build_package_bytes(package_data)

    staged_path = storage.stage_package(
        package_bytes=package_bytes,
        state_code=state_code,
        vehicle_code=vehicle_code,
        version=version,
        module_code=module_code,
    )

    checksum_sha256, package_size_bytes = storage.get_file_integrity(
        staged_path
    )

    is_valid = storage.verify_file_integrity(
        staged_path,
        checksum_sha256,
    )

    if not is_valid:
        raise ValueError("Package integrity verification failed")

    package_path = storage.activate_package(
        staged_path=staged_path,
        state_code=state_code,
        vehicle_code=vehicle_code,
        version=version,
        module_code=module_code,
    )

    package_url = storage.get_package_url(
        state_code=state_code,
        vehicle_code=vehicle_code,
        version=version,
        module_code=module_code,
    )

    content_version.package_url = package_url
    content_version.checksum = checksum_sha256
    content_version.package_size = package_size_bytes

    return {
        "package_path": package_path,
        "package_url": package_url,
        "checksum_sha256": checksum_sha256,
        "package_size_bytes": package_size_bytes,
    }