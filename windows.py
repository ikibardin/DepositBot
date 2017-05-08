import random

from telebot import types, apihelper

import events
import exceptions
from constants import errorquotes, responses, config, text_templates


class DepositBotWindow:
    def __init__(self, bot, user, chat, message_id):
        if user.id != chat.id or chat.type != 'private':
            raise exceptions.WrongChatError(
                errorquotes.WINDOW_WRONG_CHAT.format(user.id,
                                                     chat.id,
                                                     chat.type)
            )
        if message_id is None:
            raise exceptions.WindowNotFoundError(
                errorquotes.MESSAGE_ID_NOT_NONE)
        self.bot = bot
        self.user = user
        self.chat = chat
        self.message_id = message_id

    def finished(self):
        return False

    @classmethod
    def from_window(cls, window):
        if not isinstance(window, DepositBotWindow):
            raise TypeError(errorquotes.MUST_BE_WINDOW.format(type(window)))
        return cls(window.bot,
                   window.user,
                   window.chat,
                   window.message_id)

    def update_message(self, new_message):
        if not isinstance(new_message, types.Message):
            raise TypeError(
                errorquotes.MUST_BE_MESSAGE.format(type(new_message))
            )
        if self.chat.id != new_message.chat.id:
            raise exceptions.WrongChatError(
                errorquotes.WINDOW_MIGRATION.format(self.chat.id,
                                                    new_message.chat.id)
            )
        if self.message_id != new_message.message_id:
            self._destroy_window()
        self.message_id = new_message.message_id
        self.bot.update_window_record(self)

    def update_window(self, response=None):
        assert self.message_id is not None
        window_text, window_markup = self.get_message()
        bank_info = self.bot.bank_info(self.user)
        assert bank_info is not None
        if response is not None and window_text is not None:
            text = '{}\n\n{}\n\n{}'.format(response, window_text, bank_info)
        elif response is not None:
            text = '{}\n\n{}'.format(response, bank_info)
        elif window_text is not None:
            text = '{}\n\n{}'.format(window_text, bank_info)
        else:
            text = bank_info
        self.bot.update_window_record(self)
        try:
            self.bot.edit_message_text(
                text=text,
                chat_id=self.chat.id,
                message_id=self.message_id,
                reply_markup=window_markup,
                parse_mode='Markdown'
            )
        except apihelper.ApiException as exception:
            self.bot.logger.warning(exception)

    def handle_text(self, message):
        if self.user.id != message.from_user.id:
            raise exceptions.WrongChatError(errorquotes.WINDOW_WRONG_PERSON)

    def _destroy_window(self):
        assert self.message_id is not None
        self.bot.edit_message_text(
            text=random.choice(responses.WINDOW_DESTROYED),
            chat_id=self.chat.id,
            message_id=self.message_id,
            reply_markup=None,
            parse_mode='Markdown'
        )
        self.message_id = None

    def get_message(self):
        raise exceptions.WindowNotFoundError(errorquotes.MUST_BE_NOT_BASE_CLS)


class DefaultWindow(DepositBotWindow):
    def get_message(self):
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = list()
        for command in ['Add', 'Take']:
            buttons.append(
                types.InlineKeyboardButton(command,
                                           callback_data=command.upper())
            )
        markup.add(*buttons)
        buttons = list()
        if self.bot.get_active_bank(self.user).is_owner(self.user):
            markup.row(
                types.InlineKeyboardButton('💰 Set', callback_data='SET')
            )
        for command in ['Update', 'Logs', 'Change bank', 'Help']:
            buttons.append(
                types.InlineKeyboardButton(command,
                                           callback_data=command.upper())
            )
        markup.add(*buttons)
        return None, markup


class KeyboardWindow(DepositBotWindow):
    def __init__(self, bot, user, chat, message_id, mode=None, number=None):
        """ Can raise exception.BankNotFoundError as
        bot.get_active_bank() can. """
        super().__init__(bot, user, chat, message_id)
        self.mode = None
        self._number = 0
        if mode is not None:
            self.mode = mode
        if number is not None:
            self._number = number
        self._description_mode = False
        self._finished = True
        self._response = None
        self._text = None
        self._waiting_for_text = False

    def get_message(self):
        return self.get_text(), self.get_markup()

    def get_text(self):
        print(self._waiting_for_text)
        if self._waiting_for_text:
            return self._get_waiting_text()
        elif self._description_mode:
            return self._get_description_text()
        else:
            return self._get_keyboard_text()

    def get_markup(self):
        if self._waiting_for_text:
            return None
        elif self._description_mode:
            return self._get_description_markup()
        return self._get_keyboard_markup()

    def finished(self):
        return self._finished

    def get_response(self):
        return self._response

    def set_mode(self, mode):
        assert self.mode is None
        if mode not in config.KEYBOARD_MODES:
            raise exceptions.UnknownModeError(
                errorquotes.WRONG_KEYBOARD_MODE.format(config.KEYBOARD_MODES,
                                                       mode)
            )
        if (mode == 'SET' and
                not self.bot.get_active_bank(self.user).is_owner(self.user)):
            raise exceptions.AccessDenialError(errorquotes.SET_ADMIN_ONLY)
        self.mode = mode

        if self.mode == 'ADD':
            self.bot.get_active_bank(self.user).start_addition(self.user)
        elif self.mode == 'TAKE':
            self.bot.get_active_bank(self.user).start_taking(self.user)
        self._finished = False
        self._text = self._get_keyboard_text()

    def get_number(self):
        return self._number

    def press_button(self, button):
        self._assert_button_is_correct(button)
        print(button)
        if button == 'DESCR_YES':
            self._waiting_for_text = True
        elif button == 'DESCR_NO':
            self._finish_input(None)
        elif button == 'CANCEL':
            self.bot.get_active_bank(self.user).cancel_keyboard_input(
                self.user)
            self._finished = True
        elif button == 'OK':
            if not self.get_number() > 0:
                self.update_window(responses.KEYBOARD_INPUT_ERROR)
                return
            self._description_mode = True
            self._text = self._get_description_text()
        elif button == 'BACKSPACE':
            self._number //= 10
        else:
            self._number = 10 * self._number + int(button)
        self.update_window()

    def _finish_input(self, description):
        assert self.mode in config.KEYBOARD_MODES
        self._waiting_for_text = False
        self._description_mode = False
        if self.mode == 'ADD' or self.mode == 'TAKE':
            response = self.bot.get_active_bank(
                self.user).handle_keyboard_input(
                from_user=self.user,
                number=self.get_number(),
                description=description
            )
            self._response = response
        elif self.mode == 'SET':
            self.bot.get_active_bank(self.user).set_money(self.user,
                                                          self.get_number(),
                                                          description)
            self._response = responses.SUCCESS_SET.format(
                self.get_number())
        self._waiting_for_text = False
        self._description_mode = False
        self._finished = True

    def _assert_button_is_correct(self, button):
        if (not self._description_mode
            and button not in ['CANCEL', 'OK', 'BACKSPACE']
            and not (button.isdigit() and len(button) == 1)):
            raise exceptions.InvalidButtonError(
                errorquotes.INVALID_KEYBOARD_BUTTON.format(button)
            )
        if self._description_mode and button not in ['DESCR_YES', 'DESCR_NO']:
            raise exceptions.InvalidButtonError(
                errorquotes.INVALID_DESCRIPTION_BUTTON.format(button)
            )

    def handle_text(self, message):
        if self.user.id != message.from_user.id:
            raise exceptions.WrongChatError(errorquotes.WINDOW_WRONG_PERSON)
        if not self._waiting_for_text:
            return
        self._finish_input(message.text)

    def _get_description_text(self):
        text = responses.DESCRIPTION_QUESTION.format(
            self._get_operation_text()
        )
        return text

    @staticmethod
    def _get_description_markup():
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.row(
            types.InlineKeyboardButton('Yes',
                                       callback_data='KEYBOARD;DESCR_YES'),
            types.InlineKeyboardButton('No',
                                       callback_data='KEYBOARD;DESCR_NO')
        )
        return markup

    def _get_keyboard_text(self):
        assert self.mode in config.KEYBOARD_MODES
        if self.mode == 'ADD':
            text = responses.KEYBOARD_ADD_TEXT
        elif self.mode == 'TAKE':
            text = responses.KEYBOARD_TAKE_TEXT
        elif self.mode == 'SET':
            text = responses.KEYBOARD_SET_TEXT
        else:
            raise exceptions.UnknownModeError(
                errorquotes.WRONG_KEYBOARD_MODE.format(config.KEYBOARD_MODES,
                                                       self.mode)
            )
        return text_templates.KEYBOARD_TEXT.format(text, self._number)

    @staticmethod
    def _get_keyboard_markup():
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.row(
            types.InlineKeyboardButton('Cancel',
                                       callback_data='KEYBOARD;CANCEL')
        )
        buttons = [
            types.InlineKeyboardButton(str(i),
                                       callback_data='KEYBOARD;{}'.format(i))
            for i in range(1, 10)
            ]
        buttons.append(
            types.InlineKeyboardButton('<-',
                                       callback_data='KEYBOARD;BACKSPACE')
        )
        buttons.append(
            types.InlineKeyboardButton('0',
                                       callback_data='KEYBOARD;0')
        )
        buttons.append(
            types.InlineKeyboardButton('OK',
                                       callback_data='KEYBOARD;OK')
        )
        markup.add(*buttons)
        return markup

    def _get_waiting_text(self):
        print(responses.DESCRIPTION_WAITING.format(self._get_operation_text()))
        return responses.DESCRIPTION_WAITING.format(self._get_operation_text())

    def _get_operation_text(self):
        assert self.mode is not None
        if self.mode == 'ADD':
            text = responses.OPERATION_ADD_TEXT
        elif self.mode == 'TAKE':
            text = responses.OPERATION_TAKE_TEXT
        elif self.mode == 'SET':
            text = responses.OPERATION_SET_TEXT
        else:
            raise exceptions.UnknownModeError(
                errorquotes.WRONG_KEYBOARD_MODE.format(config.KEYBOARD_MODES,
                                                       self.mode)
            )
        return text.format(self.get_number())


class HistoryWindow(DepositBotWindow):
    def __init__(self, bot, user, chat, message_id):
        super().__init__(bot, user, chat, message_id)
        self._text = responses.HISTORY_TEXT
        if not self.bot.get_active_bank(user).is_owner(user):
            self._text = '{}\n\n{}'.format(self._text,
                                           responses.HISTORY_NOT_ALL_SHOWN)
        self._finished = False
        self._buttons_limit = config.HISTORY_CHUNK_SIZE

    def get_message(self):
        return self._text, self._format_history(self._get_history())

    def finished(self):
        return self._finished

    def handle_callback_query(self, query):
        mark, data = query.data.split(';', 1)
        if mark != 'HISTORY':
            raise exceptions.InvalidButtonError(
                errorquotes.INVALID_HISTORY_BUTTON.format(query.data)
            )
        if data == 'BACK':
            self._finished = True
        elif data == 'EXPAND':
            self._buttons_limit += config.HISTORY_CHUNK_SIZE
            self.update_window()
        elif data.startswith('SWITCH'):
            event_id = data.split(';')[1]
            try:
                self._switch_event(query.from_user, event_id)
                self.update_window()
            except exceptions.AccessDenialError:
                self.bot.answer_callback_query(
                    callback_query_id=query.id,
                    text=responses.HISTORY_SWITCH_NOT_ALLOWED,
                    show_alert=True
                )
        elif data.startswith('DESCR'):
            event_id = data.split(';')[1]
            description = self._get_description(event_id)
            if description is None:
                description = responses.HISTORY_NO_DESCRIPTION
            self.bot.answer_callback_query(
                callback_query_id=query.id,
                text=description,
                show_alert=True
            )
        else:
            raise exceptions.InvalidButtonError(
                errorquotes.INVALID_HISTORY_BUTTON.format(query.data)
            )

    def _get_history(self):
        bank = self.bot.get_active_bank(self.user)
        return bank.handle_logs_command(self.user)

    def _switch_event(self, user, event_id):
        self.bot.get_active_bank(self.user).switch_event(user, event_id)

    def _get_description(self, event_id):
        return self.bot.get_event_description(event_id)

    def _format_history(self, bank_history):
        """ Returns markup. """
        markup = types.InlineKeyboardMarkup()
        user_ids = {event.who.id for event in bank_history}
        for user_id in user_ids:
            user_history = [event for event in bank_history
                            if event.who.id == user_id]

            markup.row(HistoryWindow._get_user_button(user_history))
            markup.row(HistoryWindow._get_total_change_button(user_history))

            if len(user_history) > self._buttons_limit:
                markup.row(
                    types.InlineKeyboardButton('Show more...',
                                               callback_data='HISTORY;EXPAND')
                )
                user_history = user_history[-self._buttons_limit:]

            button_rows = HistoryWindow._get_event_buttons(user_history)
            for date_button, change_button in button_rows:
                markup.row(date_button, change_button)
        markup.row(
            types.InlineKeyboardButton('Back', callback_data='HISTORY;BACK')
        )
        return markup

    @staticmethod
    def _get_user_button(user_history):
        """ Returns InlineKeyboardButton with a name of the user
        whom user_history belongs to."""
        first_name = user_history[0].who.first_name
        last_name = user_history[0].who.last_name
        if last_name is not None:
            name = text_templates.HISTORY_USER_FULL.format(first_name,
                                                           last_name)
        else:
            name = text_templates.HISTORY_USER_FIRST_ONLY.format(first_name)
        return types.InlineKeyboardButton(name, callback_data='PASS')

    @staticmethod
    def _get_total_change_button(user_history):
        """ Returns InlineKeyBoardButton with sum of all operations
        of user_history on it. """
        total_change = 0
        for event in user_history:
            if event.is_deleted:
                continue
            if event.type is events.EventType.CHANGE:
                total_change += event.number
            elif event.type is events.EventType.SET:
                total_change = event.number
            else:
                raise exceptions.UnknownEventTypeError(
                    errorquotes.UNKNOWN_EVENT.format(repr(event.type))
                )
        formatted_total_change = text_templates.HISTORY_TOTAL_CHANGE.format(
            total_change
        )
        return types.InlineKeyboardButton(formatted_total_change,
                                          callback_data='PASS')

    @staticmethod
    def _get_event_buttons(user_history):
        """ Returns list of tuples (date_button, change_button)
        of InlineKeyboardButton for every row of user_history. """
        button_rows = list()
        for event in user_history:
            date_text = event.datetime.strftime(text_templates.DATE)
            if event.is_deleted:
                date_text = text_templates.DELETED.format(date_text)
            else:
                date_text = text_templates.ACTIVE.format(date_text)
            date_button = types.InlineKeyboardButton(
                date_text,
                callback_data='HISTORY;SWITCH;{}'.format(event.id)
            )

            if event.type is events.EventType.SET:
                label = text_templates.HISTORY_SET.format(event.number)
            else:
                label = text_templates.HISTORY_ADD_OR_TAKE.format(event.number)
            change_button = types.InlineKeyboardButton(
                label,
                callback_data='HISTORY;DESCR;{}'.format(event.id)
            )
            button_rows.append((date_button, change_button))
        return button_rows


class ConnectWindow(DepositBotWindow):
    def __init__(self, bot, user, chat, message_id):
        super().__init__(bot, user, chat, message_id)
        self._current_chat = None
        self._available_chats = None

    def set_chats(self, current_chat, available_chats):
        self._current_chat = current_chat
        self._available_chats = available_chats

    def get_text(self):
        if self._current_chat.type == 'private':
            current_chat_title = 'Private'
        else:
            current_chat_title = self._current_chat.title
        text = responses.CONNECT_TEXT.format(current_chat_title)
        return text

    def get_message(self):
        assert self._current_chat is not None
        assert self._available_chats is not None
        return self.get_text(), \
               self._convert_into_markup(self._available_chats)

    def connect(self, chat_id):
        if chat_id == self._current_chat.id:
            return
        self.bot.connect_user(self.user,
                              self.bot.chats[chat_id])

    @staticmethod
    def _convert_into_markup(available_chats):
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = list()
        for chat in available_chats:
            buttons.append(
                types.InlineKeyboardButton(
                    chat.title if chat.title is not None else 'Private',
                    callback_data='CONNECT_TO;' + str(chat.id)
                )
            )
        markup.add(*buttons)
        return markup
