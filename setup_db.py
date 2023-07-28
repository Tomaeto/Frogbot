import sqlite3
from sqlite3 import Error
#Program for setting up database for Frogbot admin tasks
#Contains tables for user info, banned messages, and banned term list
#By Adrian Faircloth (Tomaeto)

#Function for connecting to database file/creating if none exists
def get_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    return conn

#Function for creating a table in the database, takes sql statement as arg
def make_table(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)
    
#Function for inserting sample entries into each table
def insert_sample_entries(conn):
    sql_member_entry = """ INSERT INTO members(id, username, join_date, status, banned_msg_count)
                                VALUES(181561413989302272, 'Tomaeto', '2022-04-27', 'Admin', 1);"""
    
    sql_bannedmsg_entry = """ INSERT INTO banned_msgs(user_id, msg_text, msg_date)
                                VALUES(181561413989302272, 'Fuck testing', '2023-07-25');"""
    
    sql_banterm_entry = """ INSERT INTO banned_terms(term) VALUES('fuck');"""

    cur = conn.cursor()
    cur.execute(sql_member_entry)
    cur.execute(sql_bannedmsg_entry)
    cur.execute(sql_banterm_entry)

#Main driver function
def main():
    db = './db/bot_db.db'

    #Statement for creating members table
    #Contains fields for user ID, username, date joined the server, date left the server, status in server, and banned message count
    sql_create_members_table = """ CREATE TABLE IF NOT EXISTS members (
                                    id integer PRIMARY KEY,
                                    username text NOT NULL,
                                    join_date text NOT NULL,
                                    leave_date text,
                                    status text,
                                    banned_msg_count integer
                                    );"""
    
    #Statement for creating banned message table
    #Contains fields for user id foreign key, message text, and message date
    sql_create_bannedmsg_table = """ CREATE TABLE IF NOT EXISTS banned_msgs (
                                        user_id integer,
                                        msg_text text NOT NULL,
                                        msg_date text,
                                        FOREIGN KEY (user_id) REFERENCES members(id)
                                        );"""
    
    #Statement for creating banned term list and adding uniqueness constraint
    sql_create_banlist_table = """ CREATE TABLE IF NOT EXISTS banned_terms (
                                        term text PRIMARY KEY UNIQUE
                                        );"""
    
    #Getting database connection
    conn = get_connection(db)
    if conn is None:
        print("Cannot create database connection")
        return
    
    #Creating tables and adding sample entries
    make_table(conn, sql_create_members_table)
    make_table(conn, sql_create_bannedmsg_table)
    make_table(conn, sql_create_banlist_table)
    insert_sample_entries(conn)
    conn.close()

#Running main function
main()
