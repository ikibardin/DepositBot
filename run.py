# -*- coding: utf-8 -*-
from bot import Bot
import exceptions
import windows
from constants import bot_token, responses, errorquotes, config

# TODO
# - New chat title.

bot = Bot(bot_token.TOKEN, threaded=False)


@bot.message_handler(commands=['start'])
def send_welcome_message(message):
    bot.scan_message(message)
    print(message.chat.id not in bot.banks.keys())
    if message.chat.id not in bot.banks.keys():
        bot.create_new_bank(message.chat, message.from_user)
        bot.connect_user(message.from_user, message.chat)
        assert bot.get_active_bank(message.from_user).user_has_access(
            message.from_user)
        bot.logger.info('New bank was created.')
        response = responses.BANK_WAS_CREATED
    else:
        response = responses.BANK_ALREADY_CREATED
    if message.chat.type != 'private':
        bot.send_message(message.chat.id, response)
        return
    try:
        bot.switch_to_default_window(message.from_user)
        new_message = bot.send_message(message.chat.id,
                                       responses.WINDOW_LOADING)
        bot.get_window(message.from_user).update_message(new_message)
        bot.get_window(message.from_user).update_window(response)
    except exceptions.WindowNotFoundError:
        bot.create_window(message.from_user, message.chat, response)
    except exceptions.ApiException as exception:
        bot.logger.warning(exception)
        raise
    except Exception as exception:
        bot.logger.critical(exception)
        bot.send_message(message.chat.id, responses.UNEXPECTED_ERROR)
        raise


@bot.message_handler(commands=['help'])
def command_help(message):
    bot.scan_message(message)
    try:
        if message.chat.type != 'private':
            bot.send_message(message.chat.id,
                             responses.HELP_TEXT,
                             parse_mode='Markdown')
            return
        if message.chat.id not in bot.banks.keys():
            bot.send_message(message.chat.id, responses.BANK_NOT_FOUND)
            return
        active_window = bot.get_window(message.from_user)
        new_message = bot.send_message(message.chat.id,
                                       responses.WINDOW_LOADING)
        active_window.update_message(new_message)
        active_window.update_window(responses.HELP_TEXT)
    except exceptions.WindowNotFoundError:
        bot.create_window(message.from_user, message.chat, responses.HELP_TEXT)
    except exceptions.ApiException as exception:
        bot.logger.warning(exception)
        raise
    except Exception as exception:
        bot.logger.critical(exception)
        bot.send_message(message.chat.id, responses.UNEXPECTED_ERROR)
        raise


@bot.callback_query_handler(func=lambda query: query.data == 'HELP')
def query_help(query):
    try:
        bot.answer_callback_query(query.id)
        bot.get_window(query.from_user).update_window(responses.HELP_TEXT)
    except exceptions.WindowNotFoundError as exception:
        bot.logger.error(exception)
        bot.send_message(query.message.chat.id, responses.WINDOW_NOT_FOUND)
    except exceptions.ApiException as exception:
        bot.logger.warning(exception)
        raise
    except Exception as exception:
        bot.logger.critical(exception)
        bot.send_message(query.message.chat.id, responses.UNEXPECTED_ERROR)
        raise


@bot.callback_query_handler(
    func=lambda query: query.data in config.KEYBOARD_MODES)
def query_take(query):
    try:
        bot.answer_callback_query(query.id)
        bot.switch_to_keyboard_window(query.from_user)
        bot.get_window(query.from_user).set_mode(query.data)
        bot.get_window(query.from_user).update_window()
    except exceptions.WindowNotFoundError as exception:
        bot.logger.error(exception)
        bot.send_message(query.message.chat.id, responses.WINDOW_NOT_FOUND)
    except exceptions.BankNotFoundError as exception:
        bot.logger.warning(exception)
        bot.send_message(query.message.chat.id, responses.BANK_NOT_FOUND)
    except exceptions.AccessDenialError as exception:
        bot.logger.error(exception)
        bot.switch_to_default_window(query.from_user)
        bot.get_window(query.from_user).update_window(responses.ACCESS_DENIED)
    except exceptions.ApiException as exception:
        bot.logger.warning(exception)
        raise
    except Exception as exception:
        bot.logger.critical(exception)
        bot.send_message(query.message.chat.id, responses.UNEXPECTED_ERROR)
        raise


@bot.callback_query_handler(func=lambda query: query.data == 'LOGS')
def query_logs(query):
    try:
        bot.answer_callback_query(query.id)
        bot.switch_to_history_window(query.from_user)
        bot.get_window(query.from_user).update_window()
    except exceptions.WindowNotFoundError as exception:
        bot.logger.error(exception)
        bot.send_message(query.message.chat.id, responses.WINDOW_NOT_FOUND)
    except exceptions.BankNotFoundError as exception:
        bot.logger.warning(exception)
        bot.send_message(query.message.chat.id, responses.BANK_NOT_FOUND)
    except exceptions.AccessDenialError as exception:
        bot.logger.error(exception)
        bot.switch_to_default_window(query.from_user)
        bot.get_window(query.from_user).update_window(responses.ACCESS_DENIED)
    except exceptions.ApiException as exception:
        bot.logger.warning(exception)
        raise
    except Exception as exception:
        bot.logger.critical(exception)
        bot.send_message(query.message.chat.id, responses.UNEXPECTED_ERROR)
        raise


@bot.message_handler(commands=['add_users'])
def add_users(message):
    bot.scan_message(message)
    try:
        if message.chat.type == 'private':
            bot.send_message(message.chat.id, responses.GROUP_CHATS_ONLY)
            return
        active_bank = bot.get_chat_bank(message.chat)
        response, markup = active_bank.handle_add_users_command(message)
        response = response.format(active_bank.owner_name())
        bot.send_message(message.chat.id, response,
                         reply_markup=markup, parse_mode='Markdown')
    except exceptions.BankNotFoundError:
        bot.send_message(message.chat.id, responses.BANK_NOT_FOUND)
    except exceptions.AccessDenialError:
        creator_name = bot.get_chat_bank(message.chat).owner_name()
        bot.send_message(message.chat.id,
                         responses.CREATOR_ONLY.format(creator_name),
                         parse_mode='Markdown')
    except exceptions.ApiException as exception:
        bot.logger.warning(exception)
        raise
    except Exception as exception:
        bot.logger.critical(exception)
        bot.send_message(message.chat.id, responses.UNEXPECTED_ERROR)
        raise


@bot.callback_query_handler(func=lambda query: query.data == 'JOIN_BANK')
def query_handler(query):
    try:
        bot.scan_user(query.from_user)
        active_bank = bot.get_chat_bank(query.message.chat)
        if active_bank.user_has_access(query.from_user):
            bot.answer_callback_query(query.id, responses.ALREADY_HAVE_ACCESS)
            return
        active_bank.add_user(query.from_user)
        bot.answer_callback_query(query.id, responses.NOW_HAVE_ACCESS)
    except exceptions.BankNotFoundError as exception:
        bot.logger.error(exception)
        bot.send_message(query.message.chat.id, responses.BANK_NOT_FOUND)
    except exceptions.ApiException as exception:
        bot.logger.warning(exception)
        raise
    except Exception as exception:
        bot.logger.critical(exception)
        bot.send_message(query.message.chat.id, responses.UNEXPECTED_ERROR)
        raise


@bot.callback_query_handler(func=lambda query: query.data == 'CHANGE BANK')
def query_connect(query):
    try:
        bot.answer_callback_query(query.id)
        bot.switch_to_connect_window(query.from_user)
        bot.get_window(query.from_user).update_window()
    except exceptions.WindowNotFoundError as exception:
        bot.logger.error(exception)
        bot.send_message(query.message.chat.id, responses.WINDOW_NOT_FOUND)
    except exceptions.BankNotFoundError as exception:
        bot.logger.error(exception)
        bot.send_message(query.message.chat.id, responses.BANK_NOT_FOUND)
    except exceptions.ApiException as exception:
        bot.logger.warning(exception)
        raise
    except Exception as exception:
        bot.logger.critical(exception)
        bot.send_message(query.message.chat.id, responses.UNEXPECTED_ERROR)
        raise


@bot.callback_query_handler(
    func=lambda query: query.data.startswith('CONNECT_TO'))
def connect_to_bank(query):
    try:
        new_chat_id = int(query.data.split(';')[1])
        active_window = bot.get_window(query.from_user)
        if not isinstance(active_window, windows.ConnectWindow):
            raise exceptions.InvalidButtonError(
                errorquotes.NOT_CONNECT_INSTANCE.format(type(active_window))
            )
        active_window.connect(new_chat_id)
        bot.answer_callback_query(query.id, responses.CONNECTED)
        bot.switch_to_default_window(query.from_user)
        bot.get_window(query.from_user).update_window()
    except exceptions.InvalidButtonError as exception:
        bot.logger.warning(exception)
    except exceptions.BankNotFoundError as exception:
        bot.logger.error(exception)
        bot.send_message(query.message.chat.id, responses.BANK_NOT_FOUND)
    except exceptions.WindowNotFoundError as exception:
        bot.logger.error(exception)
        bot.send_message(query.message.chat.id, responses.WINDOW_NOT_FOUND)
    except exceptions.ApiException as exception:
        bot.logger.warning(exception)
        raise
    except Exception as exception:
        bot.logger.critical(exception)
        bot.send_message(query.message.chat.id, responses.UNEXPECTED_ERROR)
        raise


@bot.message_handler(content_types=['text'])
def text_handler(message):
    bot.scan_message(message)
    if message.chat.type != 'private':
        return
    try:
        active_window = bot.get_window(message.from_user)
        active_window.handle_text(message)
        if active_window.finished():
            response = active_window.get_response()
            bot.switch_to_default_window(message.from_user)
            new_message = bot.send_message(message.chat.id,
                                           responses.WINDOW_LOADING)
            bot.get_window(message.from_user).update_message(new_message)
            bot.get_window(message.from_user).update_window(response)
            return

        new_message = bot.send_message(message.chat.id,
                                       responses.WINDOW_LOADING)
        active_window.update_message(new_message)
        active_window.update_window(responses.HELP_TEXT)
    except exceptions.WindowNotFoundError:
        bot.send_message(message.chat.id, responses.WINDOW_NOT_FOUND)
    except exceptions.BankNotFoundError as exception:
        bot.logger.error(exception)
        bot.send_message(message.chat.id, responses.BANK_NOT_FOUND)
    except exceptions.ApiException as exception:
        bot.logger.warning(exception)
        raise
    except Exception as exception:
        bot.logger.critical(exception)
        bot.send_message(message.chat.id, responses.UNEXPECTED_ERROR)
        raise


@bot.callback_query_handler(
    func=lambda query: query.data.startswith('KEYBOARD'))
def handle_keyboard_input(query):
    try:
        bot.answer_callback_query(query.id)
        active_window = bot.get_window(query.from_user)
        if not isinstance(active_window, windows.KeyboardWindow):
            raise exceptions.InvalidButtonError(
                errorquotes.NOT_KEYBOARD_INSTANCE.format(type(active_window))
            )
        pressed_button = query.data.split(';')[1]
        active_window.press_button(pressed_button)
        if not active_window.finished():
            return
        response = active_window.get_response()
        bot.switch_to_default_window(query.from_user)
        bot.get_window(query.from_user).update_window(response)
    except exceptions.InvalidButtonError as exception:
        bot.logger.warning(exception)
    except exceptions.WindowNotFoundError as exception:
        bot.logger.error(exception)
        bot.send_message(query.message.chat.id, responses.WINDOW_NOT_FOUND)
    except exceptions.BankNotFoundError as exception:
        bot.logger.error(exception)
        bot.get_window(query.from_user).update_window(responses.BANK_NOT_FOUND)
    except exceptions.ApiException as exception:
        bot.logger.warning(exception)
        raise
    except Exception as exception:
        bot.logger.critical(exception)
        bot.send_message(query.message.chat.id, responses.UNEXPECTED_ERROR)
        raise


@bot.callback_query_handler(func=lambda query: query.data == 'PASS')
def pass_query(query):
    try:
        bot.answer_callback_query(query.id)
    except exceptions.ApiException as exception:
        bot.logger.warning(exception)
        raise
    except Exception as exception:
        bot.logger.critical(exception)
        bot.send_message(query.message.chat.id, responses.UNEXPECTED_ERROR)
        raise


@bot.callback_query_handler(func=lambda query: query.data == 'UPDATE')
def update_query(query):
    try:
        bot.answer_callback_query(query.id)
        bot.get_window(query.from_user).update_window()
    except exceptions.WindowNotFoundError as exception:
        bot.logger.error(exception)
        bot.send_message(query.message.chat.id, responses.WINDOW_NOT_FOUND)
    except exceptions.BankNotFoundError as exception:
        bot.logger.error(exception)
        bot.send_message(query.message.chat.id, responses.BANK_NOT_FOUND)
    except exceptions.ApiException as exception:
        bot.logger.warning(exception)
        raise
    except Exception as exception:
        bot.logger.critical(exception)
        bot.send_message(query.message.chat.id, responses.UNEXPECTED_ERROR)
        raise


@bot.callback_query_handler(
    func=lambda query: query.data.startswith('HISTORY'))
def switch_event(query):
    try:
        active_window = bot.get_window(query.from_user)
        if not isinstance(active_window, windows.HistoryWindow):
            raise exceptions.InvalidButtonError(
                errorquotes.NOT_HISTORY_INSTANCE.format(type(active_window))
            )
        active_window.handle_callback_query(query)
        bot.answer_callback_query(query.id)
        if not active_window.finished():
            return
        bot.switch_to_default_window(query.from_user)
        bot.get_window(query.from_user).update_window()
    except exceptions.InvalidButtonError as exception:
        bot.logger.warning(exception)
    except exceptions.WindowNotFoundError as exception:
        bot.logger.error(exception)
        bot.send_message(query.message.chat.id, responses.WINDOW_NOT_FOUND)
    except exceptions.BankNotFoundError as exception:
        bot.logger.error(exception)
        bot.get_window(query.from_user).update_window(responses.BANK_NOT_FOUND)
    except exceptions.ApiException as exception:
        bot.logger.warning(exception)
        raise
    except Exception as exception:
        bot.logger.critical(exception)
        bot.send_message(query.message.chat.id, responses.UNEXPECTED_ERROR)
        raise


if __name__ == '__main__':
    bot.polling(none_stop=True)
    print('Shutting down.')
