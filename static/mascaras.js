document.addEventListener('DOMContentLoaded', function() {
    
    // MÁSCARA DE CPF (000.000.000-00)
    const camposCpf = document.querySelectorAll('.mask-cpf');
    camposCpf.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, ""); // Remove tudo que não é número
            value = value.replace(/(\d{3})(\d)/, "$1.$2");
            value = value.replace(/(\d{3})(\d)/, "$1.$2");
            value = value.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
            e.target.value = value;
        });
        input.setAttribute('maxlength', '14'); // Limita tamanho
    });

    // MÁSCARA DE CNPJ (00.000.000/0000-00)
    const camposCnpj = document.querySelectorAll('.mask-cnpj');
    camposCnpj.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, "");
            value = value.replace(/^(\d{2})(\d)/, "$1.$2");
            value = value.replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3");
            value = value.replace(/\.(\d{3})(\d)/, ".$1/$2");
            value = value.replace(/(\d{4})(\d)/, "$1-$2");
            e.target.value = value;
        });
        input.setAttribute('maxlength', '18');
    });

    // MÁSCARA DE TELEFONE/CELULAR ((00) 00000-0000)
    const camposTel = document.querySelectorAll('.mask-tel');
    camposTel.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, "");
            value = value.replace(/^(\d{2})(\d)/g, "($1) $2");
            value = value.replace(/(\d)(\d{4})$/, "$1-$2");
            e.target.value = value;
        });
        input.setAttribute('maxlength', '15');
    });

    // MÁSCARA DE CEP (00000-000)
    const camposCep = document.querySelectorAll('.mask-cep');
    camposCep.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, "");
            value = value.replace(/^(\d{5})(\d)/, "$1-$2");
            e.target.value = value;
        });
        input.setAttribute('maxlength', '9');
    });

    // MÁSCARA DE MOEDA (R$ 0,00) - Opcional, bom para preços
    const camposDinheiro = document.querySelectorAll('.mask-money');
    camposDinheiro.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, "");
            value = (value / 100).toFixed(2) + '';
            value = value.replace(".", ",");
            value = value.replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1.');
            e.target.value = 'R$ ' + value;
        });
    });
});

// MÁSCARA DE DATA (00/00/0000)
    const camposData = document.querySelectorAll('.mask-data');
    camposData.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, ""); // Remove letras
            
            // Adiciona a primeira barra depois do dia
            if (value.length > 2) {
                value = value.substring(0, 2) + '/' + value.substring(2);
            }
            
            // Adiciona a segunda barra depois do mês
            if (value.length > 5) {
                value = value.substring(0, 5) + '/' + value.substring(5, 9);
            }
            
            e.target.value = value;
        });
        
        // Limita a 10 caracteres (10/10/2025)
        input.setAttribute('maxlength', '10');
        input.setAttribute('placeholder', 'DD/MM/AAAA');
    });