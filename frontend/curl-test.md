# Various curl commands in bash and powershell to test endpoints  

## Descriptions

- Main page endpoint \[GET]  
- Login endpoint \[POST]  
- Ticket endpoint \[POST]  
- Ticket endpoint \[GET]  
- Static favicon endpoint \[GET]  
- Static file endpoint \[GET]  
- Non-existent endpoint (Interpreted as html request) \[GET]  

## Bash    \[using -v for some output data]  

- `curl -v http://127.0.0.1:8008/`  
- `curl -v -X POST -H "Content-Type: application/json" -d '{"email":"your@email.com","password_hash":"your_password_hash"}' http://127.0.0.1:8008/api/0/POST/login`  
- `curl -v -X POST -H "Content-Type: application/json" -d '{"key":"your_verification_key","title":"Test Ticket","description":"This is a test"}' http://127.0.0.1:8008/api/0/POST/ticket`  
- `curl -v -X GET -H "Content-Type: application/json" -d '{"key":"your_verification_key"}' http://127.0.0.1:8008/api/0/GET/data`  
- `curl -v http://127.0.0.1:8008/favicon.png`  
- `curl -v http://127.0.0.1:8008/style/style.css`  
- `curl -v http://127.0.0.1:8008/nonexistent`  

## Powershell  

- `curl http://127.0.0.1:8008/`  
- `curl -X POST -H @{'Content-Type' = 'application/json'} -d '{"email":"your@email.com","password_hash":"your_password_hash"}' http://127.0.0.1:8008/api/0/POST/login`  
- `curl -X POST -H @{'Content-Type' = 'application/json'} -d '{"key":"your_verification_key","title":"Test Ticket","description":"This is a test"}' http://127.0.0.1:8008/api/0/POST/ticket`  
- `curl -X GET -H @{'Content-Type' = 'application/json'} -d '{"key":"your_verification_key"}' http://127.0.0.1:8008/api/0/GET/data`  
- `curl http://127.0.0.1:8008/favicon.png`  
- `curl http://127.0.0.1:8008/style/style.css`  
- `curl http://127.0.0.1:8008/nonexistent`  
