# -*- coding: utf-8 -*-
NO_CONNECT_METHOD = 'Active window ({}) has no connect() method. '

NOT_KEYBOARD_INSTANCE = 'Active window ({}) is not instance of ' \
                        'windows.KeyboardWindow anymore.'
NOT_HISTORY_INSTANCE = 'Active window ({}) is not instance of ' \
                       'windows.HistoryWindow anymore.'
NOT_CONNECT_INSTANCE = 'Active window ({}) is not instance of ' \
                       'windows.ConnectWindow anymore.'
BANK_NOT_FOUND_USER = 'Bank not found for user {}.'
BANK_NOT_FOUND_CHAT = 'Bank not found for chat {}.'
WINDOW_NOT_FOUND = 'Window not found for user {}'

WINDOW_PRIVATE_ONLY = 'Chat must be private to create a window in it.'

UNKNOWN_EVENT = 'Unknown event type: {}.'
ACCESS_DENIED = 'Access denied for {}.'
POSITIVE_INTEGER = 'Amount must be a positive integer number, ' \
                   'while it is {}.'
SET_ADMIN_ONLY = 'Only administrator can set the amount in the bank.'
ADD_USERS_ADMIN_ONLY = 'Only owner of the bank can start user addition.'

SWITCH_OWN_ONLY = 'Common users can only switch their own operations.'

WINDOW_WRONG_CHAT = 'Invalid chat passed to window constructor. User id ' \
                    'must be equal to chat id, while they are {} and {} ' \
                    'respectively; chat type must be "private" while it is {}.'
MUST_BE_WINDOW = 'Argument window must be instance of ' \
                 'windows.DepositBotWindow, while its type is {}.'
MUST_BE_MESSAGE = 'Argument new_message must be instance of ' \
                  'telebot.types.Message, while its type is {}.'
WINDOW_MIGRATION = 'Window can not migrate between chats. Old chat id: {}. ' \
                   'New chat id {}.'
WINDOW_WRONG_PERSON = 'Window is getting messages from wrong person.'
MESSAGE_ID_NOT_NONE = 'Message id argument must not be None. Window should ' \
                      'not be created before a message for it was sent.'
MUST_BE_NOT_BASE_CLS = 'Method get_message() must not be used for ' \
                       'windows.DepositBotWindow, it is incomplete class.'
WRONG_KEYBOARD_MODE = 'Keyboard mode must be one of following: {}, ' \
                      'while it is: {}.'
INVALID_KEYBOARD_BUTTON = 'The window is in keyboard mode. Unknown button: {}.'
INVALID_DESCRIPTION_BUTTON = 'The window is already in description mode. ' \
                             'Button is invalid: {}.'
INVALID_HISTORY_BUTTON = 'The window is in history mode. Unknown button: {}.'

TYPE_ERROR = 'Invalid argument type. Expected {}, got {}.'
ROW_EXPECTED = 'Invalid row argument. Expected instance of ' \
               'sqlite3.Row, got {}.'
