let selectedRating = 0;

function highlightStars(rating) {
    const stars = document.getElementById('star-rating').children;
    for (let i = 0; i < stars.length; i++) {
        stars[i].style.color = (i < rating) ? 'gold' : 'gray';
    }
}

function setRating(rating) {
    selectedRating = rating;
    highlightStars(rating);

    document.getElementById('hiddenRatingInput').value = selectedRating;
}

function openReviewModal() {
    document.getElementById('reviewModal').classList.remove('hidden');
}

function closeReviewModal() {
    document.getElementById('reviewModal').classList.add('hidden');
}

function submitReview() {
    if (selectedRating === 0) {
        alert('Por favor, selecciona tu calificación antes de enviar la reseña.');
        return;
    }
    alert(`Tu reseña de ${selectedRating} estrellas se ha enviado.`);
}

document.getElementById('reviewModal').querySelector('form').onsubmit = function() {
    if (selectedRating === 0) {
        alert('Por favor, selecciona tu calificación antes de enviar la reseña.');
        return false;
    }
    alert(`Tu reseña de ${selectedRating} estrellas se ha enviado.`);
};