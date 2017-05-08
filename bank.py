import enum

from telebot import types

import events
import exceptions
from constants import errorquotes, responses


class State(enum.Enum):
    STANDBY = enum.auto()
    ADDING = enum.auto()
    TAKING = enum.auto()


class Bank(object):
    def __init__(self, chat, owner, database):
        self._chat = chat
        self._owner = owner
        self._db = database
        self.sum = None
        self._recalculate_sum()
        self._states = dict()
        self.add_user(self._owner)
        for user_id in self._get_users_id_list():
            self._states[user_id] = State.STANDBY

    def _recalculate_sum(self):
        self.sum = 0
        history = self._db.get_history(self._chat.id)
        if len(history) == 0:
            return
        for event in history:
            if event.is_deleted:
                continue
            if event.type is events.EventType.CHANGE:
                self.sum += event.number
            elif event.type is events.EventType.SET:
                self.sum = event.number
            else:
                raise exceptions.UnknownEventTypeError(
                    errorquotes.UNKNOWN_EVENT.format(repr(event.type))
                )

    def title(self):
        if self._chat.type == 'private':
            return 'Private'
        return self._chat.title

    def owner_name(self):
        if self._owner.last_name is not None:
            return '{} {}'.format(self._owner.first_name,
                                  self._owner.last_name)
        return self._owner.first_name

    def current_sum(self):
        return self.sum

    def is_owner(self, user):
        return user.id == self._owner.id

    def user_has_access(self, user):
        return user.id in self._get_users_id_list()

    def add_user(self, user):
        if not self.user_has_access(user):
            self._db.add_user_to_bank(self._chat.id, user.id)

    def add_money(self, user, amount, description):
        if not self.user_has_access(user):
            raise exceptions.AccessDenialError(
                errorquotes.ACCESS_DENIED.format(repr(user))
            )
        if not amount > 0:
            raise ValueError(errorquotes.POSITIVE_INTEGER.format(str(amount)))
        event = events.Event(self._chat.id,
                             user,
                             events.EventType.CHANGE,
                             amount,
                             description)
        self._db.insert_new_event(event)
        self.sum += amount

    def take_money(self, user, amount, description):
        if not self.user_has_access(user):
            raise exceptions.AccessDenialError(
                errorquotes.ACCESS_DENIED.format(repr(user))
            )
        if not amount > 0:
            raise ValueError(errorquotes.POSITIVE_INTEGER.format(str(amount)))
        event = events.Event(self._chat.id,
                             user,
                             events.EventType.CHANGE,
                             -amount,
                             description)
        self._db.insert_new_event(event)
        self.sum -= amount

    def set_money(self, user, amount, description):
        if not self.is_owner(user):
            raise exceptions.AccessDenialError(errorquotes.SET_ADMIN_ONLY)
        event = events.Event(self._chat.id,
                             user,
                             events.EventType.SET,
                             amount,
                             description)
        self._db.insert_new_event(event)
        self.sum = amount

    def _get_users_id_list(self):
        """ Get list of users' ids of users that have access
        to the bank.
        """
        return self._db.get_bank_users_ids(self._chat.id)

    def start_addition(self, user):
        """ Can throw exception.AccessDenialError if user does not
            have access to the bank. """
        if not self.user_has_access(user):
            raise exceptions.AccessDenialError(
                errorquotes.ACCESS_DENIED.format(repr(user)))
        self._states[user.id] = State.ADDING

    def start_taking(self, user):
        """ Can throw exception.AccessDenialError if user does not
            have access to the bank. """
        if not self.user_has_access(user):
            raise exceptions.AccessDenialError(
                errorquotes.ACCESS_DENIED.format(repr(user)))
        self._states[user.id] = State.TAKING

    def handle_logs_command(self, from_user):
        """ Returns unformatted history of operations.
            Throws exception.AccessDenialError if user do not
            have access to the bank. """
        if not self.user_has_access(from_user):
            raise exceptions.AccessDenialError(
                errorquotes.ACCESS_DENIED.format(repr(from_user)))
        history = self._db.get_history(self._chat.id)
        self._states[from_user.id] = State.STANDBY
        if not self.is_owner(from_user):
            history = [event for event in history
                       if event.who.id == from_user.id]
        return history

    def handle_add_users_command(self, message):
        """ Returns (response, markup) tuple.
            Throws exception.AccessDenialError
            if user is not owner of the bank. """
        if not self.is_owner(message.from_user):
            raise exceptions.AccessDenialError(
                errorquotes.ADD_USERS_ADMIN_ONLY)
        markup = types.InlineKeyboardMarkup(row_width=1)
        join_bank_button = types.InlineKeyboardButton(
            'Join bank',
            callback_data='JOIN_BANK'
        )
        markup.add(join_bank_button)
        return responses.ADD_USERS_RESPONSE, markup

    def handle_keyboard_input(self, from_user, number, description=None):
        if not self.user_has_access(from_user):
            raise exceptions.AccessDenialError(
                errorquotes.ACCESS_DENIED.format(repr(from_user)))
        if self._states[from_user.id] is State.STANDBY:
            return responses.SEE_HELP
        elif self._states[from_user.id] in (State.ADDING, State.TAKING):
            if self._states[from_user.id] is State.ADDING:
                self.add_money(from_user, number, description)
                response = responses.SUCCESS_ADD.format(number)
            else:
                self.take_money(from_user, number, description)
                response = responses.SUCCESS_TAKE.format(number)
            self._states[from_user.id] = State.STANDBY
            return response

    def cancel_keyboard_input(self, from_user):
        self._states[from_user.id] = State.STANDBY

    def switch_event(self, user, event_id):
        event = self._db.get_event(event_id)
        if user.id != self._owner.id and user.id != event.who.id:
            raise exceptions.AccessDenialError(errorquotes.SWITCH_OWN_ONLY)
        self._db.switch_event(event_id)
        self._recalculate_sum()
