WITH available_banks AS (
    SELECT b.chat_id AS chat_id
    FROM bank b
      INNER JOIN bank_user_relation bur
        ON b.bank_id = bur.bank_id
    WHERE bur.user_id = ?
)
SELECT
  c.chat_id as id,
  c.type as type,
  c.title as title
FROM chat c
  INNER JOIN available_banks ab
    ON c.chat_id = ab.chat_id;