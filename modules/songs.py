from typing import Optional, List

from discord import Interaction
from utils.random import generate_random_string
from utils.discord import ctx_mgr, get_files_from_message, send_message, BaseEmbed, File, BaseView
from database import Database
from io import BytesIO


class Song:
    def __init__(self):
        self.song_id: Optional[str] = None
        self.name: Optional[str] = None
        self.user_id: Optional[int] = None
        self.bytes: Optional[bytes] = None
        self.artist: Optional[str] = None
    
    def generate_id(self):
        while True:
            self.song_id = generate_random_string(12)
            try:
                query = f"SELECT song_id FROM songs WHERE song_id = %s"
                Database.fetch_one(query, self.song_id)
            except:
                break
    
    def save_song(self):
        assert self.song_id is not None
        assert self.name is not None
        assert self.user_id is not None
        assert self.bytes is not None
        assert self.artist is not None
        query = "INSERT INTO songs (song_id, name, user_id, bytes, artist) VALUES (%s, %s, %s, %s, %s)"
        Database.execute_query(query, self.song_id, self.name, self.user_id, self.bytes, self.artist)
    
    def load_song(self):
        assert self.song_id is not None
        query = "SELECT name, user_id, bytes, artist FROM songs WHERE song_id = %s"
        result = Database.fetch_one(query, self.song_id)
        self.name = result[0]
        self.user_id = result[1]
        self.bytes = result[2]
        self.artist = result[3]


class Playlist:
    def __init__(self):
        self.playlist_id: Optional[str] = None
        self.name: Optional[str] = None
        self.user_id: Optional[int] = None

        self.song_ids: List[str] = []
        self.songs: List[Song] = []
    
    def generate_id(self):
        while True:
            self.playlist_id = generate_random_string(12)
            try:
                query = f"SELECT playlist_id FROM playlist WHERE playlist_id = %s"
                Database.fetch_one(query, self.playlist_id)
            except:
                break
    
    def save_playlist(self):
        assert self.playlist_id is not None
        assert self.name is not None
        assert self.user_id is not None
        query = "INSERT INTO playlist (playlist_id, name, user_id) VALUES (%s, %s, %s)"
        Database.execute_query(query, self.playlist_id, self.name, self.user_id)
    
    def load_playlist(self):
        assert self.playlist_id is not None
        query = "SELECT name, user_id FROM playlist WHERE playlist_id = %s"
        result = Database.fetch_one(query, self.playlist_id)
        self.name = result[0]
        self.user_id = result[1]
    
    def load_song_ids(self):
        assert self.playlist_id is not None
        query = "SELECT song_id FROM playlist_songs WHERE playlist_id = %s"
        result = Database.fetch_many(query, self.playlist_id)
        self.song_ids = [row[0] for row in result]
    
    def load_songs(self):
        self.songs.clear()
        for song_id in self.song_ids:
            song = Song()
            song.song_id = song_id
            song.load_song()
            self.songs.append(song)
    
    def add_song_to_playlist(self, song_id: str):
        self.load_song_ids()
        if song_id in self.song_ids:
            return
        query = "INSERT INTO playlist_songs (playlist_id, song_id) VALUES (%s, %s)"
        Database.execute_query(query, self.playlist_id, song_id)
    
    def remove_song_from_playlist(self, song_id: str):
        self.load_song_ids()
        if song_id not in self.song_ids:
            return
        query = "DELETE FROM playlist_songs WHERE playlist_id = %s AND song_id = %s"
        Database.execute_query(query, self.playlist_id, song_id)


class SongEmbed(BaseEmbed):
    def __init__(self, song: Song):
        super().__init__(title="Song Details")
        assert song.bytes is not None
        self.add_field(name="Song ID", value=f"`{song.song_id}`")
        self.add_field(name="Name", value=f"{song.name}")
        self.add_field(name="Artist", value=f"{song.artist}")
        self.add_field(name="User ID", value=f"{song.user_id}")
        self.add_field(name="Bytes", value=f"{len(song.bytes)} bytes")


class PlaylistDetailsEmbed(BaseEmbed):
    def __init__(self, playlist: Playlist):
        super().__init__(title="Playlist Details")
        self.add_field(name="Playlist ID", value=f"`{playlist.playlist_id}`")
        self.add_field(name="Name", value=f"{playlist.name}")
        self.add_field(name="User ID", value=f"{playlist.user_id}")
        for i, id in enumerate(playlist.song_ids):
            self.add_field(name=f"Song {i+1}", value=f"`{id}`")


class PlaylistView(BaseView):
    def __init__(self, playlist: Playlist):
        self.playlist = playlist
        self.idx = 0
        super().__init__()
    
    def _add_items(self):
        disabled = self.idx == 0
        self._add_button(label="Previous", custom_id="previous", disabled=disabled)
        disabled = self.idx == len(self.playlist.songs) - 1
        self._add_button(label="Next", custom_id="next", disabled=disabled)
    
    async def _button_clicked(self, interaction: Interaction, custom_id: str) -> None:
        await interaction.response.defer()
        
        if custom_id == "previous":
            self.idx -= 1
        elif custom_id == "next":
            self.idx += 1
        else:
            raise ValueError(f"Invalid custom_id: {custom_id}")
        
        await self.update_view()
    
    async def get_embed_files(self):
        embed = SongEmbed(self.playlist.songs[self.idx])
        song_bytes = self.playlist.songs[self.idx].bytes
        assert song_bytes is not None
        song_bytes = BytesIO(song_bytes)
        file = File(song_bytes, f"{self.playlist.songs[self.idx].name}.mp3")
        return embed, [file]
    

async def add_song(*args: str):
    song = Song()
    song.generate_id()
    song.user_id = ctx_mgr().get_context_user_id()
    song_details = " ".join(args)
    song.name = song_details.split("by")[0].strip()
    song.artist = song_details.split("by")[1].strip()

    message = ctx_mgr().get_init_context().message
    files = await get_files_from_message(message)
    if len(files) != 1:
        content = "Please upload only one file."
        await send_message(content=content)
        return
    song.bytes = list(files.values())[0].getvalue()
    song.save_song()

    embed = SongEmbed(song)
    await send_message(embed=embed)


async def get_song(song_id: str):
    song = Song()
    song.song_id = song_id
    song.load_song()

    embed = SongEmbed(song)
    assert song.bytes is not None
    file = File(BytesIO(song.bytes), f"{song.name}.mp3")
    await send_message(embed=embed, file=file)


async def create_playlist(*args: str):
    playlist = Playlist()
    playlist.generate_id()
    playlist.user_id = ctx_mgr().get_context_user_id()
    playlist.name = " ".join(args)
    playlist.save_playlist()
    
    assert playlist.playlist_id is not None
    await get_playlist(playlist.playlist_id)


async def get_playlist(playlist_id: str):
    playlist = Playlist()
    playlist.playlist_id = playlist_id
    playlist.load_playlist()
    playlist.load_song_ids()
    playlist.load_songs()

    embed = PlaylistDetailsEmbed(playlist)
    await send_message(embed=embed)


async def add_song_to_playlist(playlist_id: str, song_id: str):
    playlist = Playlist()
    playlist.playlist_id = playlist_id
    playlist.add_song_to_playlist(song_id)

    await get_playlist(playlist_id)


async def remove_song_from_playlist(playlist_id: str, song_id: str):
    playlist = Playlist()
    playlist.playlist_id = playlist_id
    playlist.remove_song_from_playlist(song_id)

    await get_playlist(playlist_id)


async def play_playlist(playlist_id: str):
    playlist = Playlist()
    playlist.playlist_id = playlist_id
    playlist.load_playlist()
    playlist.load_song_ids()
    playlist.load_songs()

    view = PlaylistView(playlist)
    await view.send()

