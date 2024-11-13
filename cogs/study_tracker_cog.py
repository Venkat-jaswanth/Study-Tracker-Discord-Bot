from discord.ext import commands, tasks
from discord.ext.commands import command, Bot, Cog, Context  # type: ignore
from discord import Embed
from typing import Any
from logging import info, error as err
from database.database import Database
from utils.context_manager import ctx_mgr

current_task_id=None
class StudyTrackerCog(Cog):
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.task_reminder.start()
        info("StudyTrackerCog has been loaded.")

    async def cog_command_error(self, ctx: Context[Any], error: Exception) -> None:
        if isinstance(error, commands.CheckFailure):
            return
        err(f"An excpetion occured: {error}", exc_info=True)
        # await ctx.reply(f"ERROR: {type(error)} {error}")
    
    @command(name="ping")
    async def ping(self, ctx: Context[Bot]):
        ctx_mgr().set_init_context(ctx)
        
        from asyncio import sleep
        from utils.discord import send_message, BaseEmbed

        embed1 = BaseEmbed(title="Ping!")
        await send_message(content="Pong!", embed=embed1)
        await sleep(3)
        embed2 = BaseEmbed(title="Pong!")
        await send_message(content="Ping!", embed=embed2)
        await sleep(3)
        embed3 = BaseEmbed(title="Ping!")
        await send_message(content="Pong!", embed=embed3)
    
    @command(name="register")
    async def register(self, ctx: Context[Bot], *args: str):
        from modules.user import register_user

        ctx_mgr().set_init_context(ctx)
        await register_user(*args)
    
    @command(name="set_institution")
    async def set_institution(self, ctx: Context[Bot], *args: str):
        from modules.user import set_institution

        ctx_mgr().set_init_context(ctx)
        try:
            query = ("SELECT user_id FROM Users WHERE user_id=%s")
            Database.fetch_one(query, ctx_mgr().get_context_user_id())
            await set_institution(*args)
        except Exception as e:
            await ctx.send("User not found. Please register first.")
    
    @command(name="set_time_zone")
    async def set_time_zone(self, ctx: Context[Bot], time_zone: str):
        from modules.user import set_time_zone

        ctx_mgr().set_init_context(ctx)
        try:
            query = ("SELECT user_id FROM Users WHERE user_id=%s")
            Database.fetch_one(query, ctx_mgr().get_context_user_id())
            await set_time_zone(time_zone)
        except Exception as e:
            await ctx.send("User not found. Please register first.")
    
    @command(name="set_dob")
    async def set_dob(self, ctx: Context[Bot], *args: str):
        from modules.user import set_dob

        ctx_mgr().set_init_context(ctx)
        try:
            query = ("SELECT user_id FROM Users WHERE user_id=%s")
            Database.fetch_one(query, ctx_mgr().get_context_user_id())
            await set_dob(*args)
        except Exception as e:
            await ctx.send("User not found. Please register first.")
       

    @command(name="add_flashcard")
    async def add_flashcard(self, ctx: Context[Bot]):
        from modules.flashcards import add_flashcard
        
        ctx_mgr().set_init_context(ctx)
        try:
            query = ("SELECT user_id FROM Users WHERE user_id=%s")
            Database.fetch_one(query, ctx_mgr().get_context_user_id())
            await add_flashcard()
        except Exception as e:
            await ctx.send("User not found. Please register first.")
    
    @command(name="list_flashcards")
    async def list_flashcards(self, ctx: Context[Bot]):
        from modules.flashcards import list_flashcards
        
        ctx_mgr().set_init_context(ctx)
        await list_flashcards()
    
    @command(name="flashcard_flash")
    async def flashcard_flash(self, ctx: Context[Bot], card_id: str):
        from modules.flashcards import flashcard_flash
        
        ctx_mgr().set_init_context(ctx)
        await flashcard_flash(card_id)

    @command(name="flashcard_create_set")
    async def flashcard_create(self, ctx: Context[Bot], set_name: str):
        from modules.flashcards import flashcard_create_set
        try:
            ctx_mgr().set_init_context(ctx)
            query = ("SELECT user_id FROM Users WHERE user_id=%s")
            Database.fetch_one(query, ctx_mgr().get_context_user_id())
            await flashcard_create_set(set_name)
        except Exception as e:
            await ctx.send("User not found. Please register first.")
    
    @command(name="flashcard_add_to_set")
    async def flashcard_add_to_set(self, ctx: Context[Bot], set_id: str, card_id: str):
        from modules.flashcards import flashcard_add_to_set

        ctx_mgr().set_init_context(ctx)
        await flashcard_add_to_set(set_id, card_id)

    @command(name="flashcard_remove_from_set")
    async def flashcard_remove_from_set(self, ctx: Context[Bot], set_id: str, card_id: str):
        from modules.flashcards import flashcard_remove_from_set

        ctx_mgr().set_init_context(ctx)
        await flashcard_remove_from_set(set_id, card_id)
    
    @command(name="flashcard_review_set")
    async def flashcard_review_set(self, ctx: Context[Bot], set_id: str):
        from modules.flashcards import flashcard_review_set

        ctx_mgr().set_init_context(ctx)
        await flashcard_review_set(set_id)
    
    @command(name="add_task")
    async def add_task(self, ctx: Context[Bot],*,name=""):
        if name.strip() == "":
            await ctx.send("Please provide a task name")
            return
        from modules.tasks import add_task
        ctx_mgr().set_init_context(ctx)
        await add_task(name=name)

        
    @command(name="set_task")
    async def set_current_task(self, ctx: Context[Bot],*,name: str):
        query=("SELECT task_id FROM Tasks WHERE name=%s")
        id=Database.fetch_one(query,name)
        global current_task_id
        current_task_id=id
        await ctx.send(f"Current task set to name: {name}, id: {current_task_id}")

    @command(name="set_task_by_id")
    async def settask(self, ctx: Context[Bot], *, id):
        query=("SELECT name FROM Tasks WHERE task_id=%s")
        name=Database.fetch_one(query,id)
        global current_task_id
        current_task_id = id
        await ctx.send(f"Current task set to name: {name}, id: {current_task_id}")
     

    @command(name="add_description")
    async def add_description(self, ctx: Context[Bot],*, description: str):
        from modules.tasks import add_description
        id=current_task_id
        if(id==None):
            await ctx.send("Please set the  task.")
            await ctx.send("Use set_task <task_name> or set_task_by_id <task_id>")
        ctx_mgr().set_init_context(ctx)
        await add_description(id, description)

    @command(name="list_tasks")
    async def list_tasks(self, ctx: Context[Bot]):
        from modules.tasks import list_tasks
        
        ctx_mgr().set_init_context(ctx)
        await list_tasks()
    
    @command(name="remove_task")
    async def remove_task(self, ctx: Context[Bot],*,name: str):
        from modules.tasks import remove_task
        try:
            query=("SELECT task_id FROM Tasks WHERE name=%s")
            id=Database.fetch_one(query,name)
            ctx_mgr().set_init_context(ctx)
            await remove_task(id)
        except Exception as e:
            await ctx.send("Task not found")
            

    @command(name="delete_task")
    async def delete_task(self, ctx: Context[Bot],*,id):
        from modules.tasks import remove_task

        ctx_mgr().set_init_context(ctx)
        await remove_task(id)

    @command(name="mark_as_done")
    async def mark_as_done(self, ctx: Context[Bot],*,name: str):
        from modules.tasks import mark_as_done
        try:
            query=("SELECT task_id FROM Tasks WHERE name=%s")
            id=Database.fetch_one(query,name)
            ctx_mgr().set_init_context(ctx)
            await mark_as_done(id)
        except Exception as e:
            await ctx.send("Task not found")


    @command(name="mark_as_started")
    async def mark_as_started(self, ctx: Context[Bot],*,name: str):
        from modules.tasks import mark_as_started
        try:
            query=("SELECT task_id FROM Tasks WHERE name=%s")
            id=Database.fetch_one(query,name)
            ctx_mgr().set_init_context(ctx)
            await mark_as_started(id)    
        except Exception as e:
            await ctx.send("Task not found")
            return


    @command(name="mark_as_started_by_id")
    async def mark_as_started_by_id(self, ctx: Context[Bot],*,id: str):
        from modules.tasks import mark_as_started
        
        ctx_mgr().set_init_context(ctx)
        await mark_as_started(id)
    
    @command(name="mark_as_done_by_id")
    async def mark_as_done_by_id(self, ctx: Context[Bot],*,id: str):
        from modules.tasks import mark_as_done
        
        ctx_mgr().set_init_context(ctx)
        await mark_as_done(id)

    @command(name="set_due_date")
    async def set_due_date(self, ctx: Context[Bot],*,due_date: str):
        from modules.tasks import set_due_date
        id=current_task_id
        if(id==None):
            await ctx.send("Please set the  task.")
            await ctx.send("Use set_task <task_name> or set_task_by_id <task_id>")
        ctx_mgr().set_init_context(ctx)
        await set_due_date(id, due_date)
    
    @command(name="add_song")
    async def add_song(self, ctx: Context[Bot], *args: str):
        from modules.songs import add_song

        ctx_mgr().set_init_context(ctx)
        try:
            query = ("SELECT user_id FROM Users WHERE user_id=%s")
            Database.fetch_one(query, ctx_mgr().get_context_user_id())
            await add_song(*args)
        except Exception as e:
            await ctx.send("User not found. Please register first.")
    
    @command(name="get_song")
    async def get_song(self, ctx: Context[Bot], song_id: str):
        from modules.songs import get_song

        ctx_mgr().set_init_context(ctx)
        await get_song(song_id)
    
    @command(name="create_playlist")
    async def create_playlist(self, ctx: Context[Bot], *args: str):
        from modules.songs import create_playlist

        ctx_mgr().set_init_context(ctx)
        try:
            query = ("SELECT user_id FROM Users WHERE user_id=%s")
            Database.fetch_one(query, ctx_mgr().get_context_user_id())
            await create_playlist(*args)
        except Exception as e:
            await ctx.send("User not found. Please register first.")
    
    @command(name="get_playlist")
    async def get_playlist(self, ctx: Context[Bot], playlist_id: str):
        from modules.songs import get_playlist

        ctx_mgr().set_init_context(ctx)
        await get_playlist(playlist_id)

    @command(name="add_song_to_playlist")
    async def add_song_to_playlist(self, ctx: Context[Bot], playlist_id: str, song_id: str):
        from modules.songs import add_song_to_playlist

        ctx_mgr().set_init_context(ctx)
        await add_song_to_playlist(playlist_id, song_id)
    
    @command(name="remove_song_from_playlist")
    async def remove_song_from_playlist(self, ctx: Context[Bot], playlist_id: str, song_id: str):
        from modules.songs import remove_song_from_playlist

        ctx_mgr().set_init_context(ctx)
        await remove_song_from_playlist(playlist_id, song_id)

    @command(name="play_playlist")
    async def play_playlist(self, ctx: Context[Bot], playlist_id: str):
        from modules.songs import play_playlist

        ctx_mgr().set_init_context(ctx)
        await play_playlist(playlist_id)
    
    @command(name="create_time_table_entry")
    async def create_time_table_entry(self, ctx: Context[Bot]):
        from modules.time_table import create_time_table_entry

        ctx_mgr().set_init_context(ctx)
        try:
            query = ("SELECT user_id FROM Users WHERE user_id=%s")
            Database.fetch_one(query, ctx_mgr().get_context_user_id())
            await create_time_table_entry()
        except Exception as e:
            await ctx.send("User not found. Please register first.")
    
    @command(name="delete_time_table_entry")
    async def delete_time_table_entry(self, ctx: Context[Bot], entry_id: str):
        from modules.time_table import delete_time_table_entry

        ctx_mgr().set_init_context(ctx)
        await delete_time_table_entry(entry_id)
    
    @tasks.loop(seconds=60)
    async def task_reminder(self):
        from modules.time_table import send_alert

        await send_alert(self.bot)

    @command(name="help1")
    async def help1_command(self, ctx: Context[Bot]):
        embed = Embed(title="Study Tracker Commands", description="List of available commands and their usage", color=0x00ff00)

        commands_info = {
            
            "ping": "Responds with 'Pong!' and alternates messages.",
            "add_flashcard": "Adds a new flashcard.",
            "list_flashcards": "Lists all flashcards.",
            "flashcard_flash": "Flashes a specific flashcard by ID.",
            "flashcard_create_set": "Creates a new flashcard set given the name.",
            "flashcard_add_to_set": "Adds a flashcard to a set give the set_id & card_id.",
            "flashcard_remove_from_set": "Removes a flashcard from a set given the set_id & card_id.",
            "flashcard_review_set": "Reviews a flashcard set given the set_id.",
            "add_task": "Adds a new task with a specified name.",
            "set_task": "Sets the current task by name.",
            "set_task_by_id": "Sets the current task by ID.",
            "add_description": "Adds a description to the current task.",
            "list_tasks": "Lists all tasks.",
            "remove_task": "Removes a task by name.",
            "delete_task": "Deletes a task by ID.",
            "mark_as_done": "Marks a task as done by name.",
            "mark_as_started": "Marks a task as started by name.",
            "mark_as_started_by_id": "Marks a task as started by ID.",
            "mark_as_done_by_id": "Marks a task as done by ID.",
            "set_due_date": "Sets a due date for the current task.",
        }

        for command_name, description in commands_info.items():
            embed.add_field(name=f"${command_name}", value=description, inline=False)

        await ctx.send(embed=embed)
    
    @command(name="help2")
    async def help2_command(self, ctx: Context[Bot]):
        embed = Embed(title="Study Tracker Commands", description="List of available commands and their usage", color=0x00ff00)

        commands_info = {
            "add_song": "Adds a song to the database given name in the format: 'Song Name by Artist Name'",
            "get_song": "Gets a song by ID.",
            "create_playlist": "Creates a playlist given a name.",
            "get_playlist": "Gets a playlist by ID.",
            "add_song_to_playlist": "Adds a song to a playlist given the playlist_id & song_id.",
            "remove_song_from_playlist": "Removes a song from a playlist given the playlist_id & song_id.",
            "play_playlist": "Plays a playlist given the playlist_id.",
            "create_time_table_entry": "Creates a new time table entry.",
            "delete_time_table_entry": "Deletes a time table entry given the entry_id.",
            "query": "Queries the Gemini API with your question and returns a response.",
            "pm": "Sends a private message to you asking how the bot can help and you can talk to it.",
            "gemini enable": "Enables Gemini to respond to every message in the server.",
            "gemini disable": "Disables Gemini from responding to every message in the server.",
        }

        for command_name, description in commands_info.items():
            embed.add_field(name=f"${command_name}", value=description, inline=False)

        await ctx.send(embed=embed)
 
