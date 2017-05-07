import enum
import datetime

import exceptions
from constants import errorquotes


class EventType(enum.Enum):
    CHANGE = enum.auto()
    SET = enum.auto()


class Event(object):
    def __init__(self, chat_id, user, event_type,
                 number, description,
                 datetime_=None, is_deleted=False, id_=None):
        if not isinstance(event_type, EventType):
            raise exceptions.UnknownEventTypeError(
                errorquotes.UNKNOWN_EVENT.format(repr(event_type))
            )
        if datetime_ is None:
            self.datetime = datetime.datetime.today()
        else:
            if not isinstance(datetime_, datetime.datetime):
                raise TypeError('date must be instance of datetime.datetime.')
            self.datetime = datetime_
        self.chat_id = chat_id
        self.who = user
        self.type = event_type
        self.number = number
        self.description = description
        self.is_deleted = is_deleted
        self.id = id_
