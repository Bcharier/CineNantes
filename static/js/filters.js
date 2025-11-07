const theaterFilters = document.querySelectorAll('.theater-filter');

for (const button of theaterFilters) {
    button.addEventListener('click', () => {
        button.classList.toggle('active');
        filterShowtimesByTheater();
    });
}

function filterShowtimesByTheater() {
    const activeTheaters = Array.from(theaterFilters)
        .filter(button => button.classList.contains('active'))
        .map(button => button.textContent);

    console.log("Active theaters:", activeTheaters);

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
