document.getElementById('movieSearch').addEventListener('input', function() {

    const search = this.value.toLowerCase();

    for (const card of document.querySelectorAll('.film-container')) {
        const title = card.querySelector('.titreFilm').textContent.toLowerCase();
        card.style.display = title.includes(search) ? '' : 'none';
    }
})