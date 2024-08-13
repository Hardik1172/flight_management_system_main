document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    const resultsContainer = document.getElementById('search-results');

    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(searchForm);

        fetch('/search/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            resultsContainer.innerHTML = '<h2>Search Results</h2>';
            if (data.flights.length === 0) {
                resultsContainer.innerHTML += '<p>No flights found matching your criteria.</p>';
            } else {
                const list = document.createElement('div');
                list.className = 'list-group';
                data.flights.forEach(flight => {
                    list.innerHTML += `
                        <a href="/book/${flight.id}/" class="list-group-item list-group-item-action">
                            <div class="d-flex w-100 justify-content-between">
                                <h5 class="mb-1">Flight ${flight.flight_number}: ${flight.origin__city} to ${flight.destination__city}</h5>
                                <small>$${flight.price}</small>
                            </div>
                            <p class="mb-1">Departure: ${new Date(flight.departure_time).toLocaleString()} | Arrival: ${new Date(flight.arrival_time).toLocaleString()}</p>
                            <small>Available Seats: ${flight.available_seats}</small>
                        </a>
                    `;
                });
                resultsContainer.appendChild(list);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultsContainer.innerHTML = '<p>An error occurred while searching for flights. Please try again.</p>';
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}