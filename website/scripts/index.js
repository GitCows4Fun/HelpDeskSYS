const tickets = [];
function showTab(tabId) {
	document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
	document.getElementById(tabId).classList.add('active');
}
function createTicket(event) {
	event.preventDefault();
	const title = document.getElementById('title').value.trim();
	const description = document.getElementById('description').value.trim();
	if (!title || !description) return;
	const ticket = { title, description, createdAt: new Date().toLocaleString(), resolved: false };
	tickets.push(ticket);
	document.getElementById('title').value = '';
	document.getElementById('description').value = '';
	alert('Ticket submitted!');
	displayTickets();
	showTab('ticketList');
}
function resolveTicket(index) {
	tickets[index].resolved = true;
	displayTickets();
}
function displayTickets() {
	const ticketContainer = document.getElementById('tickets');
	ticketContainer.innerHTML = '';
	tickets.forEach((ticket, index) => {
	const ticketDiv = document.createElement('div');
	ticketDiv.className = 'ticket' + (ticket.resolved ? ' resolved' : '');
	ticketDiv.innerHTML = `
		<strong>${ticket.title}</strong>
		<p>${ticket.description}</p>
		<small>Submitted on: ${ticket.createdAt}</small><br/>
		${ticket.resolved ? '<em>Resolved</em>' : `<button onclick="resolveTicket(${index})">Resolve</button>`}
	`;
	ticketContainer.appendChild(ticketDiv);
	});
	document.getElementById('ticketCount').textContent = tickets.length;
}
function logout() {
	alert('You have been logged out.');
	window.location.href = 'login.html';
}