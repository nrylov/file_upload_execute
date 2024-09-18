import time
import sqlite3
import os


# Handles saving the file
def filehandler(filename, file):
    insertfile(filename, file)
    savepath = f'\nYour link: http://127.0.0.1:5000/{filename}\n'
    return savepath


# handles inserting file into the database
def insertfile(filename, file):
    # connects to sqlite3 db
    db = sqlite3.connect('files.db')
    # finds current timestamp
    timestamp = int(time.time())
    try:
        # creates a db cursor
        cursor = db.cursor()
        # defines query
        sqlite_insert_blob_query = "INSERT INTO files (filename, date, file) VALUES (?, ?, ?)"

        # organizes data in a tuple
        data_tuple = (filename, timestamp, file)
        # executes query
        cursor.execute(sqlite_insert_blob_query, data_tuple)
        # saves changes
        db.commit()
        # closes cursor
        cursor.close()

    # handles errors
    except sqlite3.Error as error:
        print("Failed to insert data into sqlite table", error)
    # closes db when done
    finally:
        if db:
            db.close()


# handles getting files
def grabfile(id):
    try:
        # connects to db
        db = sqlite3.connect('files.db')
        cursor = db.cursor()
        # defines query
        sql_fetch_blob_query = "SELECT * from files where id = ?"
        # Executes the query
        cursor.execute(sql_fetch_blob_query, (id,))
        result = cursor.fetchone()
        cursor.close()
        # saves data to a dict
        file = {'id': result[0],
                'filename': result[1],
                'date': result[2],
                'file': result[3]}
        return file
        # return results

    except sqlite3.Error as error:
        print("Failed to get data from sqlite table", error)
    finally:
        if db:
            db.close()


# handles giving a file executable permissions
def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)

