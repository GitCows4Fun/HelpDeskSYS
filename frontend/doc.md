# Server endpoints  

## API Endpoints

### POST Endpoints

1. `/api/0/POST/login`
   - Handles login requests
   - Expects JSON with `email` and `password_hash` formatted as:
     - `[{"email": "name@somewhere"}, {"pw_hash": "<>"}]`  
   - Returns auth key and expiration time as:
     - `[true, 200, {"userid": 0, "auth_key": "xxxxxxxxxxxxxxxxxxxx", "expires_in": 300}]`  

2. `/api/0/POST/data`
   - Handles ticket creation
   - Expects JSON with `key`, `title`, and `description` as:  
     - `[{"title": "some stuff"}, {"description": "long string"}, {"key": "<>"}]`  
   - Creates and stores new support tickets
   - Responds with:  
     - `[false, 401, "Invalid or expired key"]`  

3. `/api/0/POST/newuser`
   - Handles new user requests
   - Expects JSON with `email`, `pw_hash` as:  
     - `[{"email": "name@somewhere"}, {"pw_hash": "<>"}, {"commonName": "something something"}]`  
   - Creates new user ticket
   - Responds with:  
     - `[false, 500, "User creation failed"]`  

### GET Endpoints

1. `/api/0/GET/data?key=<auth_key>`
   - Returns list of support tickets as:  
     - `[true, 200, [{"ticketID": 1, "userID": 1, "title": "Some", "description": "strings"},<REPEAT>]]`  
   - Requires valid auth key in query parameter

## Static File Serving

### GET Endpoints​  

1. `/`
   - Serves `dashboard.html`

2. `/favicon.png`
   - Serves favicon

3. `/style`, `/script`, and other static files
   - Serves static content from respective directories within the website folder

4. Other paths like `/about`, `/contact`, etc. which dont include a `.`  
   - Serves corresponding HTML files if they exist

## Return codes

| Code | Meaning |
| :--: | :------ |
| 200 | Query successful |
| 201 | Ticket creation successful |
| 202 | Query accepted (No sql injection detected) |
| 400 | Request is incomplete/incorrect |
| 401 | Unauthorized or expired authentication key |
| 403 | Forbidden (Detected SQL injection) |
| 404 | Request cannot be fulfilled/Resource not found |
| 405 | Method not allowed for request type |
| 411 | Missing content length |
| 418 | Wrong endpoint for request |
| 500 | Server is down |
| 507 | New key cannot be created (Max auth reached) |
