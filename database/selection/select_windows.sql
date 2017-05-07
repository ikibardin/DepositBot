-- bot, user, chat, message_id, mode=None, number=None

SELECT
  u.user_id    AS user_id,
  u.first_name AS first_name,
  u.last_name  AS last_name,
  u.username   AS username,
  c.chat_id    AS chat_id,
  c.type       AS c_type,
  c.title      AS c_title,
  w.message_id AS w_message_id
FROM window w
  INNER JOIN user u
    ON w.user_id = u.user_id
  INNER JOIN chat c
    ON c.chat_id = w.chat_id;