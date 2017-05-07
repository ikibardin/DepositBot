BEGIN;

CREATE TABLE IF NOT EXISTS user (
  user_id      INTEGER PRIMARY KEY,
  first_name   VARCHAR(50) NOT NULL,
  username     VARCHAR(50),
  last_name    VARCHAR(50),
  connected_to INTEGER,
  FOREIGN KEY (connected_to) REFERENCES bank (bank_id)
);

CREATE TABLE IF NOT EXISTS chat (
  chat_id INTEGER PRIMARY KEY,
  type    VARCHAR(20) NOT NULL,
  title   VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS bank (
  bank_id  INTEGER PRIMARY KEY AUTOINCREMENT,
  chat_id  INTEGER NOT NULL UNIQUE,
  owner_id INTEGER NOT NULL,
  FOREIGN KEY (chat_id) REFERENCES chat (chat_id),
  FOREIGN KEY (owner_id) REFERENCES user (user_id)
);

CREATE TABLE IF NOT EXISTS bank_user_relation (
  bank_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  FOREIGN KEY (bank_id) REFERENCES bank (bank_id),
  FOREIGN KEY (user_id) REFERENCES user (user_id)
);

CREATE TABLE IF NOT EXISTS window (
  user_id    INTEGER UNIQUE NOT NULL,
  chat_id    INTEGER UNIQUE NOT NULL,
  message_id INTEGER        NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (user_id),
  FOREIGN KEY (chat_id) REFERENCES chat (chat_id)
);

CREATE TABLE IF NOT EXISTS event (
  event_id   INTEGER PRIMARY KEY AUTOINCREMENT,
  date       TIMESTAMP  NOT NULL,
  bank_id    INTEGER    NOT NULL,
  user_id    INTEGER    NOT NULL,
  type       VACHAR(20) NOT NULL,
  what       BIGINT     NOT NULL,
  is_deleted BOOLEAN    NOT NULL DEFAULT 0,
  descr      TEXT,
  FOREIGN KEY (user_id) REFERENCES user (user_id),
  FOREIGN KEY (bank_id) REFERENCES bank (bank_id),
  CHECK (type IN ('CHANGE', 'SET'))
);

COMMIT;
