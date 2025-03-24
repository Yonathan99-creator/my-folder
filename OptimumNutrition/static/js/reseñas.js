document.addEventListener('DOMContentLoaded', function() {
    const reviews = document.querySelectorAll('.review-item');
    const loadMoreButton = document.getElementById('load-more');
    let reviewsShown = 0;
    const reviewsPerPage = 3;

    function showReviews() {
        // Calcular el índice máximo de reseñas que se deben mostrar
        const nextReviewsToShow = Math.min(reviewsShown + reviewsPerPage, reviews.length);

        // Mostrar reseñas hasta el índice calculado
        for (let i = reviewsShown; i < nextReviewsToShow; i++) {
            reviews[i].classList.remove('hidden');
        }

        reviewsShown = nextReviewsToShow;

        // Ocultar el botón si no hay más reseñas para mostrar
        if (reviewsShown >= reviews.length) {
            loadMoreButton.style.display = 'none';
        }
    }

    // Mostrar inicialmente el primer conjunto de reseñas
    showReviews();

    // Añadir un evento al botón para mostrar más reseñas
    loadMoreButton.addEventListener('click', function() {
        showReviews();
    });
});