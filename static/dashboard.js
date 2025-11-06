// === LOGOUT FUNCTION ===
function logout() {
    localStorage.removeItem("token"); 
    window.location.href = "/login"; // Redirects to login page
}

// === SEARCH FUNCTION ===
const performSearch = async (searchTerm) => {
    const resultsContainer = document.getElementById('resultsContainer');
    if (!searchTerm) return; // Don't search if the box is empty

    // === NEW CODE START ===
    // 1. Create a card for the user's query
    const queryCard = document.createElement('div');
    queryCard.className = 'user-query-card'; // New CSS class for user's chat bubble
    queryCard.textContent = searchTerm;
    resultsContainer.appendChild(queryCard);
    // === NEW CODE END ===

    resultsContainer.innerHTML += '<p class="system-message">Searching...</p>';
    
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(searchTerm)}`);
        
        const searchingMessage = resultsContainer.querySelector('.system-message:last-child');
        if (searchingMessage) searchingMessage.remove();

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const results = await response.json();

        if (results.length === 0) {
            resultsContainer.innerHTML += '<p class="system-message">No matching situations found.</p>';
        } else {
            results.forEach(item => {
                const card = document.createElement('div');
                card.className = 'result-card'; // This is the bot's answer bubble
                
                let cardHtml = `<h3>${item.situation}</h3>`;
                
                if (item.legal_section) {
                    cardHtml += `<p class="legal-section"><strong>Relevant Section:</strong> ${item.legal_section}</p>`;
                }
                
                cardHtml += `<p><strong>Your Rights:</strong> ${item.rights}</p>`;
                cardHtml += `<p><strong>Best Action:</strong> ${item.best_action}</p>`;
                
                card.innerHTML = cardHtml;
                resultsContainer.appendChild(card);
            });
        }
    } catch (error) {
        console.error("Search failed:", error);
        resultsContainer.innerHTML += '<p class="system-message">An error occurred. Please try again.</p>';
    }
    
    // Scroll to the bottom to show new results
    resultsContainer.scrollTop = resultsContainer.scrollHeight;
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

    // 3. WIRE UP THE ONE AND ONLY SEARCH BAR
    const mainSearchInput = document.getElementById('mainSearchInput');
    const mainSearchButton = document.getElementById('mainSearchButton');
    
    const runSearch = () => {
        const searchTerm = mainSearchInput.value;
        performSearch(searchTerm);
        mainSearchInput.value = ""; // Clear input after search
    };

    mainSearchButton.addEventListener('click', runSearch);
    
    mainSearchInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            runSearch();
        }
    });
});