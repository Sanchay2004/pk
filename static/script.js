document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.recommendation-form');
    const recommendationList = document.getElementById('recommendation-list');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        const formData = new FormData(form);
        const category = formData.get('category');
        const zone = formData.get('zone');

        // Make an AJAX request to fetch recommendations based on category and zone
        fetch('/', {
            method: 'POST',
            body: new URLSearchParams({ category: category, zone: zone }),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Clear previous recommendations
            recommendationList.innerHTML = '';

            // Append new recommendations to the list
            data.recommendations.forEach(recommendation => {
                const li = document.createElement('li');
                li.textContent = `${recommendation['steel supplier']} - ${recommendation['city']}, ${recommendation['state']} - Price: ${recommendation['price/kg(rupee)']} RS, Reliability Score: ${recommendation['reliability_score']}`;
                recommendationList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error fetching recommendations:', error);
        });
    });
});
