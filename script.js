/* Java do carrossel*/ 

let slideIndex = 0;
    const slides = document.querySelectorAll('.slide');
    const dots = document.querySelectorAll('.dot');

    // Inicia o carrossel automático
    let autoSlide = setInterval(() => { mudarSlide(1) }, 5000); // Muda a cada 5 segundos

    function mostrarSlide(n) {
        // Reseta o index se passar do limite
        if (n >= slides.length) slideIndex = 0;
        if (n < 0) slideIndex = slides.length - 1;

        // Remove classe ativa de todos
        slides.forEach(slide => slide.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));

        // Adiciona classe ativa no atual
        slides[slideIndex].classList.add('active');
        dots[slideIndex].classList.add('active');
    }

    function mudarSlide(n) {
        clearInterval(autoSlide); // Para o tempo se o usuário clicar
        mostrarSlide(slideIndex += n);
        autoSlide = setInterval(() => { mudarSlide(1) }, 5000); // Reinicia o tempo
    }

    function irParaSlide(n) {
        clearInterval(autoSlide);
        slideIndex = n;
        mostrarSlide(slideIndex);
        autoSlide = setInterval(() => { mudarSlide(1) }, 5000);
    }

    /* FIM do Java do carrossel*/ 