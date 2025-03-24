function toggleModal(tipo) {
    const modal = document.getElementById('modal');
    modal.querySelector('h2').textContent = tipo === 'debito' ? 'Nueva tarjeta de débito' : 'Nueva tarjeta de crédito';
    document.getElementById('tipo-tarjeta').value = tipo;
    modal.classList.toggle('hidden');
}

function guardarTarjeta(event) {
    event.preventDefault();
    const formData = new FormData(document.getElementById('tarjetaForm'));

    fetch('/guardar_tarjeta', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            window.location.reload();
        } else {
            alert('Hubo un problema al guardar la tarjeta');
        }
    })
    .catch(error => console.error('Error:', error));
}