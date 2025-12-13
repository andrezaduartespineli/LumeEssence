document.addEventListener('DOMContentLoaded', function() {
    
    const campoCep = document.getElementById('cep');

    // Função segura para preencher valor (só preenche se o campo existir no HTML)
    function setVal(id, valor) {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.value = valor;
        }
    }

    if (campoCep) {
        campoCep.addEventListener('blur', function() {
            let cep = this.value.replace(/\D/g, '');

            if (cep.length === 8) {
                // Preenche com "..." apenas nos campos que existem na tela
                setVal('rua', '...');
                setVal('bairro', '...');
                setVal('cidade', '...');
                setVal('uf', '...');

                fetch(`https://viacep.com.br/ws/${cep}/json/`)
                    .then(response => response.json())
                    .then(data => {
                        if (!data.erro) {
                            // Preenche os dados reais
                            setVal('rua', data.logradouro);
                            setVal('bairro', data.bairro);
                            setVal('cidade', data.localidade);
                            setVal('uf', data.uf);
                            
                            // Tenta focar no número, se existir
                            const campoNumero = document.getElementById('numero');
                            if (campoNumero) campoNumero.focus();
                        } else {
                            alert("CEP não encontrado.");
                            limparCampos();
                        }
                    })
                    .catch(() => {
                        alert("Erro ao buscar CEP.");
                        limparCampos();
                    });
            }
        });
    }

    function limparCampos() {
        setVal('rua', '');
        setVal('bairro', '');
        setVal('cidade', '');
        setVal('uf', '');
    }
});