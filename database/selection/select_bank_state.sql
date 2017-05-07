SELECT
  c.chat_id    AS c_id,
  c.type       AS c_type,
  c.title      AS c_title,
  u.user_id    AS u_id,
  u.first_name AS u_first_name,
  u.last_name  AS u_last_name,
  u.username   AS u_username
FROM bank b
  INNER JOIN chat c
    ON c.chat_id = b.chat_id
  INNER JOIN user u
    ON b.owner_id = u.user_id
WHERE b.chat_id = ?;
