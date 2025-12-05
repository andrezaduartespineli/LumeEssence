/*------ JAVA DO MODAL DE NOVA REVEITA (FINANCEIRO)------- */

 // Pega os elementos
        const modalReceita = document.getElementById('modal-receita');
        const btnNovaReceita = document.querySelector('.btn-income'); // O botão verde que já existe na tela
        
        // Define a data de hoje automaticamente no input
        document.getElementById('data-hoje').valueAsDate = new Date();

        // Função Abrir
        btnNovaReceita.addEventListener('click', () => {
            modalReceita.style.display = 'flex';
        });

        // Função Fechar
        function fecharModalReceita() {
            modalReceita.style.display = 'none';
        }

        // Fechar se clicar fora da caixinha branca
        modalReceita.addEventListener('click', (e) => {
            if (e.target === modalReceita) {
                fecharModalReceita();
            }
        });

/*------ FIM DO JAVA DO MODAL DE NOVA REVEITA (FINANCEIRO)------- */

/*------ JAVA DO MODAL DE NOVA DESPESA (FINANCEIRO)------- */

        const modalDespesa = document.getElementById('modal-despesa');
        const btnNovaDespesa = document.querySelector('.btn-expense'); // Botão vermelho da tela

        // Define data de hoje também para despesa
        if(document.getElementById('data-despesa')) {
            document.getElementById('data-despesa').valueAsDate = new Date();
        }

        if(btnNovaDespesa) {
            btnNovaDespesa.addEventListener('click', () => {
                modalDespesa.style.display = 'flex';
            });
        }

        function fecharModalDespesa() {
            modalDespesa.style.display = 'none';
        }

        modalDespesa.addEventListener('click', (e) => {
            if (e.target === modalDespesa) fecharModalDespesa();
        });
   

/*------ FIM DO JAVA DO MODAL DE NOVA DESPESA (FINANCEIRO)------- */

/*------ JAVA DA CONFIGURAÇÕES ------- */
function openTab(evt, tabName) {
            // Esconde todo o conteúdo
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }

            // Remove a classe "active" de todos os botões
            tablinks = document.getElementsByClassName("tab-link");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }

            // Mostra a aba clicada e adiciona "active" no botão
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }

        // Simula o clique na primeira aba ao abrir
        document.addEventListener("DOMContentLoaded", function() {
            document.querySelector('.tab-link').click(); 
        });
/*------ FIM DO JAVA DA CONFIGURAÇÕES ------- */

/* --- JAVA do Dropdown de Perfil --- */

function toggleProfileMenu() {
        const menu = document.getElementById('profileMenu');
        menu.classList.toggle('active');
    }

    // Fecha o menu se clicar em qualquer lugar fora dele
    document.addEventListener('click', function(event) {
        const profileArea = document.querySelector('.user-profile');
        const menu = document.getElementById('profileMenu');
        
        // Se o clique NÃO foi dentro da área do perfil e o menu está aberto
        if (!profileArea.contains(event.target) && menu.classList.contains('active')) {
            menu.classList.remove('active');
        }
    });

    /* ---FIM JAVA do Dropdown de Perfil --- */

    /* ----- JAVA DO CADASTRO DE PRODUTOS ----- */
  
                // 1. Função de Tamanhos (Mantida)
                function atualizarTamanhos() {
                    const categoria = document.getElementById('categoria').value;
                    const selectTamanho = document.getElementById('tamanho');
                    const labelTamanho = document.getElementById('label-tamanho');

                    selectTamanho.innerHTML = ""; // Limpa opções antigas

                    if (categoria === 'velas') {
                        labelTamanho.innerText = "Peso (Gramas)";
                        let opcoes = ["100g", "150g", "230g", "330g"];
                        adicionarOpcoes(selectTamanho, opcoes);
                    } else if (categoria === 'spray' || categoria === 'difusor') {
                        labelTamanho.innerText = "Volume (ml)";
                        let opcoes = ["30ml", "50ml", "100ml", "150ml", "250ml","300ml", "500ml"];
                        adicionarOpcoes(selectTamanho, opcoes);
                    } else {
                        labelTamanho.innerText = "Tamanho";
                        let opcoes = ["Padrão", "Kit P", "Kit M" , "Kit G"];
                        adicionarOpcoes(selectTamanho, opcoes);
                    }
                }

                // Auxiliar para criar as opções
                function adicionarOpcoes(select, arrayOpcoes) {
                    arrayOpcoes.forEach(texto => {
                        let option = document.createElement("option");
                        option.text = texto;
                        select.add(option);
                    });
                }

                // 2. NOVA Função de Data (Método Manual Infalível)
                function preencherDataHoje() {
                    const campoData = document.getElementById('data-cadastro');
                    
                    if (campoData) {
                        const hoje = new Date();
                        
                        // Pega partes da data localmente (navegador)
                        const ano = hoje.getFullYear();
                        // Adiciona zero à esquerda se for menor que 10 (ex: mês 5 vira "05")
                        const mes = String(hoje.getMonth() + 1).padStart(2, '0');
                        const dia = String(hoje.getDate()).padStart(2, '0');
                        
                        // Monta no formato que o HTML exige: YYYY-MM-DD
                        const dataFormatada = `${ano}-${mes}-${dia}`;
                        
                        campoData.value = dataFormatada;
                    } else {
                        console.error("Erro: Campo data-cadastro não encontrado.");
                    }
                }

                // Executa tudo quando a tela terminar de carregar
                window.onload = function() {
                    atualizarTamanhos();
                    preencherDataHoje();
                };
           
       /* -----  FIM JAVA DO CADASTRO DE PRODUTOS ----- */