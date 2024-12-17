from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from .models import User
from .schemas import UserCreateModel
from .utils import generate_passwd_hash


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession) -> User | None:
        """
        Retrieve a user by their email address.
        """
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        return result.first()

    async def user_exists(self, email: str, session: AsyncSession) -> bool:
        """
        Check if a user with the given email exists.
        """
        return bool(await self.get_user_by_email(email, session))

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession) -> User:
        """
        Create a new user in the database.
        """
        user_data_dict = user_data.dict()  # Using `dict` to convert the model to a dictionary.
        new_user = User(**user_data_dict)

        # Hash the password and set default role.
        new_user.password_hash = generate_passwd_hash(
            user_data_dict["password"])
        new_user.role = "user"

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)  # Refresh to get updated data.

        return new_user

    async def update_user(self, user: User, user_data: dict, session: AsyncSession) -> User:
        """
        Update an existing user's attributes with the given data.
        """
        for key, value in user_data.items():
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)  # Refresh to get updated data.

        return user
