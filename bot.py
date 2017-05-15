import logging

import telebot

from bank import Bank
from database.deposit_bot_database import SQLDatabase
import windows
import exceptions
from constants import config, errorquotes, text_templates, responses

logging.basicConfig(filename=config.LOGS_PATH,
                    format=config.LOGS_FORMAT,
                    level=logging.INFO)


class Bot(telebot.TeleBot):
    def __init__(self, token, threaded=True):
        super().__init__(token, threaded=threaded)
        self.logger = telebot.logger
        self.logger.setLevel(logging.INFO)

        self.logger.info('Starting up...')

        self._db = SQLDatabase(self, config.DATABASE_PATH)
        self._db.setup()
        self.logger.info('Database started up.')

        self.users = dict()
        self.chats = dict()
        self.banks = dict()
        self.windows = dict()

        self._init_users()
        self._init_chats()
        self._init_banks()
        self.user_connections = dict(self._db.get_user_connections())
        self._init_windows()
        self.logger.info('Running...')

    def _init_users(self):
        assert not bool(self.users)
        for user in self._db.get_users_list():
            self.users[user.id] = user
        self.logger.info('Users initialized.')

    def _init_chats(self):
        assert not bool(self.chats)
        for chat in self._db.get_chats_list():
            self.chats[chat.id] = chat
        self.logger.info('Chats initialized.')

    def _init_banks(self):
        assert not bool(self.banks)
        for chat_id in self._db.get_chats_with_banks():
            self.banks[chat_id] = self._db.get_bank(chat_id)
        self.logger.info('Banks initialized.')

    def _init_windows(self):
        assert not bool(self.windows)
        for window_ in self._db.get_windows_list():
            self.windows[window_.user.id] = window_
            if isinstance(window_, windows.ConnectWindow):
                self.switch_to_connect_window(window_.user)
            try:
                self.windows[window_.user.id].update_window()
            except telebot.apihelper.ApiException as exception:
                self.logger.warning(exception)
        self.logger.info('Windows initialized.')

    def scan_user(self, user):
        if user.id not in self.users.keys():
            self._db.insert_new_user(user)
            self.users[user.id] = user
            self.logger.info('New user: {}'.format(user))

    def scan_message(self, message):
        self.logger.info(text_templates.MESSAGE_LOG.format(message.text,
                                                           message.from_user))
        self.scan_user(message.from_user)
        if message.chat.id not in self.chats.keys():
            self._db.insert_new_chat(message.chat)
            self.chats[message.chat.id] = message.chat
            self.logger.info('New chat: {}'.format(message.chat))

    def create_new_bank(self, chat, owner):
        assert chat.id not in self.banks.keys()
        self._db.insert_new_bank(chat, owner)
        self.banks[chat.id] = Bank(chat, owner, self._db)

    def connect_user(self, user, chat):
        self._db.connect_user(user, chat)
        self.user_connections[user.id] = chat.id

    def get_active_bank(self, user):
        """ Returns Bank object which user is connected to.
            Throws exception.BankNotFoundError if such bank
            was not found. """
        try:
            return self.banks[self.user_connections[user.id]]
        except KeyError as exception:
            raise exceptions.BankNotFoundError(
                errorquotes.BANK_NOT_FOUND_USER.format(str(user))
            ) from exception

    def get_chat_bank(self, chat):
        try:
            return self.banks[chat.id]
        except KeyError as exception:
            raise exceptions.BankNotFoundError(
                errorquotes.BANK_NOT_FOUND_CHAT.format(chat)
            ) from exception

    def get_window(self, user):
        """ Returns Window object which user is connected to.
            Throws window.WindowNotFoundError if such window
            was not found. """
        try:
            return self.windows[user.id]
        except KeyError as exception:
            raise exceptions.WindowNotFoundError(
                errorquotes.WINDOW_NOT_FOUND.format((user))
            ) from exception

    def bank_info(self, user):
        """ Returns text. """
        bank = self.get_active_bank(user)
        text = text_templates.BANK_INFO.format(bank.title(),
                                               bank.owner_name(),
                                               bank.current_sum())
        return text

    def create_window(self, for_user, chat, text):
        if chat.type != 'private':
            raise exceptions.WrongChatError(errorquotes.WINDOW_PRIVATE_ONLY)
        sent_message = self.send_message(chat.id, responses.WINDOW_LOADING)
        self.windows[for_user.id] = windows.DefaultWindow(
            bot=self,
            user=for_user,
            chat=chat,
            message_id=sent_message.message_id
        )
        self._db.insert_new_window(self.windows[for_user.id])
        self.windows[for_user.id].update_window(text)

    def switch_to_default_window(self, user):
        try:
            self.windows[user.id] = windows.DefaultWindow.from_window(
                self.windows[user.id]
            )
        except KeyError as exception:
            raise exceptions.WindowNotFoundError(
                errorquotes.WINDOW_NOT_FOUND.format(user)
            ) from exception

    def switch_to_keyboard_window(self, user):
        try:
            self.windows[user.id] = windows.KeyboardWindow.from_window(
                self.windows[user.id]
            )
        except KeyError as exception:
            raise exceptions.WindowNotFoundError(
                errorquotes.WINDOW_NOT_FOUND.format(user)
            ) from exception

    def switch_to_history_window(self, user):
        try:
            self.windows[user.id] = windows.HistoryWindow.from_window(
                self.windows[user.id]
            )
        except KeyError as exception:
            raise exceptions.WindowNotFoundError(
                errorquotes.WINDOW_NOT_FOUND.format(user)
            ) from exception

    def switch_to_connect_window(self, user):
        try:
            current_chat = self.chats[self.user_connections[user.id]]
        except KeyError as exception:
            raise exceptions.BankNotFoundError(
                errorquotes.BANK_NOT_FOUND_USER.format(user)
            ) from exception
        available_chats = self._db.get_available_chats(user)
        try:
            self.windows[user.id] = windows.ConnectWindow.from_window(
                self.windows[user.id]
            )
        except KeyError as exception:
            raise exceptions.WindowNotFoundError(
                errorquotes.WINDOW_NOT_FOUND.format(user)
            ) from exception
        self.windows[user.id].set_chats(current_chat,
                                        available_chats)

    def update_window_record(self, window_):
        self._db.update_window(window_)

    def get_event_description(self, event_id):
        return self._db.get_event(event_id).description

    def log_query(self, query):
        self.logger.info(text_templates.QUERY_LOG.format(query.data,
                                                         query.from_user))
