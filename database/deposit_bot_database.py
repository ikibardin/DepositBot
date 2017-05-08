import sqlite3

from telebot import types

import events
import windows
from bank import Bank
from database.converter import Converter
import database.db_paths as paths


class SQLDatabase:
    def __init__(self, bot, db_name):
        self._bot = bot
        self.db_name = db_name
        self.connection = sqlite3.connect(db_name,
                                          detect_types=sqlite3.PARSE_DECLTYPES)
        self.connection.row_factory = sqlite3.Row
        self.converter = Converter(self)
        sqlite3.register_adapter(bool, int)
        sqlite3.register_converter('BOOLEAN', lambda v: int(v) == 1)

    def setup(self):
        with open(paths.SETUP, 'r') as setup_script:
            query = setup_script.read()
        with self.connection:
            self.connection.executescript(query)

    def insert_new_user(self, user):
        with open(paths.INSERT_USER, 'r') as insert_user_script:
            query = insert_user_script.read()
        with self.connection:
            self.connection.execute(query, self.converter.user_to_row(user))

    def insert_new_chat(self, chat):
        with open(paths.INSERT_CHAT, 'r') as insert_chat_script:
            query = insert_chat_script.read()
        with self.connection:
            self.connection.execute(query, self.converter.chat_to_row(chat))

    def insert_new_bank(self, chat, owner):
        if owner.id not in [user.id for user in self.get_users_list()]:
            self.insert_new_user(owner)
        with open(paths.INSERT_BANK, 'r') as insert_bank_script:
            query = insert_bank_script.read()
        with self.connection:
            self.connection.execute(query, [chat.id, owner.id])

    def insert_new_window(self, window):
        with open(paths.INSERT_WINDOW, 'r') as insert_window_script:
            query = insert_window_script.read()
        args = self.converter.window_to_row(window)
        with self.connection:
            self.connection.execute(query, args)

    def insert_new_event(self, event):
        with open(paths.INSERT_EVENT, 'r') as insert_event_script:
            query = insert_event_script.read()
        with self.connection:
            self.connection.execute(query, self.converter.event_to_row(event))

    def get_users_list(self):
        with open(paths.SELECT_USERS, 'r') as select_users_script:
            query = select_users_script.read()
        with self.connection:
            users_table = self.connection.execute(query).fetchall()
        return [self.converter.row_to_user(row) for row in users_table]

    def get_chats_list(self):
        with open(paths.SELECT_CHATS, 'r') as select_chats_script:
            query = select_chats_script.read()
        with self.connection:
            chats_table = self.connection.execute(query).fetchall()
        return [self.converter.row_to_chat(row) for row in chats_table]

    def get_chats_with_banks(self):
        """ Returns list of chat ids,
        chat id is in the list if there is a bank already
        created for this chat."""
        query = 'SELECT b.chat_id AS chat_id FROM bank b'
        with self.connection:
            rows = self.connection.execute(query).fetchall()
        print(rows)
        return [row['chat_id'] for row in rows]

    def get_windows_list(self):
        """ Returns list of created windows. """
        with open(paths.SELECT_WINDOWS, 'r') as select_windows_script:
            query = select_windows_script.read()
        with self.connection:
            windows_table = self.connection.execute(query).fetchall()
        return [self.converter.row_to_window(row) for row in windows_table]

    def get_bank(self, chat_id):
        """ Returns tuple (chat, owner, sum) for the bank_id (chat_id).
            Returns None if no banks with such chat_id was found. """
        with open(paths.SELECT_BANK_STATE, 'r') as select_state_script:
            query = select_state_script.read()
        with self.connection:
            bank_row = self.connection.execute(query, [chat_id]).fetchone()
        return self.converter.row_to_bank(bank_row)

    def add_user_to_bank(self, chat_id, user_id):
        with open(paths.ADD_USER_TO_BANK, 'r') as add_user_to_bank_script:
            query = add_user_to_bank_script.read()
        bank_id = self._get_bank_id(chat_id)
        with self.connection:
            self.connection.execute(query, [bank_id, user_id])

    def get_bank_users_ids(self, chat_id):
        """ Get list of user ids of users of particular bank. """
        with open(paths.GET_BANK_USERS, 'r') as get_bank_users_script:
            query = get_bank_users_script.read()
        bank_id = self._get_bank_id(chat_id)
        with self.connection:
            id_list = self.connection.execute(query, [bank_id]).fetchall()
        return [row['user_id'] for row in id_list]

    def get_history(self, chat_id):
        """ Returns list of following tuples:
            (user_id, first_name, last_name,
            event_id, datetime, type, amount, is_deleted)"""
        with open(paths.SELECT_HISTORY, 'r') as select_history_script:
            query = select_history_script.read()
        with self.connection:
            history = self.connection.execute(query, [chat_id]).fetchall()
        return [self.converter.row_to_event(row) for row in history]

    def get_event(self, event_id):
        with open(paths.SELECT_EVENT, 'r') as select_event_script:
            query = select_event_script.read()
        with self.connection:
            row = self.connection.execute(query, [event_id]).fetchone()
        return self.converter.row_to_event(row)

    def get_user_connections(self):
        with open(paths.SELECT_CONNECTION, 'r') as select_user_conn_script:
            query = select_user_conn_script.read()
        with self.connection:
            connection_list = self.connection.execute(query).fetchall()
        connection_list = list(connection_list)
        return connection_list

    def connect_user(self, user, chat):
        with open(paths.CONNECT_USER, 'r') as connect_user_script:
            query = connect_user_script.read()
        with self.connection:
            self.connection.execute(query, [chat.id, user.id])

    def get_available_chats(self, user):
        with open(paths.SELECT_AVAILABLE_CHATS, 'r') as select_chats_script:
            query = select_chats_script.read()
        print(user.id, type(user.id))
        with self.connection:
            chat_rows = self.connection.execute(query, [user.id]).fetchall()
        print(chat_rows)
        return [self.converter.row_to_chat(row) for row in chat_rows]

    def update_window(self, window):
        with open(paths.UPDATE_WINDOW, 'r') as update_window_script:
            query = update_window_script.read()
        with self.connection:
            self.connection.execute(query, [window.message_id, window.user.id])

    def switch_event(self, event_id):
        query = \
            'UPDATE event SET is_deleted = NOT is_deleted WHERE event_id = ?'
        with self.connection:
            self.connection.execute(query, [event_id])

    def _get_bank_id(self, chat_id):
        query = 'SELECT b.bank_id AS id FROM bank b WHERE b.chat_id = ?;'
        with self.connection:
            row = self.connection.execute(query, [chat_id]).fetchone()
        return row['id']
