
// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8008';

// Load current user from sessionStorage
function getCurrentUser() {
    const currentUserData = sessionStorage.getItem('currentUser');
    return currentUserData ? JSON.parse(currentUserData) : null;
}

// Check if authentication key has expired (5 minutes as per API spec)
function isAuthKeyExpired(user) {
    if (!user || !user.loginTime) return true;
    const currentTime = new Date().getTime();
    const fiveMinutes = 5 * 60 * 1000; // 5 minutes in milliseconds
    return (currentTime - user.loginTime) > fiveMinutes;
}

// Check if user is logged in and redirect if not
const currentUser = getCurrentUser();
if (!currentUser || isAuthKeyExpired(currentUser)) {
    sessionStorage.removeItem('currentUser');
    window.location.href = 'Login.html';
} else {
    // Display user welcome message
    document.getElementById('userWelcome').textContent = `Welcome, ${currentUser.username}`;
}

// API function to fetch tickets
async function fetchTickets() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/0/GET/data`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                key: currentUser.authKey
            })
        });

        if (response.status === 200) {
            const tickets = await response.json();
            return { success: true, data: tickets };
        } else if (response.status === 401) {
            // Authentication expired
            sessionStorage.removeItem('currentUser');
            window.location.href = 'Login.html';
            return { success: false, error: 'Session expired' };
        } else {
            return { success: false, error: `Server error: ${response.status}` };
        }
    } catch (error) {
        return { success: false, error: 'Network error: Unable to connect to server' };
    }
}

// API function to create a new ticket
async function createTicket(title, description) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/0/POST/data`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title: title,
                description: description,
                key: currentUser.authKey
            })
        });

        if (response.status === 201) {
            return { success: true };
        } else if (response.status === 401) {
            // Authentication expired
            sessionStorage.removeItem('currentUser');
            window.location.href = 'Login.html';
            return { success: false, error: 'Session expired' };
        } else if (response.status === 400) {
            return { success: false, error: 'Invalid ticket data provided' };
        } else if (response.status === 403) {
            return { success: false, error: 'Request blocked for security reasons' };
        } else {
            return { success: false, error: `Server error: ${response.status}` };
        }
    } catch (error) {
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
        sessionStorage.removeItem('currentUser');
        window.location.href = 'Login.html';
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