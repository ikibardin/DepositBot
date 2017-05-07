-- self, chat_id, user, event_type, number, description, datetime, is_deleted
SELECT
  e.event_id   AS event_id,
  b.chat_id    AS chat_id,

  u.user_id    AS user_id,
  u.first_name AS u_first_name,
  u.last_name  AS u_last_name,
  u.username   AS u_username,

  e.type       AS type,
  e.what       AS what,
  e.descr      AS descr,
  e.date       AS datetime,
  e.is_deleted AS is_deleted
FROM event e
  INNER JOIN bank b
    ON b.bank_id = e.bank_id
  INNER JOIN user u
    ON u.user_id = e.user_id
WHERE e.event_id = ?;