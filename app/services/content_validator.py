from app.models.content_version import ContentVersion


def validate_content_version(
    content_version: ContentVersion,
) -> list[str]:
    errors: list[str] = []

    if not content_version.topics:
        errors.append(
            "Content version has no topics"
        )
        return errors

    content_keys: set[str] = set()

    for topic in content_version.topics:

        if not topic.lessons:
            errors.append(
                f"Topic '{topic.title}' has no lessons"
            )
            continue

        for lesson in topic.lessons:

            if not lesson.questions:
                errors.append(
                    f"Lesson '{lesson.title}' has no questions"
                )
                continue

            for question in lesson.questions:

                if not question.options:
                    errors.append(
                        f"Question '{question.content_key}' has no options"
                    )
                    continue

                if question.content_key in content_keys:
                    errors.append(
                        f"Duplicate content_key: "
                        f"{question.content_key}"
                    )
                else:
                    content_keys.add(
                        question.content_key
                    )

                option_ids = {
                    option.option_id
                    for option in question.options
                }

                if question.correct_option_id not in option_ids:
                    errors.append(
                        f"Question "
                        f"'{question.content_key}' "
                        f"has invalid correct_option_id"
                    )

                if question.source_id is None:
                    errors.append(
                    f"Question '{question.content_key}' must have a source"
                    )
                elif question.source is None:
                    errors.append(
                        f"Question '{question.content_key}' has invalid source"
                    )
                elif question.source.verified_at is None:
                    errors.append(
                        f"Source for question '{question.content_key}' is not verified"
                 )

                for translation in question.translations:

                    if translation.review_status != "approved":
                        errors.append(
                            f"Translation "
                            f"'{translation.language}' "
                            f"for question "
                            f"'{question.content_key}' "
                            f"is not approved"
                        )

    return errors