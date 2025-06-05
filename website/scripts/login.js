<<<<<<< HEAD

// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8008';

// Utility function to generate SHA256 hash
async function generateSHA256(message) {
	const msgBuffer = new TextEncoder().encode(message);
	const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
	const hashArray = Array.from(new Uint8Array(hashBuffer));
	const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
	return hashHex;
}

// Save current user session and authentication key
function saveCurrentUser(userInfo) {
	sessionStorage.setItem('currentUser', JSON.stringify(userInfo));
}

// API login function
async function loginUser(email, password) {
	try {
		const passwordHash = await generateSHA256(password);
		
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

		if (response.status === 200) {
			const result = await response.json();
			return {
				success: true,
				data: result
			};
		} else if (response.status === 400) {
			return {
				success: false,
				error: 'Invalid credentials provided'
			};
		} else if (response.status === 401) {
			return {
				success: false,
				error: 'Authentication failed'
			};
		} else {
			return {
				success: false,
				error: `Server error: ${response.status}`
			};
		}
	} catch (error) {
		return {
			success: false,
			error: 'Network error: Unable to connect to server'
		};
	}
}

document.getElementById('loginForm').addEventListener('submit', async function(e) {
	e.preventDefault();
	
	const username = document.getElementById('username').value.trim();
	const password = document.getElementById('password').value;
	const errorMessage = document.getElementById('errorMessage');
	
	// Hide any previous error messages
	errorMessage.style.display = 'none';
	
	// Disable submit button during login attempt
	const submitButton = e.target.querySelector('button[type="submit"]');
	submitButton.disabled = true;
	submitButton.textContent = 'Logging in...';
	
	// For demo purposes, treat username as email if it contains @, otherwise append domain
	const email = username.includes('@') ? username : `${username}@helpdesk.com`;
	
	const loginResult = await loginUser(email, password);
	
	if (loginResult.success) {
		// Store user session with authentication key
		const userInfo = {
			email: email,
			username: username,
			userId: loginResult.data.userid,
			authKey: loginResult.data.key,
			loginTime: new Date().getTime()
		};
		
		saveCurrentUser(userInfo);
		window.location.href = 'Dashboard.html';
	} else {
		errorMessage.textContent = loginResult.error;
		errorMessage.style.display = 'block';
		
		// Hide error message after 5 seconds
		setTimeout(() => {
			errorMessage.style.display = 'none';
		}, 5000);
	}
	
	// Re-enable submit button
	submitButton.disabled = false;
	submitButton.textContent = 'Login';
});