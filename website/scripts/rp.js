function resetPassword(event) {
	event.preventDefault();
	const username = document.getElementById('username').value.trim();
	const newPassword = document.getElementById('newPassword').value;
	const confirmNewPassword = document.getElementById('confirmNewPassword').value;
	if (newPassword !== confirmNewPassword) {
		alert('Passwords do not match!');
		return;
	}
	alert(`Password reset for ${username}`);
	window.location.href = 'login.html';
}