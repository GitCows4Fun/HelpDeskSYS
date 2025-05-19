function createAccount(event) {
	event.preventDefault();
	const email = document.getElementById('email').value.trim();
	const password = document.getElementById('password').value;
	const confirmPassword = document.getElementById('confirmPassword').value;
	if (password !== confirmPassword) {
		alert('Passwords do not match!');
		return;
	}
	alert(`Account created for ${email}`);
	window.location.href = 'login.html';
}