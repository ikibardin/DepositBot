UPDATE user
SET connected_to = (SELECT b.bank_id
                      FROM bank b
                      WHERE b.chat_id = ?)
WHERE user_id = ?;