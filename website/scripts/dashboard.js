
// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8008';

// Load authentication data from localStorage (matching login.js implementation)
function getAuthKey() {
	return localStorage.getItem('authKey');
}

function getUserData() {
	return {
		authKey: localStorage.getItem('authKey'),
		userId: localStorage.getItem('userId'),
		username: localStorage.getItem('username'),
		email: localStorage.getItem('userEmail')
	};
}

// Check if user is authenticated and redirect if not
const authKey = getAuthKey();
const userData = getUserData();

// Add debugging to see what values we have
console.log('Auth Key:', authKey);
console.log('User Data:', userData);
console.log('Username specifically:', userData.username);

if (!authKey || !userData.username) {
    console.log('Authentication failed - redirecting to login');
    // Clear any invalid authentication data
    localStorage.clear();
    window.location.href = 'login.html';
} else {
	// Display user welcome message
	document.getElementById('userWelcome').textContent = `Welcome, ${userData.username}`;
}

// API function to fetch tickets
async function fetchTickets() {
	try {
		console.log('Fetching tickets with auth key:', authKey);
		
		const response = await fetch(`${API_BASE_URL}/api/0/GET/data`, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({
				key: authKey
			})
		});

		console.log('Fetch tickets response status:', response.status);
		
		if (response.status === 200) {
			const responseText = await response.text();
			console.log('Raw response:', responseText);
			
			let tickets;
			try {
				tickets = JSON.parse(responseText);
			} catch (parseError) {
				console.error('Failed to parse tickets response:', parseError);
				return { success: false, error: 'Invalid response format from server' };
			}
			
			console.log('Parsed tickets:', tickets);
			return { success: true, data: tickets };
		} else if (response.status === 401) {
			console.log('Authentication expired during ticket fetch');
			localStorage.removeItem('authKey');
			localStorage.removeItem('userId');
			localStorage.removeItem('username');
			localStorage.removeItem('userEmail');
			window.location.href = 'Login.html';
			return { success: false, error: 'Session expired' };
		} else {
			const errorText = await response.text();
			console.error('Server error fetching tickets:', response.status, errorText);
			return { success: false, error: `Server error: ${response.status}` };
		}
	} catch (error) {
		console.error('Network error fetching tickets:', error);
		return { success: false, error: 'Network error: Unable to connect to server' };
	}
}

// API function to create a new ticket
async function fetchTickets() {
	try {
		console.log('Fetching tickets with auth key:', authKey);

		// Encode key in the query string
		const encodedKey = encodeURIComponent(authKey);
		const url = `${API_BASE_URL}/api/0/GET/data?key=${encodedKey}`;

		const response = await fetch(url, {
			method: 'GET',
			headers: {
				'Accept': 'application/json',
			}
		});

		console.log('Fetch tickets response status:', response.status);

		if (response.status === 200) {
			const responseText = await response.text();
			console.log('Raw response:', responseText);

			let tickets;
			try {
				tickets = JSON.parse(responseText);
			} catch (parseError) {
				console.error('Failed to parse tickets response:', parseError);
				return { success: false, error: 'Invalid response format from server' };
			}

			console.log('Parsed tickets:', tickets);
			return { success: true, data: tickets };
		} else if (response.status === 401) {
			console.log('Authentication expired during ticket fetch');
			localStorage.clear();
			window.location.href = 'Login.html';
			return { success: false, error: 'Session expired' };
		} else {
			const errorText = await response.text();
			console.error('Server error fetching tickets:', response.status, errorText);
			return { success: false, error: `Server error: ${response.status}` };
		}
	} catch (error) {
		console.error('Network error fetching tickets:', error);
		return { success: false, error: 'Network error: Unable to connect to server' };
	}
}


// Initialize tickets array
let tickets = [];

// Load tickets from API
async function loadTickets() {
	const result = await fetchTickets();
	if (result.success) {
		tickets = Array.isArray(result.data) ? result.data : [];
	} else {
		console.error('Failed to load tickets:', result.error);
		tickets = [];
	}
	renderTickets();
	updateStats();
}

// Update statistics
function updateStats() {
	const total = tickets.length;
	const open = tickets.filter(t => t.status === 'open' || t.status === 'pending').length;
	const inProgress = tickets.filter(t => t.status === 'in-progress' || t.status === 'working').length;
	const resolved = tickets.filter(t => t.status === 'resolved' || t.status === 'closed').length;

	document.getElementById('totalTickets').textContent = total;
	document.getElementById('openTickets').textContent = open;
	document.getElementById('inProgressTickets').textContent = inProgress;
	document.getElementById('resolvedTickets').textContent = resolved;
}

// Render tickets table
function renderTickets() {
	const tbody = document.getElementById('ticketsTableBody');
	
	if (tickets.length === 0) {
		tbody.innerHTML = `
			<tr>
				<td colspan="6" class="empty-state">
					<h3>No tickets found</h3>
					<p>Create your first support ticket to get started</p>
				</td>
			</tr>
		`;
		return;
	}

	tbody.innerHTML = tickets.map((ticket, index) => {
		const ticketId = ticket.id || (index + 1);
		const status = ticket.status || 'open';
		const priority = ticket.priority || 'medium';
		const created = ticket.created || ticket.date_created || new Date().toLocaleDateString();
		
		return `
			<tr>
				<td>#${ticketId}</td>
				<td>${ticket.title || ticket.subject || 'Untitled'}</td>
				<td><span class="priority-${priority}">${priority.toUpperCase()}</span></td>
				<td><span class="status-badge status-${status}">${status.replace('-', ' ')}</span></td>
				<td>${created}</td>
				<td>
					<div class="action-buttons">
						<button class="action-btn btn-view" onclick="viewTicket(${index})">View</button>
					</div>
				</td>
			</tr>
		`;
	}).join('');
}

// Open add ticket modal
function openAddTicketModal() {
	document.getElementById('addTicketModal').style.display = 'block';
}

// Close add ticket modal
function closeAddTicketModal() {
	document.getElementById('addTicketModal').style.display = 'none';
	document.getElementById('addTicketForm').reset();
}

// Add new ticket
document.getElementById('addTicketForm').addEventListener('submit', async function(e) {
	e.preventDefault();
	
	const formData = new FormData(e.target);
	const title = formData.get('subject');
	const description = formData.get('description');
	
	// Disable submit button during creation
	const submitButton = e.target.querySelector('button[type="submit"]');
	submitButton.disabled = true;
	submitButton.textContent = 'Creating...';
	
	const result = await createTicket(title, description);
	
	if (result.success) {
		closeAddTicketModal();
		// Reload tickets from server
		await loadTickets();
	} else {
		alert(`Failed to create ticket: ${result.error}`);
	}
	
	// Re-enable submit button
	submitButton.disabled = false;
	submitButton.textContent = 'Create Ticket';
});

// View ticket
function viewTicket(index) {
	const ticket = tickets[index];
	if (ticket) {
		const ticketId = ticket.id || (index + 1);
		const title = ticket.title || ticket.subject || 'Untitled';
		const status = ticket.status || 'open';
		const description = ticket.description || 'No description available';
		
		alert(`Ticket #${ticketId}\nTitle: ${title}\nStatus: ${status}\nDescription: ${description}`);
	}
}

// Logout function
function logout() {
	if (confirm('Are you sure you want to logout?')) {
		localStorage.removeItem('authKey');
		localStorage.removeItem('userId');
		localStorage.removeItem('username');
		localStorage.removeItem('userEmail');
		window.location.href = 'login';
	}
}

// Close modal when clicking outside
window.onclick = function(event) {
	const modal = document.getElementById('addTicketModal');
	if (event.target === modal) {
		closeAddTicketModal();
	}
}

// Initialize dashboard
loadTickets();