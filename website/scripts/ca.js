function createAccount(event) {
  event.preventDefault();
  const email = document.getElementById('username').value.trim().toLowerCase();
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirmPassword').value;

  if (!email.endsWith('@gmail.com')) {
    alert('Only Gmail addresses are allowed.');
    return;
  }

  if (password !== confirmPassword) {
    alert('Passwords do not match!');
    return;
  }

  let users = JSON.parse(localStorage.getItem('users') || '{}');

  if (users[email]) {
    alert('An account with this Gmail already exists.');
    return;
  }

  users[email] = { password };
  localStorage.setItem('users', JSON.stringify(users));

  alert(`Account created for ${email}`);
  window.location.href = 'login.html'; // Corrected to .html
}
