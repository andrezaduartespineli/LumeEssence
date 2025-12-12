/* JAVA PAGINA CARTOES*/

function abrirModalCartao() {
            document.getElementById('modal-cartao').style.display = 'flex';
        }
        function fecharModalCartao() {
            document.getElementById('modal-cartao').style.display = 'none';
        }

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