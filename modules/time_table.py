from typing import Optional, List
from discord.ext.commands import Bot  # type: ignore

from utils.context_manager import ctx_mgr
from utils.random import generate_random_string
from utils.discord import send_message, BaseEmbed, get_channel, Embed
from utils.general import get_time, get_day, get_time_frmt
from database import Database
from logging import info


class TimeTableEntry:
    def __init__(self):
        self.tt_id: Optional[str] = None
        self.time: Optional[int] = None
        self.days: Optional[int] = None
        self.duration: Optional[int] = None
        self.name: Optional[str] = None
        self.user_id: Optional[int] = None
        self.description: Optional[str] = None
        self.ping: Optional[bool] = None
        self.active: Optional[bool] = None

    def generate_id(self):
        while True:
            self.tt_id = generate_random_string(12)
            try:
                query = "SELECT tt_id FROM Time_Table WHERE tt_id = %s"
                Database.fetch_one(query, self.tt_id)
            except:
                break

    def check_valid(self):
        if (
            self.tt_id is None
            or self.time is None
            or self.days is None
            or self.duration is None
            or self.name is None
            or self.user_id is None
            or self.ping is None
            or self.active is None
        ):
            return False
        return True

    def save(self):
        query = (
            "INSERT INTO Time_Table (tt_id, user_id, name, description, days, time, duration, ping, active) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        Database.execute_query(
            query,
            self.tt_id,
            self.user_id,
            self.name,
            self.description,
            self.days,
            self.time,
            self.duration,
            self.ping,
            self.active
        )
    
    def delete(self):
        assert self.tt_id is not None
        query = "DELETE FROM Time_Table WHERE tt_id = %s"
        Database.execute_query(query, self.tt_id)
    
    def load(self):
        assert self.tt_id is not None
        query = "SELECT user_id, name, description, days, time, duration, ping, active FROM Time_Table WHERE tt_id = %s"
        result = Database.fetch_one(query, self.tt_id)
        self.user_id = result[0]
        self.name = result[1]
        self.description = result[2]
        self.days = result[3]
        self.time = result[4]
        self.duration = result[5]
        self.ping = result[6]
        self.active = result[7]
    
    def get_days(self):
        assert self.days is not None
        days: List[str] = []
        for i, day in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
            if self.days & (1 << i):
                days.append(day)
        return days


class TimeTableEntryDetailsEmbed(BaseEmbed):
    def __init__(self, tt_entry: TimeTableEntry):
        super().__init__(title="Time Table Entry Details")
        self.add_field(name="ID", value=f"{tt_entry.tt_id}")
        self.add_field(name="Name", value=f"{tt_entry.name}")
        self.add_field(name="Description", value=f"{tt_entry.description}")
        self.add_field(name="Time", value=str(tt_entry.time))
        self.add_field(name="Days", value=" ".join(tt_entry.get_days()))
        self.add_field(name="Duration", value=str(tt_entry.duration))
        self.add_field(name="Ping", value=str(tt_entry.ping))
        self.add_field(name="Active", value=str(tt_entry.active))


class TimeTableEntryAlertEmbed(Embed):
    def __init__(self, tt_entry: TimeTableEntry):
        super().__init__(title=f"Reminder: {tt_entry.name}")
        self.add_field(name=f"{tt_entry.description}", value="", inline=False)
        self.add_field(name="Time", value=f"{str(tt_entry.time)[:2]}:{str(tt_entry.time)[2:]}", inline=False)
        self.add_field(name="Duration", value=f"{tt_entry.duration} minutes", inline=False)
        self.add_field(name="ID", value=f"{tt_entry.tt_id}", inline=False)
        self.color = 0xFF0000


async def create_time_table_entry():
    message = ctx_mgr().get_init_context().message

    tt_entry = TimeTableEntry()
    tt_entry.generate_id()
    tt_entry.user_id = ctx_mgr().get_context_user_id()
    tt_entry.active = True
    tt_entry.ping = True

    for line in message.content.splitlines():
        if line.startswith("## time: "):
            tt_entry.time = int(line[8:].replace(":", ""))
        elif line.startswith("## days: "):
            tt_entry.days = 0
            for i, day in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
                if day in line:
                    tt_entry.days |= 1 << i
        elif line.startswith("## duration: "):
            tt_entry.duration = int(line[12:])
        elif line.startswith("# name: "):
            tt_entry.name = line[7:]
        elif line.startswith("- description: "):
            tt_entry.description = line[15:]

    if not tt_entry.check_valid():
        tt_entry_format = (
            "# name: <name>\n"
            "## time: <time>\n"
            "## days: <days>\n"
            "## duration: <duration>\n"
            "- description: <description>"
        )
        await send_message(
            content=f"ERROR: Invalid time table entry format\nPlease use the following format:\n{tt_entry_format}",
            mention_author=True,
        )
        return
    
    tt_entry.save()

    embed = TimeTableEntryDetailsEmbed(tt_entry)
    await send_message(embed=embed)


async def delete_time_table_entry(tt_id: str):
    tt_entry = TimeTableEntry()
    tt_entry.tt_id = tt_id
    tt_entry.delete()
    await send_message(content="Time Table Entry deleted.")


async def send_alert(bot: "Bot"):
    info("Send alert was called!")
    alert_channel_id = 1282659377437999185
    alert_channel = await get_channel(alert_channel_id, bot)

    current_time = get_time_frmt("%H%M")
    day = get_day(get_time())
    day = 1 << ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].index(day)
    query = "SELECT tt_id FROM Time_Table WHERE active = TRUE AND ping = TRUE AND days & %s = %s AND time = %s"
    result = Database.fetch_many(query, day, day, int(current_time))
    tt_ids = [row[0] for row in result]
    
    for tt_id in tt_ids:
        tt_entry = TimeTableEntry()
        tt_entry.tt_id = tt_id
        tt_entry.load()

        content = f"<@{tt_entry.user_id}> you have a time table alert!"
        embed = TimeTableEntryAlertEmbed(tt_entry)
        await alert_channel.send(content=content, embed=embed)  # type: ignore


