document.addEventListener('DOMContentLoaded', function() {
    const closeAlertBtn = document.getElementById('closeAlert');
    const alertBox = document.querySelector('.alert');

    closeAlertBtn.addEventListener('click', function() {
        alertBox.style.display = 'none'; // Oculta el mensaje de alerta
    });
});
