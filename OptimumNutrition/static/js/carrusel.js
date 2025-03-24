let slideIndex = 0;
let autoSlide = true;
const slides = document.querySelector(".carousel-slide");
const totalSlides = document.querySelectorAll(".carousel-slide img").length;
const pauseButton = document.querySelector(".pause");

const titles = [
    "WHEY PROTEIN",
    "LA MEJOR CALIDAD",
    "MULTIPLES SABORES"
];

const descriptions = [
    "Completa tu requerimiento proteico de la forma mas deliciosa.",
    "Con 24 gramos por servicio, ofrecemos la mejor calidad garantizada.",
    "Nuestros sabores haran que jamas te aburras de tomarlos."
];

function showSlide(index) {
    if (index >= totalSlides) slideIndex = 0;
    if (index < 0) slideIndex = totalSlides - 1;

    slides.style.transform = `translateX(-${slideIndex * 100}vw)`;
    document.getElementById("carousel-title").textContent = titles[slideIndex];
    document.getElementById("carousel-description").textContent = descriptions[slideIndex];
}

function nextSlide() {
    slideIndex++;
    showSlide(slideIndex);
}

function prevSlide() {
    slideIndex--;
    showSlide(slideIndex);
}

let slideInterval = setInterval(nextSlide, 5000);

document.querySelector(".next").addEventListener("click", () => {
    nextSlide();
    resetInterval();
});

document.querySelector(".prev").addEventListener("click", () => {
    prevSlide();
    resetInterval();
});

pauseButton.addEventListener("click", () => {
    if (autoSlide) {
        clearInterval(slideInterval);
        pauseButton.innerHTML = "▶";
    } else {
        slideInterval = setInterval(nextSlide, 5000);
        pauseButton.innerHTML = "⏸";
    }
    autoSlide = !autoSlide;
});

function resetInterval() {
    clearInterval(slideInterval);
    if (autoSlide) {
        slideInterval = setInterval(nextSlide, 5000);
    }
}
