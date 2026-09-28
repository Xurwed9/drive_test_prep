import asyncio

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.admin_user import AdminUser


async def main():
    async with SessionLocal() as session:
        user = AdminUser(
            username="admin",
            password_hash=hash_password("admin123"),
            role="admin",
        )

        session.add(user)
        await session.commit()

        print("Admin created successfully")


if __name__ == "__main__":
    asyncio.run(main())