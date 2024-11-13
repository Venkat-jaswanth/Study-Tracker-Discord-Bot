from utils.context_manager import ctx_mgr
from utils.discord import send_message, get_files_from_message, BaseEmbed, BaseView
from utils.random import generate_random_string
from database import Database
from utils.general import get_time
import time


def epoch_to_date(epoch):
    # Assuming the input is in milliseconds, convert to seconds
    if epoch is None:
        return
    return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch / 1000)))

def date_to_epoch(date: str):
    if date is None:
        return
    from dateutil.parser import parse

    return int(parse(date).timestamp() * 1000)

def date_to_epoch(date: str):
    if date is None:
        return
    from dateutil.parser import parse

    return int(parse(date).timestamp() * 1000)
    



'''CREATE TABLE Tasks("
        "task_id BIGINT PRIMARY KEY,"
        "user_id BIGINT NOT NULL,"
        "name VARCHAR(128) NOT NULL,"
        "description TEXT,"
        "status VARCHAR(32),"
        "due_date BIGINT,"
        "completion_time BIGINT,"
        "FOREIGN KEY (user_id) REFERENCES Users(user_id)"
        ")'''

class Task:
    
    def __init__(self,name="",task_id=0,description=None,status="pending",due_date=None,completion_time=None):
        self.user_id= ctx_mgr().get_context_user_id()
        self.task_id = task_id
        self.name = name
        self.description = description
        self.status = status
        self.due_date = due_date
        self.completion_time = completion_time
        

    def add_task(self):
        query = ("INSERT INTO Tasks(user_id,name,description,status,due_date,completion_time) VALUES(%s,%s,%s,%s,%s,%s)")
        Database.execute_query(query,self.user_id,self.name,self.description,self.status,self.due_date,self.completion_time)

    def list_tasks(self):
        query = ("SELECT * FROM Tasks WHERE user_id=%s ORDER BY task_id")
        tasks = Database.fetch_many(query,self.user_id)
        return tasks
    
    def mark_as_done(self):
        query = ("UPDATE Tasks SET status='done' WHERE task_id=%s and user_id=%s")
        Database.execute_query(query, self.task_id, self.user_id)
        completion_time = get_time()
        query = ("UPDATE Tasks SET completion_time=%s WHERE task_id=%s and user_id=%s")
        Database.execute_query(query, completion_time, self.task_id, self.user_id)

    def mark_as_started(self):
        query = ("UPDATE Tasks SET status='started' WHERE task_id=%s and user_id=%s")
        Database.execute_query(query, self.task_id, self.user_id)

    def delete_task(self):
        query = ("DELETE FROM Tasks WHERE task_id=%s and user_id=%s")
        Database.execute_query(query, self.task_id, self.user_id)



async def list_tasks():
    tasks = Task().list_tasks()
    embed = BaseEmbed(title="Tasks")
    for task in tasks:
        embed.add_field(
            name=task[2],
            value=(
            f"task number: {task[0]}\n"
            f"Description: {task[3]}\n"
            f"Status: {task[4]}\n"
            f"Due Date: {epoch_to_date(task[5])}\n"
            f"Completion Time: {epoch_to_date(task[6])}"
            )
        )
    await send_message(embed=embed)

async def add_task(name:str):
    try:
        query = ("SELECT user_id FROM Users WHERE user_id=%s")
        Database.fetch_one(query, ctx_mgr().get_context_user_id())
        Task(name=name).add_task()
        await send_message(content="Task added successfully")
    except Exception as e:
        await send_message(content="Task addition failed.Please register first")

async def remove_task(task_id):
    try:
        Task(task_id=task_id).delete_task()
        await send_message(content="Task removed successfully")
    except Exception as e:
        await send_message(content="Task removal failed. Task not found")

async def add_description(task_id, description):
    query = ("UPDATE Tasks SET description=%s WHERE task_id=%s")
    Database.execute_query(query, description, task_id)

async def mark_as_done(task_id):
    try:
        Task(task_id=task_id).mark_as_done()
        await send_message(content="Task marked as done")
    except Exception as e:
        await send_message("Task not found")

async def mark_as_started(task_id):
    try:
        Task(task_id=task_id).mark_as_started()
        await send_message(content="Task marked as started")
    except Exception as e:
        await send_message(content="Task not found")

async def set_due_date(task_id:int, due_date:str):
    try:
        due_date = date_to_epoch(due_date)
        query = ("UPDATE Tasks SET due_date=%s WHERE task_id=%s")
        Database.execute_query(query, due_date, task_id)
    except Exception as e:
        await send_message(content="Task not found")
    






