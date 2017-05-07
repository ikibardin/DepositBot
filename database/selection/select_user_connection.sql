SELECT
  u.user_id,
  b.chat_id
FROM user u
LEFT JOIN bank b
ON u.connected_to = b.bank_id;