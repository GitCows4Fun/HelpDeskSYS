
// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8008';

// Generate SHA256 hash for password security
async function generateSHA256(message) {
	const msgBuffer = new TextEncoder().encode(message);
	const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
	const hashArray = Array.from(new Uint8Array(hashBuffer));
	const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
	return hashHex;
}

// Handle login button click
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault(); // Prevent default form submission
	e.stopPropagation();
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const errorMessage = document.getElementById('errorMessage');
    const loginButton = document.getElementById('loginButton');
    
    // Validate input fields
    if (!username || !password) {
        errorMessage.textContent = 'Please enter both email and password.';
        errorMessage.style.display = 'block';
        return;
    }
    
    // Update UI state during authentication
    loginButton.disabled = true;
    loginButton.textContent = 'Logging in...';
    errorMessage.style.display = 'none';
    
    // Convert username to email format if needed
    const email = username.includes('@') ? username : `${username}@helpdesk.sys`;
    
    try {
        // Hash password for API transmission
        const passwordHash = await generateSHA256(password);
        
        // Send authentication request to API
        const response = await fetch(`${API_BASE_URL}/api/0/POST/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
			body: JSON.stringify({
				email: email,
				password_hash: passwordHash
		})
        });

		const payload = {
			email: email,
			password_hash: passwordHash
		};

		console.log('Payload to send:', payload);
		console.log('Payload JSON:', JSON.stringify(payload));

        // Process API response
        const responseData = await response.text();
        
        if (responseData.startsWith('{')) {
            const authData = JSON.parse(responseData);
            if (authData.auth_key) {
                // Store authentication credentials
                localStorage.setItem('authKey', authData.auth_key);
                localStorage.setItem('userId', authData.userid);
                localStorage.setItem('userEmail', email);
                localStorage.setItem('username', username);
                
                // Redirect to dashboard after successful authentication
                window.location.href = 'Dashboard.html';
            } else {
                throw new Error('Authentication failed');
            }
        } else {
            throw new Error(responseData);
        }
        
    } catch (error) {
        // Handle network or request errors
        console.error('Authentication error:', error);
        errorMessage.textContent = 'Unable to authenticate. Please check your credentials.';
        errorMessage.style.display = 'block';
    }
    
    // Reset UI state
    loginButton.disabled = false;
    loginButton.textContent = '💖 Login';
});