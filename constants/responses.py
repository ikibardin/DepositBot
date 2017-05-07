# -*- coding: utf-8 -*-
HELP_TEXT = 'Tap on Add or Take to manage the balance of the bank.' \
            '\nTap on Logs to see history of operations and to undo' \
            ' some of them if necessary.\nTap on Connect to connect to' \
            ' another bank, created in some group chat (Your personal' \
            ' bank is called Private).\n\nTo create a bank for a group ' \
            'chat, add the bot to the chat, type /start to create bank,' \
            ' then type /add\_users to start users addition to the bank. '

BANK_WAS_CREATED = 'A new bank was created for this chat. Feel free to use ' \
                   'it. See /help for available commands.'

BANK_ALREADY_CREATED = 'A bank for this chat has already been created. See ' \
                       '/help for a list of available commands.'

BANK_NOT_FOUND = 'No bank created for this chat was found. ' \
                 'Create it, using /start command.'

WINDOW_LOADING = 'Loading window, please wait...'

WINDOW_NOT_FOUND = 'Sorry, no session was found. ' \
                   'Please, try typing /start.'

UNEXPECTED_ERROR = 'Sorry, unexpected error occurred. Now I am dead. ☠️'

ACCESS_DENIED = 'Access denied.'

GROUP_CHATS_ONLY = 'Sorry, this command is available in group ' \
                   'chats only. See /help for more information.'

CREATOR_ONLY = 'Only administrator of the bank can initialize ' \
               'user addition to the bank.\nAdministrator: *{}*.'

ALREADY_HAVE_ACCESS = 'You already have access to the bank.'
NOW_HAVE_ACCESS = 'Now you have access to the bank.'

CONNECTED = 'Connected.'

ADD_USERS_RESPONSE = 'Press the button to get access to the bank of ' \
                     'this chat.\n\nAdministrator of the bank: *{}*.'

SEE_HELP = 'See /help for a list of available commands.'

WINDOW_DESTROYED = [
    'This message has flown away.  🚀',
    'This message was stolen. 👽',
    'This message was recycled. ♻️',
    'This message was eaten. 🐉'
]

# KEYBOARD RESPONSES

KEYBOARD_ADD_TEXT = 'Enter sum to be added to the bank.'
KEYBOARD_TAKE_TEXT = 'Enter sum to be taken from the bank.'
KEYBOARD_SET_TEXT = 'Enter sum to set for the bank.'

OPERATION_ADD_TEXT = '*Add {}* to the bank.'
OPERATION_TAKE_TEXT = '*Take {}* from the bank.'
OPERATION_SET_TEXT = '*Set {}* for the bank.'

SUCCESS_ADD = 'Successfully added *{}*.'
SUCCESS_TAKE = 'Successfully taken *{}*.'
SUCCESS_SET = 'Successfully set amount in the bank to *{}*.'

DESCRIPTION_QUESTION = 'Would you like to leave a description for the ' \
                       'following operation?\n{}'
DESCRIPTION_WAITING = 'Please send me description for the following ' \
                      'operation:\n{}'

# HISTORY RESPONSES
HISTORY_TEXT = 'Tap on the date of an operation to delete ' \
               'or recover it.\nTap on the number of an operation ' \
               'to see its description.'
HISTORY_NOT_ALL_SHOWN = 'Note that as you are not the administrator ' \
                        'of the bank, history of only your operations' \
                        ' is shown.'
HISTORY_SWITCH_NOT_ALLOWED = 'As a non-administrator, you are allowed to' \
                             ' switch only your operations.'
HISTORY_NO_DESCRIPTION = 'No description was left.'

# CONNECTION WINDOW RESPONSES
CONNECT_TEXT = 'You have access to the following banks. ' \
               'Choose the one you would like to connect to. ' \
               '(Now connected to *{}*)'
