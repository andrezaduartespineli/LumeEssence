/* JAVA PAGINA CARTOES*/

/* --- LÓGICA DO MODAL DE CARTÕES --- */

// Função para abrir o modal (chamada pelo botão "+ Novo Cartão")
function abrirModal() {
    const modal = document.getElementById('modal-cartao');
    if (modal) {
        // 'flex' é importante para o CSS centralizar a caixa na tela
        modal.style.display = 'flex'; 
    }
}

// Função para fechar o modal (chamada pelo 'X' e pelo botão 'Cancelar')
function fecharModal() {
    const modal = document.getElementById('modal-cartao');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Lógica para fechar ao clicar FORA da caixa branca (na parte escura)
window.addEventListener('click', function(event) {
    const modal = document.getElementById('modal-cartao');
    // Se o elemento clicado for EXATAMENTE o fundo escuro (modal-container), fecha.
    if (event.target === modal) {
        modal.style.display = 'none';
    }
});

/* fim JAVA PAGINA CARTOES*/

/* JAVA PAGINA ENDEREÇOS*/

function abrirModalEndereco() {
            document.getElementById('modal-endereco').style.display = 'flex';
        }
        function fecharModalEndereco() {
            document.getElementById('modal-endereco').style.display = 'none';
        }

/* FIM JAVA PAGINA ENDEREÇOS*/

function previewImagem(event) {
        var input = event.target;
        var reader = new FileReader();
        
        reader.onload = function(){
            var img = document.getElementById('preview-img');
            img.src = reader.result;
        };
        
        if(input.files && input.files[0]){
            reader.readAsDataURL(input.files[0]);
        }
    }