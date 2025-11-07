const pinIcons = document.querySelectorAll('.pin-icon');

let pinned = [];
pinned = JSON.parse(localStorage.getItem('pinnedMovies')) || [];


globalThis.addEventListener('DOMContentLoaded', () => {
    for (const icon of pinIcons) {
        const movieId = icon.dataset.movieId;
        if (pinned.includes(movieId)) {
            icon.src = '/static/images/push-pin-fill.png';
            const movieContainer = icon.closest('.film-container');
            movieContainer.classList.add('pinned');
        } else {
            icon.src = '/static/images/push-pin.png';        
        }
    }
});

for (const icon of pinIcons) {
    icon.addEventListener('click', () => {

        const movieId = icon.dataset.movieId;
        const movieContainer = icon.closest('.film-container');

        if (icon.src.endsWith('push-pin.png')) {
            icon.src = '/static/images/push-pin-fill.png';
            movieContainer.classList.add('pinned');
            if (!pinned.includes(movieId)) {
                pinned.push(movieId);
            }
        } else {
            icon.src = '/static/images/push-pin.png';
            movieContainer.classList.remove('pinned');
            pinned = pinned.filter(id => id !== movieId);
        }

        localStorage.setItem('pinnedMovies', JSON.stringify(pinned));
    });
}

