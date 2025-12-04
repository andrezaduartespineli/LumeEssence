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

    /*Java do carrossel de produtos no final da pag*/
    
document.addEventListener("DOMContentLoaded", function() {
        const track = document.getElementById('productTrack');
        const nextBtn = document.getElementById('nextBtn');
        const prevBtn = document.getElementById('prevBtn');

        if (track && nextBtn && prevBtn) {
            
            // Lógica do Botão Direito (Avançar)
            nextBtn.addEventListener('click', () => {
                // Se chegou no fim, volta para o começo (Loop)
                const maxScroll = track.scrollWidth - track.clientWidth;
                if (track.scrollLeft >= maxScroll - 10) { // -10 é uma margem de segurança
                    track.scrollTo({ left: 0, behavior: 'smooth' });
                } else {
                    track.scrollBy({ left: 300, behavior: 'smooth' });
                }
            });

            // Lógica do Botão Esquerdo (Voltar)
            prevBtn.addEventListener('click', () => {
                // Se está no começo (0), vai para o fim (Loop)
                if (track.scrollLeft === 0) {
                    track.scrollTo({ left: track.scrollWidth, behavior: 'smooth' });
                } else {
                    track.scrollBy({ left: -300, behavior: 'smooth' });
                }
            });

        } else {
            console.error("Erro: Elementos do carrossel não encontrados.");
        }
    });

    /* Fim do carrossel de produtos no final da pag*/

    /* Java carrossel sobre*/

document.addEventListener("DOMContentLoaded", function() {
        const track = document.getElementById('storyTrack');
        const nextBtn = document.getElementById('btnNextStory');
        const prevBtn = document.getElementById('btnPrevStory');
        const indicators = document.querySelectorAll('.indicator');
        let currentIndex = 0;

        function updateCarousel() {
            // Move o carrossel (100% da largura por vez)
            track.style.transform = `translateX(-${currentIndex * 100}%)`;
            
            // Atualiza as barrinhas
            indicators.forEach((ind, i) => {
                if (i === currentIndex) ind.classList.add('active');
                else ind.classList.remove('active');
            });
        }

        if (track && nextBtn && prevBtn) {
            nextBtn.addEventListener('click', () => {
                // Se for o último, volta pro primeiro (0), senão soma 1
                currentIndex = (currentIndex === indicators.length - 1) ? 0 : currentIndex + 1;
                updateCarousel();
            });

            prevBtn.addEventListener('click', () => {
                // Se for o primeiro, vai pro último, senão subtrai 1
                currentIndex = (currentIndex === 0) ? indicators.length - 1 : currentIndex - 1;
                updateCarousel();
            });
        }
    });
    /* Fim do java carrossel sobre*/

  /* Java da pagina de detalhes dos produto*/
// Trocar imagem da galeria
        
function changeImage(element) {
            // Troca a imagem grande
            document.getElementById('mainImage').src = element.src;
            
            // Remove a classe 'active' de todas as thumbs
            document.querySelectorAll('.thumb').forEach(thumb => thumb.classList.remove('active'));
            
            // Adiciona na clicada
            element.classList.add('active');
        }

        // Alterar Quantidade
        function updateQty(change) {
            const input = document.getElementById('productQty');
            let value = parseInt(input.value);
            value = value + change;
            if (value < 1) value = 1;
            input.value = value;
        }

   /* Fim Java da pagina de detalhes dos produto*/

   /* Java da pagina de Checkout */
   
   function selectPayment(method) {
            // Esconde todos
            document.getElementById('credit-content').style.display = 'none';
            document.getElementById('pix-content').style.display = 'none';
            
            // Remove classe active dos botões
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

            // Mostra o selecionado
            if (method === 'credit') {
                document.getElementById('credit-content').style.display = 'block';
                event.currentTarget.classList.add('active'); // Adiciona active no botão clicado
            } else {
                document.getElementById('pix-content').style.display = 'block';
                event.currentTarget.classList.add('active');
            }
        }
      
  /* Fim da pagina de Checkout */    
  
  /* Java do modal de newsletter */

    document.addEventListener("DOMContentLoaded", function() {
        const modal = document.getElementById('newsletter-modal');
        const closeBtn = document.getElementById('close-modal');
        const form = document.querySelector('.newsletter-form');

        // Verifica se o usuário já viu/fechou o modal anteriormente
        // Se NÃO tiver a marcação no navegador, executa
        if (!localStorage.getItem('lumeEssencePopupClosed')) {
            
            // Espera 2.5 segundos para mostrar o modal (menos intrusivo)
            setTimeout(() => {
                modal.style.display = 'flex';
                // Pequeno delay para permitir a transição CSS funcionar
                setTimeout(() => {
                    modal.classList.add('active');
                }, 10);
            }, 2500);
        }

        // Função para fechar o modal
        function closeModal() {
            modal.classList.remove('active');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 500); // Espera a animação de fade-out terminar
            
            // Salva no navegador que o usuário fechou, para não mostrar de novo
            localStorage.setItem('lumeEssencePopupClosed', 'true');
        }

        // Eventos de clique para fechar
        closeBtn.addEventListener('click', closeModal);
        
        // Fecha se clicar fora da caixinha branca
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });

        // Opcional: Feedback ao enviar o formulário
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            // Aqui você colocaria a lógica real de envio (PHP/JS)
            alert('Bem-vindo(a) à Lume Essence! Seu cupom é: LUME10');
            closeModal();
        });
    });
/* FIm Java do modal de newsletter */