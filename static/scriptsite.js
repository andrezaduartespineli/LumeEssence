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
 
    // Função para trocar as abas (Cartão vs Pix)
    function selectPayment(method) {
        // 1. Reset visual: Esconde tudo e tira a cor dos botões
        document.getElementById('credit-content').style.display = 'none';
        document.getElementById('pix-content').style.display = 'none';
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

        // 2. Mostra a aba certa e avisa o Python (Input Oculto)
        if (method === 'credit') {
            document.getElementById('credit-content').style.display = 'block';
            // CRÍTICO: Atualiza o valor que vai pro banco de dados
            document.getElementById('input-pagamento').value = 'credit'; 
            
            // Marca o botão como ativo
            document.querySelector("button[onclick=\"selectPayment('credit')\"]").classList.add('active');
        } else {
            document.getElementById('pix-content').style.display = 'block';
            // CRÍTICO: Atualiza o valor que vai pro banco de dados
            document.getElementById('input-pagamento').value = 'pix';
            
            document.querySelector("button[onclick=\"selectPayment('pix')\"]").classList.add('active');
        }
    }

    // Função que roda ao clicar em "CONFIRMAR PEDIDO"
/* JAVA PEDIDO CHECKOUT */

// --- A "SUPER FUNÇÃO" FINAL (CORRIGIDA) ---
/* JAVA PEDIDO CHECKOUT */

function prepararEnvio() {
    console.log("--- INICIANDO PREPARAÇÃO DO ENVIO ---");

    // 1. Verifica se é cartão de crédito
    const metodo = document.getElementById('input-pagamento').value;
    console.log("Método de pagamento:", metodo);

    if (metodo === 'credit') {
        // Tenta pegar os elementos visíveis
        const visualNum = document.getElementById('card_number');
        const visualName = document.getElementById('card_holder');
        const visualDate = document.getElementById('card_expiry');
        const checkSave = document.getElementById('save_card_check');

        // Debug: Mostra se achou os campos
        if (!visualNum || !visualName) {
            alert("ERRO: Não encontrei os campos do cartão no HTML! Verifique os IDs.");
            return; 
        }

        console.log("Valor Digitado no Cartão:", visualNum.value);
        console.log("Checkbox Salvar marcado?", checkSave.checked);

        // Copia para os ocultos
        document.getElementById('hidden-card-number').value = visualNum.value;
        document.getElementById('hidden-card-holder').value = visualName.value;
        document.getElementById('hidden-card-expiry').value = visualDate.value;
        
        // Define se salva ou não
        const salvar = checkSave.checked ? 'sim' : 'nao';
        document.getElementById('hidden-save-option').value = salvar;
        
        console.log("Valor copiado para hidden-save-option:", salvar);
    }
    
    // Pega parcelas
    const parcelas = document.getElementById('select-parcelas');
    if (parcelas) {
        document.getElementById('hidden-parcelas').value = parcelas.value;
    }
    
    console.log("--- DADOS PREPARADOS COM SUCESSO ---");
}

function fecharModalNewsletter() {
    const modal = document.getElementById('newsletter-modal');
    modal.classList.remove('show');
}
/* FIm Java do modal de newsletter */

/* JAVA PAGINA DO CARRINHO*/
// Seleciona todos os botões de mais e menos
        const plusBtns = document.querySelectorAll('.plus');
        const minusBtns = document.querySelectorAll('.minus');

        plusBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const input = this.parentElement.querySelector('input');
                let value = parseInt(input.value);
                input.value = value + 1;
                // Aqui você adicionaria a lógica para atualizar o preço total
            });
        });

        minusBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const input = this.parentElement.querySelector('input');
                let value = parseInt(input.value);
                if (value > 1) {
                    input.value = value - 1;
                }
            });
        });
/* FIM JAVA PAGINA DO CARRINHO*/

/* JAVA PAGINA DO RASTREIO*/

function simularRastreio() {
            const input = document.getElementById('trackingInput');
            const result = document.getElementById('trackingResult');
            
            if(input.value.trim() === "") {
                alert("Por favor, digite um código de rastreio.");
                return;
            }

            // Simula um carregamento de 1 segundo
            input.disabled = true;
            document.querySelector('.btn-tracking').innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

            setTimeout(() => {
                input.disabled = false;
                document.querySelector('.btn-tracking').innerHTML = '<i class="fas fa-search"></i>';
                result.style.display = "block"; // Mostra o resultado
            }, 1000);
        }

/* FIM JAVA PAGINA DO RASTREIO*/

/* JAVA PEDIDO CHECKOUT */

    
/* JAVA PEDIDO CHECKOUT */

/* JAVA PEDIDO CHECKOUT */

function verificarEmail(event) {
    // 1. IMPEDE O RECARREGAMENTO DA PÁGINA (Se foi chamado por um evento)
    if (event) event.preventDefault();

    const emailInput = document.getElementById('email-checkout');
    const email = emailInput.value;
    const msgLoading = document.getElementById('msg-loading');

    // Validação simples
    if (!email || !email.includes('@')) {
        alert('Por favor, digite um e-mail válido.');
        return;
    }

    // Mostra carregando e bloqueia botão
    msgLoading.style.display = 'block';
    emailInput.disabled = true;

    // Chama o Python
    fetch('/verificar_email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email: email })
    })
    .then(response => response.json())
    .then(data => {
        // Redirecionamento forçado via JavaScript
        if (data.existe) {
            // CENÁRIO A: Tem conta -> Vai para Login
            window.location.replace(`/login?email=${email}&redirect=checkout`);
        } else {
            // CENÁRIO B: Não tem conta -> Vai para Cadastro
            window.location.replace(`/cadastro-cliente?email=${email}&redirect=checkout`);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao verificar e-mail. Tente novamente.');
        msgLoading.style.display = 'none';
        emailInput.disabled = false;
    });
}
    // Função para alternar abas (Cartão vs Pix)
    function selectPayment(method) {
        // ... sua lógica visual de esconder/mostrar divs ...
        
        // Atualiza o input hidden
        document.getElementById('input-pagamento').value = method;
    }

  
    // Função para alternar abas visualmente e atualizar o input hidden
    function selectPayment(method) {
        // Esconde todos os conteúdos
        document.getElementById('credit-content').style.display = 'none';
        document.getElementById('pix-content').style.display = 'none';
        
        // Remove classe ativa dos botões
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        
        // Mostra o selecionado e atualiza o input hidden
        if (method === 'credit') {
            document.getElementById('credit-content').style.display = 'block';
            // Adicione a classe 'active' ao botão do cartão (adicione IDs aos botões se necessário)
        } else {
            document.getElementById('pix-content').style.display = 'block';
        }
        
        // Atualiza o valor para o Python saber qual foi escolhido
        document.getElementById('input-pagamento').value = method;
    }

    // --- A "SUPER FUNÇÃO" FINAL (USE APENAS ESTA) ---
    function prepararEnvio() {
        
        // 1. PREPARAR OS ITENS (Simulação)
        // Na prática, você pegaria isso do seu carrinho real
        const itensCarrinho = [
            { id_produto: 1, qtd: 1, preco: 68.00 },
            { id_produto: 3, qtd: 2, preco: 45.00 }
        ];
        // Converte para texto e joga no input oculto 'lista_itens'
        document.getElementById('input-itens').value = JSON.stringify(itensCarrinho);

        // 2. PREPARAR DADOS DE PAGAMENTO
        const metodo = document.getElementById('input-pagamento').value;
        
        if (metodo === 'credit') {
            // Se for crédito, pega os dados digitados e joga nos inputs ocultos
            document.getElementById('hidden-card-number').value = document.getElementById('card_number').value;
            document.getElementById('hidden-card-holder').value = document.getElementById('card_holder').value;
            document.getElementById('hidden-card-expiry').value = document.getElementById('card_expiry').value;
            
            // Verifica se quer salvar o cartão
            const salvar = document.getElementById('save_card_check').checked ? 'sim' : 'nao';
            document.getElementById('hidden-save-option').value = salvar;

            // Pega o número de parcelas escolhido no select
            const parcelas = document.getElementById('select-parcelas').value;
            document.getElementById('hidden-parcelas').value = parcelas;
            
        } else {
            // Se for Pix, garantimos que parcelas seja 1
            document.getElementById('hidden-parcelas').value = "1";
        }
        
        // O formulário será enviado automaticamente após essa função rodar no 'onclick' do botão submit
    }

/* FIM JAVA PEDIDO CHECKOUT */
 

// Script simples para visual da quantidade (opcional)
        function updateQty(change) {
            let input = document.getElementById('productQty');
            let newVal = parseInt(input.value) + change;
            if (newVal >= 1) input.value = newVal;
        }


