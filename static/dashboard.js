// === LOGOUT FUNCTION ===
function logout() {
    localStorage.removeItem("token"); 
    window.location.href = "/login";
}

// === SEARCH FUNCTION ===
// This function will be called by all search buttons
const performSearch = async (searchTerm) => {
    const resultsContainer = document.getElementById('resultsContainer');
    if (!searchTerm) return; // Don't search if the box is empty

    resultsContainer.innerHTML = '<p>Searching...</p>';
    
    // Call the /api/search endpoint
    const response = await fetch(`/api/search?q=${encodeURIComponent(searchTerm)}`);
    const results = await response.json();

    resultsContainer.innerHTML = ''; // Clear "Searching..."

    if (results.length === 0) {
        resultsContainer.innerHTML = '<p>No matching situations found.</p>';
    } else {
        results.forEach(item => {
            // Create result card elements dynamically
            const card = document.createElement('div');
            card.className = 'result-card'; // You can style '.result-card' in your CSS
            
            let cardHtml = `<h3>${item.situation}</h3>`;
            
            if (item.legal_section) {
                // Use the 'legal-section' class from your CSS
                cardHtml += `<p class="legal-section"><strong>Relevant Section:</strong> ${item.legal_section}</p>`;
            }
            
            cardHtml += `<p><strong>Your Rights:</strong> ${item.rights}</p>`;
            cardHtml += `<p><strong>Best Action:</strong> ${item.best_action}</p>`;
            
            card.innerHTML = cardHtml;
            resultsContainer.appendChild(card);
        });
    }
};

// === RUNS WHEN THE PAGE IS LOADED ===
document.addEventListener('DOMContentLoaded', () => {
    
    const token = localStorage.getItem('token');
    const welcomeHeading = document.getElementById('welcome-heading');
    
    // 1. FETCH USER INFO
    if (!token) {
        window.location.href = '/login'; // If no token, kick to login
        return;
    }

    fetch('/user-info', {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(response => {
        if (response.status === 401 || response.status === 422) {
            logout(); // If token is bad, kick to login
        }
        return response.json();
    })
    .then(data => {
        if (data.username) {
            welcomeHeading.textContent = `Welcome, ${data.username}!`;
        }
    })
    .catch(error => {
        console.error('Error fetching user info:', error);
        logout();
    });

    // 2. WIRE UP LOGOUT BUTTON
    document.getElementById('logoutButton').addEventListener('click', logout);

    // 3. WIRE UP ALL SEARCH BUTTONS
    
    // Left panel search
    const mainSearchInput = document.getElementById('mainSearchInput');
    const mainSearchButton = document.getElementById('mainSearchButton');
    mainSearchButton.addEventListener('click', () => {
        performSearch(mainSearchInput.value);
    });
    mainSearchInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') performSearch(mainSearchInput.value);
    });

    // Center panel (preset buttons)
    document.querySelectorAll('.buttons button').forEach(button => {
        button.addEventListener('click', () => {
            const searchTerm = button.getAttribute('data-search');
            performSearch(searchTerm);
            // Optional: scroll to results
            document.getElementById('search-panel').scrollIntoView({ behavior: 'smooth' });
        });
    });

    // Center panel (search bar)
    const centerSearchInput = document.getElementById('centerSearchInput');
    centerSearchInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            performSearch(centerSearchInput.value);
            // Optional: scroll to results
            document.getElementById('search-panel').scrollIntoView({ behavior: 'smooth' });
        }
    });
});