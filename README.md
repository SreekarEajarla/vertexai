curl --location 'http://localhost:5050/login?email=rajesh%40p2x.com&password=123321' \
--header 'Content-Type: text/plain' \
--header 'Content-Type: application/json' \
--data-raw '{
  "email_id": "rajesh@p2x.com",
  "password": "123321"
}
'
