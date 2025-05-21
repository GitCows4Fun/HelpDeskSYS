function login(event) {
	event.preventDefault();
	const username = document.getElementById('username').value;
	alert(`Attempted login with Username: ${username}`);
	window.location.href = "../";
}