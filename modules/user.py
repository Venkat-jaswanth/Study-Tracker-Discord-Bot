from typing import Optional
from utils.context_manager import ctx_mgr
from utils.general import get_time, get_time_from_str, get_time_str
from database import Database
from utils.discord import send_message, BaseEmbed


class User:
    def __init__(self):
        self.user_id: Optional[int] = None
        self.name: Optional[str] = None
        self.join_date: Optional[int] = None
        self.dob: Optional[int] = None
        self.institution: Optional[str] = None
        self.time_zone: Optional[int] = None

    def register_user(self):
        assert self.user_id is not None
        assert self.name is not None
        assert self.join_date is not None

        query = "INSERT INTO users (user_id, name, join_date) VALUES (%s, %s, %s)"
        Database.execute_query(query, self.user_id, self.name, self.join_date)

    def load_user(self):
        assert self.user_id is not None

        query = "SELECT name, join_date, dob, institution, time_zone FROM users WHERE user_id = %s"
        result = Database.fetch_one(query, self.user_id)
        self.name = result[0]
        self.join_date = result[1]
        self.dob = result[2]
        self.institution = result[3]
        self.time_zone = result[4]

    def update_user(self):
        query = "UPDATE users SET name = %s, dob = %s, institution = %s, time_zone = %s WHERE user_id = %s"
        Database.execute_query(
            query, self.name, self.dob, self.institution, self.time_zone, self.user_id
        )


class UserEmbed(BaseEmbed):
    def __init__(self, user: User):
        super().__init__(title="User Information")
        assert user.join_date is not None
        self.add_field(name="User ID", value=f"{user.user_id}")
        self.add_field(name="Name", value=f"{user.name}")
        if user.dob is not None:
            self.add_field(name="Date of Birth", value=f"{get_time_str(user.dob)}")
        self.add_field(name="Join Date", value=f"{get_time_str(user.join_date)}")
        self.add_field(name="Institution", value=f"{user.institution}")
        self.add_field(name="Time Zone", value=f"{user.time_zone}")


async def register_user(*args: str):
    user = User()
    user.user_id = ctx_mgr().get_context_user_id()
    user.name = " ".join(args)
    user.join_date = get_time()
    user.register_user()

    embed = UserEmbed(user)
    await send_message(embed=embed)


async def set_institution(*args: str):
    user = User()
    user.user_id = ctx_mgr().get_context_user_id()
    user.load_user()
    user.institution = " ".join(args)
    user.update_user()

    embed = UserEmbed(user)
    await send_message(embed=embed)


async def set_time_zone(time_zone: str):
    user = User()
    user.user_id = ctx_mgr().get_context_user_id()
    user.load_user()
    user.time_zone = int(time_zone)
    user.update_user()

    embed = UserEmbed(user)
    await send_message(embed=embed)


async def set_dob(*args: str):
    user = User()
    user.user_id = ctx_mgr().get_context_user_id()
    user.load_user()
    user.dob = get_time_from_str(" ".join(args))
    user.update_user()

    embed = UserEmbed(user)
    await send_message(embed=embed)
