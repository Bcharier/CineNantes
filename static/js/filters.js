const theaterFilters = document.querySelectorAll('.theater-filter');

// Restore selected theaters from localStorage
const savedTheaters = JSON.parse(localStorage.getItem('selectedTheaters') || '[]');
for (const button of theaterFilters) {
    if (savedTheaters.includes(button.textContent)) {
        button.classList.add('active');
    }
}

// Initial filter on page 
filterShowtimesByTheater();

// Add event listeners to theater filter buttons
for (const button of theaterFilters) {
    button.addEventListener('click', () => {
        button.classList.toggle('active');

         // Save selected theaters to localStorage
        const activeTheaters = Array.from(theaterFilters)
            .filter(btn => btn.classList.contains('active'))
            .map(btn => btn.textContent);
        localStorage.setItem('selectedTheaters', JSON.stringify(activeTheaters));
        
        filterShowtimesByTheater();
    });
}

// Function to filter showtimes based on selected theaters
function filterShowtimesByTheater() {
    const activeTheaters = Array.from(theaterFilters)
        .filter(button => button.classList.contains('active'))
        .map(button => button.textContent);

    const seanceContainers = document.querySelectorAll('.seance_container');

    for (const container of seanceContainers) {
        const theater = container.dataset.theater;
        if (activeTheaters.length === 0 || activeTheaters.includes(theater)) {
            container.style.display = 'flex';
        } else {
            container.style.display = 'none';
        }
    }

    const movieCards = document.querySelectorAll('.film-container');
    for (const card of movieCards) {
        const visibleSeances = card.querySelectorAll('.seance_container:not([style*="display: none"])');
        if (visibleSeances.length === 0) {
            card.style.display = 'none';
        } else {
            card.style.display = '';
        }
    }
}


const filterContainer = document.querySelector('.mobile-filter-container');
const filterButton = document.querySelector('.mobile-filter-button');
filterButton.addEventListener('click', () => {
    filterContainer.classList.toggle('visible');
});
