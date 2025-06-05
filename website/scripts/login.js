function login(event) {
  event.preventDefault();

  const email = document.getElementById('username').value.trim().toLowerCase();
  const password = document.getElementById('password').value;

  const usersJSON = localStorage.getItem('users');
  console.log('users JSON from localStorage:', usersJSON);
  
  if (!usersJSON) {
	alert('No users found. Please create an account first.');
	return;
  }
  console.log('Parsed users object:', users);

  if (!users[email]) {
    alert('No account found with that Gmail address.');
    return;
  }

  if (users[email].password !== password) {
    alert('Incorrect password.');
    return;
  }

  alert(`Login successful! Welcome, ${email}`);
  localStorage.setItem('loggedInUser', email);
  const users = JSON.parse(localStorage.getItem('users') || '{}');
users[email] = password;
localStorage.setItem('users', JSON.stringify(users));

  window.location.href = '../index.html';
}
