from database import Database


def main():
    Database().establish_connection()
    
    table_list = ["Users", "Tasks", "Time_Table", "Time_Table_Status", "Focus_Mode", "Songs", "Playlist", "Playlist_Songs", "Flashcard", "Flashcard_Set", "Flashcard_set_access", "Flashcard_Set_Cards", "Flashcard_History"]
    
    for table in table_list:
            query = ("DROP TABLE IF EXISTS " + table + " CASCADE")
            Database.execute_query(query)
    
    # Create Relations
    #Create Tables
    
    query = ("CREATE TABLE Users("
             "user_id BIGINT PRIMARY KEY,"
             "name VARCHAR(64) NOT NULL,"
             "join_date BIGINT NOT NULL,"
             "dob BIGINT,"
             "institution VARCHAR(256),"
             "time_zone SMALLINT"
             ")")
    Database.execute_query(query)
    
    query = ("CREATE TABLE Tasks("
         "task_id SERIAL PRIMARY KEY,"
         "user_id BIGINT NOT NULL,"
         "name VARCHAR(128) NOT NULL,"
         "description TEXT,"
         "status VARCHAR(32),"
         "due_date BIGINT,"
         "completion_time BIGINT,"
         "FOREIGN KEY (user_id) REFERENCES Users(user_id)"
         ")")
    
    Database.execute_query(query)
    
    query = ("CREATE TABLE Time_Table("
         "tt_id VARCHAR(12) PRIMARY KEY,"
         "user_id BIGINT NOT NULL,"
         "name VARCHAR(128) NOT NULL,"
         "description TEXT,"
         "days SMALLINT NOT NULL,"
         "time SMALLINT NOT NULL,"
         "duration SMALLINT,"
         "ping BOOLEAN NOT NULL,"
         "active BOOLEAN NOT NULL,"
         "FOREIGN KEY (user_id) REFERENCES Users(user_id)"
         ")")
    
    Database.execute_query(query)
    
    query = ("CREATE TABLE Time_Table_Status("
         "tt_id VARCHAR(12) NOT NULL,"
         "time BIGINT NOT NULL,"
         "status VARCHAR(32),"
         "PRIMARY KEY (tt_id, time),"
         "FOREIGN KEY (tt_id) REFERENCES Time_Table(tt_id)"
         ")")
    
    Database.execute_query(query)
    
    
    query = ("CREATE TABLE Focus_Mode("
         "user_id BIGINT,"
         "start_time BIGINT NOT NULL,"
         "duration BIGINT NOT NULL,"
         "PRIMARY KEY (user_id, start_time),"
         "FOREIGN KEY (user_id) REFERENCES Users(user_id)"
         ")")
    
    Database.execute_query(query)
    
    
    query = ("CREATE TABLE Songs("
      "song_id VARCHAR(12) PRIMARY KEY,"
      "user_id BIGINT NOT NULL,"
      "name VARCHAR(128) NOT NULL,"
      "bytes bytea NOT NULL,"
      "artist VARCHAR(64) NOT NULL,"
      "FOREIGN KEY (user_id) REFERENCES Users(user_id)"
      ")")
    
    Database.execute_query(query)
    
    query = ("CREATE TABLE Playlist("
         "playlist_id VARCHAR(12) PRIMARY KEY,"
         "user_id BIGINT NOT NULL,"
         "name VARCHAR(128) NOT NULL,"
         "FOREIGN KEY (user_id) REFERENCES Users(user_id)"
         ")")
    
    Database.execute_query(query)
    
    query = ("CREATE TABLE Playlist_Songs("
         "playlist_id VARCHAR(12),"
         "song_id VARCHAR(12),"
         "PRIMARY KEY (playlist_id, song_id),"
         "FOREIGN KEY (playlist_id) REFERENCES Playlist(playlist_id),"
         "FOREIGN KEY (song_id) REFERENCES Songs(song_id)"
         ")")
    
    Database.execute_query(query)
    
    query = ("CREATE TABLE Flashcard("
         "card_id VARCHAR(12) PRIMARY KEY,"
         "user_id BIGINT NOT NULL,"
         "question TEXT NOT NULL,"
         "options TEXT[],"
         "answer TEXT,"
         "image BYTEA,"
         "FOREIGN KEY (user_id) REFERENCES Users(user_id)"
         ")")
    
    Database.execute_query(query)
    
        
    query = ("CREATE TABLE Flashcard_Set("
         "card_set_id VARCHAR(12) PRIMARY KEY,"
         "name VARCHAR(128) NOT NULL,"
         "owner BIGINT NOT NULL,"
         "description TEXT,"
         "FOREIGN KEY (owner) REFERENCES Users(user_id)"
         ")")
    
    Database.execute_query(query)
    
    query = ("CREATE TABLE Flashcard_set_access("
           "card_set_id VARCHAR(12),"
           "user_id BIGINT,"
           "PRIMARY KEY (card_set_id, user_id),"
           "FOREIGN KEY (card_set_id) REFERENCES Flashcard_Set(card_set_id),"
           "FOREIGN KEY (user_id) REFERENCES Users(user_id)"
             ")")
    
    Database.execute_query(query)
    
    query = ("CREATE TABLE Flashcard_Set_Cards("
         "card_set_id VARCHAR(12),"
         "card_id VARCHAR(12),"
         "added_by BIGINT NOT NULL,"
         "PRIMARY KEY (card_set_id, card_id),"
         "FOREIGN KEY (card_set_id) REFERENCES Flashcard_Set(card_set_id),"
         "FOREIGN KEY (card_id) REFERENCES Flashcard(card_id)"
         ")")
    
    Database.execute_query(query)
    
    query = ("CREATE TABLE Flashcard_History("
         "card_id VARCHAR(12),"
         "user_id BIGINT,"
         "time BIGINT,"
         "correct BOOLEAN,"
         "PRIMARY KEY (card_id, user_id, time),"
         "FOREIGN KEY (card_id) REFERENCES Flashcard(card_id),"
         "FOREIGN KEY (user_id) REFERENCES Users(user_id)"
         ")")
    
    Database.execute_query(query)

    Database().terminate_connection()


if __name__ == '__main__':
    main()
