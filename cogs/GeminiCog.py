from config import Gemini_API_Key
from discord.ext import commands
import google.generativeai as genai
import time

helpContext='''
Below is the list of available commands

Study Tracker Commands

Flashcard Commands
- $add_flashcard 
    {message} (message should be in a new line)
  Adds a new flashcard. Message format should be
# Q: <question 256 chars>
## A: <answer 256 chars>
- <option1 256 chars>
- <option2 256 chars>
- <option3>
 Always give atleast 2 options and try to give 3 options

- $list_flashcards  
  Lists all flashcards. No arguments required.
- $flashcard_flash {card_id}  
  Flashes a specific flashcard by ID. Takes one argument: card_id.
- $flashcard_create_set {set_name}
  Creates a new flashcard set. Takes one argument: <set_name>
- $flashcard_add_to_set {set_id} {card_id}
  Adds a flashcard to a set by ID. Takes two arguments: set_id, card_id.
- $flashcard_remove_from_set {set_id} {card_id}
  Removes a flashcard from a set by ID. Takes two arguments: set_id, card_id.
- $flashcard_review_set {set_id}
  Reviews a flashcard set by ID. Takes one argument: set_id.

Task Management Commands
- $add_task {name}  
  Adds a new task with a specified name. Takes one argument: name.
- $set_task {name}  
  Sets the current task by name. Takes one argument: name.
- $set_task_by_id {id}  
  Sets the current task by ID. Takes one argument: id.
- $add_description {description}  
  Adds a description to the current task. Takes one argument: description.
- $list_tasks  
  Lists all tasks. No arguments required.
- $remove_task {name}  
  Removes a task by name. Takes one argument: name.
- $delete_task {id}  
  Deletes a task by ID. Takes one argument: id.Also called task number
- $mark_as_done {name}  
  Marks a task as done by name. Takes one argument: name.
- $mark_as_started {name}  
  Marks a task as started by name. Takes one argument: name.
- $mark_as_started_by_id {id}  
  Marks a task as started by ID. Takes one argument: id.
- $mark_as_done_by_id {id}  
  Marks a task as done by ID. Takes one argument: id.
- $set_due_date {due_date}  
  Sets a due date for the current task. Takes one argument: due_date (format: YYYY-MM-DD HH:MM:SS).

Music Commands
- $add_song {message}  
  Adds a new song. Message format should be 'Song Name by Artist.
  For example: despacito by justin bieber
  An attachment containing an audio file(mp3) should be sent with the message
- $get_song {song_id}  
  Retrieves a song by ID. Takes one argument: song_id.
- $create_playlist {playlist_name}  
  Creates a new playlist. Takes the name of the playlist.
- $get_playlist {playlist_id}  
  Retrieves a playlist by ID. Takes one argument: playlist_id.
- $add_song_to_playlist {playlist_id} {song_id}  
  Adds a song to a playlist by song ID and playlist ID. Takes two arguments: playlist_id, song_id.
- $remove_song_from_playlist {playlist_id} {song_id}  
  Removes a song from a playlist by song ID and playlist ID. Takes two arguments: playlist_id, song_id.
- $play_playlist {playlist_id}  
  Plays a playlist by ID. Takes one argument: playlist_id.

Time Table Management Commands
- $create_time_table_entry {message}
  Adds a new time table entry. Message format should be
  # name: <name>
  ## time: <time>
  ## days: <day>(day should be first three letters of the word with first letter in capital.E.g. Mon)
  ## duration: <duration>(an integer in minutes)
  - description: <description>
-$delete_time_table_entry {tt_id}
  Removes a time table entry by ID. Takes one argument: tt_id.


General Purpose Commands
- $ping  
  Responds with 'Pong!' and alternates messages. No arguments required.
- $query {question}  
  Queries the Gemini API with your question and returns a response. Takes one argument: question.
- $pm  
  Sends a private message to you asking how the bot can help and you can talk to it. No arguments required.
- $gemini enable  
  Enables Gemini to respond to every message in the server. No arguments required.
- $gemini disable  
  Disables Gemini from responding to every message in the server. No arguments required.
- $register {name}  
  Registers a new user. Takes the name of the user
- $set_institution {institution}
  Sets the institution of the user. Takes the name of the institution
- $set_dob {dob}
  Sets the date of birth of the user. Takes the date of birth in the format DD MM YYYY
- !help {question}  
  To ask a question related to the commands to the bot. Takes one optional argument: question.
'''


genai.configure(api_key=Gemini_API_Key)
DISCORD_MAX_MESSAGE_LENGTH=2000
PLEASE_TRY_AGAIN_ERROR_MESSAGE='There was an issue with your question please try again.. '
Gemini=False
first_time=True
class GeminiAgent(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
        self.model = genai.GenerativeModel('gemini-pro')

    @commands.Cog.listener()
    async def on_message(self,msg):
        try:
            if msg.content == "ping gemini-agent":
                await msg.channel.send("Agent is connected..")
            elif msg.content[:5] == "!help":
                 prompt=msg.content[5:]
                 global helpContext
                 response = self.gemini_generate_content(helpContext+prompt)
                 await self.send_message_in_chunks(msg.channel,response)
            elif 'Direct Message' in str(msg.channel) and not msg.author.bot:
                response = self.gemini_generate_content(msg.content)
                dmchannel = await msg.author.create_dm()
                await self.send_message_in_chunks(dmchannel,response) 
                global first_time
            elif(not msg.author.bot and Gemini):
                if first_time:
                    await msg.channel.send('Hi, I am Gemini Agent. How can I help you today?')
                    first_time=False
                else:
                    if(msg.content[0]!='$'):
                        response = self.gemini_generate_content(msg.content)
                        await self.send_message_in_chunks(msg.channel,response) 
        except Exception as e:
            await msg.channel.send("There was an error from serverside.. Please try again..")
        

    @commands.command()
    async def query(self,ctx,*,question):
        try:
            response = self.gemini_generate_content(question)
            await self.send_message_in_chunks(ctx,response)
            
        except Exception as e:
            await ctx.send("There was an error from serverside.. Please try again..")
    
    @commands.group()
    async def gemini(self,ctx):
        pass

    @gemini.command()
    async def enable(self,ctx):
        global Gemini,first_time
        Gemini=True
        await ctx.send('Gemini Agent is enabled..')
    
    @gemini.command()
    async def disable(self,ctx):
        global Gemini,first_time
        Gemini=False
        first_time=True
        await ctx.send('Gemini Agent is disabled..')

    @commands.command()
    async def pm(self,ctx):
        dmchannel = await ctx.author.create_dm()
        await dmchannel.send('Hi how can I help you today?')

    def gemini_generate_content(self, content, retries=4, delay=2):
        attempt = 0
        while attempt < retries:
            try:
                response = self.model.generate_content(content, stream=True)
                return response
            except Exception as e:
                print(f"Attempt {attempt + 1}: error in gemini_generate_content:", e)
                if attempt < retries - 1:
                    time.sleep(delay)
                attempt += 1
                return PLEASE_TRY_AGAIN_ERROR_MESSAGE + str(e)
        
    async def send_message_in_chunks(self,ctx,response):
        message = ""
        for chunk in response:
            message += chunk.text
            if len(message) > DISCORD_MAX_MESSAGE_LENGTH:
                extraMessage = message[DISCORD_MAX_MESSAGE_LENGTH:]
                message = message[:DISCORD_MAX_MESSAGE_LENGTH]
                await ctx.send(message)
                message = extraMessage
        if len(message) > 0:
            while len(message) > DISCORD_MAX_MESSAGE_LENGTH:
                extraMessage = message[DISCORD_MAX_MESSAGE_LENGTH:]
                message = message[:DISCORD_MAX_MESSAGE_LENGTH]
                await ctx.send(message)
                message = extraMessage
            await ctx.send(message)
