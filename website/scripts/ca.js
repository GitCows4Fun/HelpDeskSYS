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

// API function to create new user
async function createNewUser(email, password, firstName, lastName) {
	try {
		const passwordHash = await generateSHA256(password);
		const commonName = `${firstName} ${lastName}`.trim();
		
		const response = await fetch(`${API_BASE_URL}/api/0/POST/newuser`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				email: email,
				pw_hash: passwordHash,
				commonName: commonName
			})
		});

		if (response.status === 201) {
			return { success: true };
		} else if (response.status === 400) {
			return { success: false, error: 'Invalid user data provided or user already exists' };
		} else if (response.status === 403) {
			return { success: false, error: 'Request blocked for security reasons' };
		} else {
			return { success: false, error: `Server error: ${response.status}` };
		}
	} catch (error) {
		return { success: false, error: 'Network error: Unable to connect to server' };
	}
}

// Wait for DOM to be fully loaded before setting up event listeners
document.addEventListener('DOMContentLoaded', function() {
	// Get form elements
	const form = document.getElementById('signupForm');
	const submitBtn = document.getElementById('submitBtn');
	const errorMessage = document.getElementById('errorMessage');
	const successMessage = document.getElementById('successMessage');

	// Validation functions
	function validateEmail(email) {
		const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		return re.test(email);
	}

	function validatePassword(password) {
		const requirements = {
			length: password.length >= 6,
			uppercase: /[A-Z]/.test(password),
			lowercase: /[a-z]/.test(password),
			number: /\d/.test(password)
		};
		return requirements;
	}

	function updatePasswordStrength(password) {
		const requirements = validatePassword(password);
		const strengthFill = document.getElementById('strengthFill');
		
		// Update requirement indicators
		document.getElementById('req-length').className = requirements.length ? 'valid' : 'invalid';
		document.getElementById('req-uppercase').className = requirements.uppercase ? 'valid' : 'invalid';
		document.getElementById('req-lowercase').className = requirements.lowercase ? 'valid' : 'invalid';
		document.getElementById('req-number').className = requirements.number ? 'valid' : 'invalid';

		// Calculate strength
		const validCount = Object.values(requirements).filter(Boolean).length;
		const strengthPercent = (validCount / 4) * 100;
		
		strengthFill.style.width = strengthPercent + '%';
		
		// Set strength class - Clear previous classes first
		strengthFill.className = 'strength-fill';
		if (validCount === 1) strengthFill.classList.add('strength-weak');
		else if (validCount === 2) strengthFill.classList.add('strength-fair');
		else if (validCount === 3) strengthFill.classList.add('strength-good');
		else if (validCount === 4) strengthFill.classList.add('strength-strong');

		// Return true only if ALL requirements are met
		return validCount === 4;
	}

	function updateFeedback(elementId, isValid) {
		const feedback = document.getElementById(elementId);
		if (feedback) {
			feedback.textContent = isValid ? '✓' : '✗';
			feedback.className = 'input-feedback ' + (isValid ? 'valid' : 'invalid');
		}
	}

	// Improved form validation function with better logic flow
	function checkFormValidity() {
		// Get current form values
		const firstName = document.getElementById('firstName').value.trim();
		const lastName = document.getElementById('lastName').value.trim();
		const email = document.getElementById('email').value.trim();
		const username = document.getElementById('username').value.trim();
		const password = document.getElementById('password').value;
		const confirmPassword = document.getElementById('confirmPassword').value;
		const role = document.getElementById('role').value;

		// Validate each field individually
		const isFirstNameValid = firstName.length > 0;
		const isLastNameValid = lastName.length > 0;
		const isEmailValid = validateEmail(email);
		const isUsernameValid = username.length >= 3;
		
		// Password validation - this is the key fix
		const isPasswordValid = updatePasswordStrength(password);
		
		// Confirm password validation - check both that passwords match AND that original password is valid
		const isConfirmPasswordValid = password === confirmPassword && password.length > 0 && isPasswordValid;
		
		const isRoleValid = role !== '';

		// Update feedback for each field
		updateFeedback('firstNameFeedback', isFirstNameValid);
		updateFeedback('lastNameFeedback', isLastNameValid);
		updateFeedback('emailFeedback', isEmailValid);
		updateFeedback('usernameFeedback', isUsernameValid);
		updateFeedback('passwordFeedback', isPasswordValid);
		updateFeedback('confirmPasswordFeedback', isConfirmPasswordValid);

		// Check if entire form is valid
		const isFormValid = isFirstNameValid && isLastNameValid && isEmailValid && 
							isUsernameValid && isPasswordValid && isConfirmPasswordValid && isRoleValid;

		// Enable/disable submit button
		submitBtn.disabled = !isFormValid;
		
		// Debug logging to help troubleshoot (remove in production)
		console.log('Form Validation Status:', {
			firstName: isFirstNameValid,
			lastName: isLastNameValid,
			email: isEmailValid,
			username: isUsernameValid,
			password: isPasswordValid,
			confirmPassword: isConfirmPasswordValid,
			role: isRoleValid,
			formValid: isFormValid
		});

		return isFormValid;
	}

	// Add event listeners with debouncing to prevent excessive validation calls
	let validationTimeout;
	function debouncedValidation() {
		clearTimeout(validationTimeout);
		validationTimeout = setTimeout(checkFormValidity, 100); // Wait 100ms after last input
	}

	// Event listeners for real-time validation
	['firstName', 'lastName', 'email', 'username', 'password', 'confirmPassword', 'role'].forEach(id => {
		const element = document.getElementById(id);
		if (element) {
			element.addEventListener('input', debouncedValidation);
			// Also check on blur to catch cases where user tabs through fields
			element.addEventListener('blur', checkFormValidity);
		}
	});

	// Initial validation check
	checkFormValidity();

	// Form submission
	form.addEventListener('submit', async function(e) {
		e.preventDefault();
		
		// Double-check form validity before submission
		if (!checkFormValidity()) {
			errorMessage.textContent = 'Please complete all required fields correctly.';
			errorMessage.style.display = 'block';
			successMessage.style.display = 'none';
			return;
		}
		
		const formData = new FormData(form);
		const firstName = formData.get('firstName').trim();
		const lastName = formData.get('lastName').trim();
		const email = formData.get('email').trim();
		const password = formData.get('password');
		
		// Disable submit button during account creation
		const submitButton = e.target.querySelector('button[type="submit"]');
		submitButton.disabled = true;
		submitButton.textContent = 'Requesting Account...';
		
		// Hide any previous messages
		errorMessage.style.display = 'none';
		successMessage.style.display = 'none';
		
		const result = await createNewUser(email, password, firstName, lastName);
		
		if (result.success) {
			// Show success message
			successMessage.textContent = 'Account creation successfully requested! Redirecting to login...';
			successMessage.style.display = 'block';
			errorMessage.style.display = 'none';

			// Redirect to login page after 2 seconds
			setTimeout(() => {
				window.location.href = 'login';
			}, 2000);
		} else {
			errorMessage.textContent = result.error;
			errorMessage.style.display = 'block';
			successMessage.style.display = 'none';
			
			// Re-enable submit button
			submitButton.disabled = false;
			submitButton.textContent = 'Create Account';
		}
	});
});