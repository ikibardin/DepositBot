import sqlite3
from telebot import types

import windows
import events
from bank import Bank
from constants import errorquotes


class Converter:
    def __init__(self, database):
        self._db = database

    @staticmethod
    def user_to_row(user):
        if not isinstance(user, types.User):
            raise TypeError(errorquotes.TYPE_ERROR.format(types.User,
                                                          type(user)))
        return [user.id, user.first_name, user.last_name, user.username]

    @staticmethod
    def row_to_user(row):
        if not isinstance(row, sqlite3.Row):
            raise TypeError(errorquotes.ROW_EXPECTED.format(type(row)))
        return types.User(id=row['id'],
                          first_name=row['first_name'],
                          last_name=row['last_name'],
                          username=row['username'])

    @staticmethod
    def chat_to_row(chat):
        if not isinstance(chat, types.Chat):
            raise TypeError(errorquotes.TYPE_ERROR.format(types.Chat,
                                                          type(chat)))
        return [chat.id, chat.type, chat.title]

    @staticmethod
    def row_to_chat(row):
        if not isinstance(row, sqlite3.Row):
            raise TypeError(errorquotes.ROW_EXPECTED.format(type(row)))
        return types.Chat(id=row['id'],
                          type=row['type'],
                          title=row['title'])

    def event_to_row(self, event):
        if not isinstance(event, events.Event):
            raise TypeError(
                errorquotes.TYPE_ERROR.format(events.Event, type(event)))
        result = [event.datetime,
                  self._db._get_bank_id(event.chat_id),
                  event.who.id]
        if event.type is events.EventType.CHANGE:
            result.append('CHANGE')
        elif event.type is events.EventType.SET:
            result.append('SET')
        else:
            raise TypeError(errorquotes.UNKNOWN_EVENT.format(type(event)))
        result.extend([event.number, event.description])
        return result

    @staticmethod
    def row_to_event(row):
        assert isinstance(row, sqlite3.Row)
        user = types.User(
            id=row['user_id'],
            first_name=row['u_first_name'],
            last_name=row['u_last_name'],
            username=row['u_username']
        )
        if row['type'] == 'CHANGE':
            event_type = events.EventType.CHANGE
        elif row['type'] == 'SET':
            event_type = events.EventType.SET
        else:
            raise TypeError('Unknown event type.')
        result = events.Event(
            chat_id=row['chat_id'],
            user=user,
            event_type=event_type,
            number=row['what'],
            description=row['descr'],
            datetime_=row['datetime'],
            is_deleted=row['is_deleted'],
            id_=row['event_id']
        )
        return result

    @staticmethod
    def window_to_row(window):
        """ Returns list of arguments of the window to be stored
        in the database. """
        if not isinstance(window, windows.DepositBotWindow):
            raise TypeError(
                errorquotes.TYPE_ERROR.format(windows.DepositBotWindow,
                                              type(window))
            )
        result = [
            window.user.id,
            window.chat.id,
            window.message_id
        ]
        return result

    def row_to_window(self, row):
        """ row should be tuple-like object:
        (user_id, first_name, last_name, username,
        chat_id, chat_type, chat_title,
        window_message_id, window_type, window_mode, window_number)"""
        if not isinstance(row, sqlite3.Row):
            raise TypeError(errorquotes.ROW_EXPECTED.format(type(row)))
        user = types.User(id=row['user_id'],
                          first_name=row['first_name'],
                          last_name=row['last_name'],
                          username=row['username'])
        chat = types.Chat(id=row['chat_id'],
                          type=row['c_type'],
                          title=row['c_title'])
        return windows.DefaultWindow(bot=self._db._bot,
                                     user=user,
                                     chat=chat,
                                     message_id=row['w_message_id'])

    def row_to_bank(self, row):
        if not isinstance(row, sqlite3.Row):
            raise TypeError(errorquotes.ROW_EXPECTED.format(type(row)))

        chat = types.Chat(id=row['c_id'],
                          type=row['c_type'],
                          title=row['c_title'])
        owner = types.User(id=row['u_id'],
                           first_name=row['u_first_name'],
                           last_name=row['u_last_name'],
                           username=row['u_username'])
        return Bank(chat, owner, self._db)
