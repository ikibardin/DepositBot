from telebot.apihelper import ApiException


class DepositBotError(Exception):
    pass


# Windows exceptions:

class WindowError(DepositBotError):
    pass


class WindowNotFoundError(WindowError):
    pass


class WrongChatError(WindowError):
    pass


class UnknownCallbackError(WindowError):
    pass


class InvalidButtonError(WindowError):
    pass


class KeyboardError(WindowError):
    pass


class UnknownModeError(KeyboardError):
    pass


# Banks exceptions:

class BankError(DepositBotError):
    pass


class AccessDenialError(BankError):
    pass


class BankNotFoundError(BankError):
    pass


# Other:

class UnknownEventTypeError(DepositBotError):
    pass
