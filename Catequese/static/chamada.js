document.addEventListener("DOMContentLoaded", function () {


    const botoes = document.querySelectorAll(
        ".botoes button"
    );


    botoes.forEach(function (botao) {


        botao.addEventListener("click", function () {


            const alunoId = this.dataset.alunoId;

            const data = this.dataset.data;

            const presente =
                this.dataset.presente === "true";


            // =========================================
            // VERIFICA SE JÁ ESTÁ SELECIONADO
            // =========================================

            const jaSelecionado =
                this.classList.contains("selecionado");


            // =========================================
            // SE CLICOU NOVAMENTE
            // REMOVE A MARCAÇÃO
            // =========================================

            const novoValor =
                jaSelecionado
                    ? null
                    : presente;


            salvarChamada(
                this,
                alunoId,
                data,
                novoValor
            );


        });

    });

});


// =====================================================
// SALVAR CHAMADA
// =====================================================

async function salvarChamada(
    botao,
    alunoId,
    data,
    presente
) {


    try {


        const resposta = await fetch(
            "/api/chamada",
            {

                method: "POST",

                headers: {

                    "Content-Type":
                        "application/json"

                },

                body: JSON.stringify({

                    aluno_id:
                        Number(alunoId),

                    data:
                        data,

                    presente:
                        presente

                })

            }
        );


        const resultado =
            await resposta.json();


        // =========================================
        // ERRO DO SERVIDOR
        // =========================================

        if (!resposta.ok || !resultado.ok) {


            console.error(
                "Erro:",
                resultado
            );


            alert(
                resultado.erro ||
                "Erro ao registrar chamada."
            );


            return;

        }


        // =========================================
        // PEGA A CÉLULA DOS BOTÕES
        // =========================================

        const botoesContainer =
            botao.parentElement;


        const botaoPresente =
            botoesContainer.querySelector(
                ".presente"
            );


        const botaoFalta =
            botoesContainer.querySelector(
                ".falta"
            );


        // =========================================
        // REMOVE SELEÇÃO DOS DOIS
        // =========================================

        botaoPresente.classList.remove(
            "selecionado"
        );


        botaoFalta.classList.remove(
            "selecionado"
        );


        // =========================================
        // MARCA O NOVO ESTADO
        // =========================================

        if (presente === true) {


            botaoPresente.classList.add(
                "selecionado"
            );


        }
        else if (presente === false) {


            botaoFalta.classList.add(
                "selecionado"
            );

        }


        // =========================================
        // ATUALIZA STATUS DO ALUNO
        // =========================================

        atualizarStatus(
            alunoId,
            resultado.faltas,
            resultado.status
        );


    }
    catch (erro) {


        console.error(
            "Erro de comunicação:",
            erro
        );


        alert(
            "Não foi possível comunicar com o servidor."
        );

    }

}


// =====================================================
// ATUALIZA STATUS
// =====================================================

function atualizarStatus(
    alunoId,
    faltas,
    status
) {


    const linha =
        document.querySelector(
            "#aluno-" + alunoId
        );


    if (!linha) {

        return;

    }


    const statusTexto =
        linha.querySelector(
            ".status-text"
        );


    const contador =
        linha.querySelector(
            ".contador"
        );


    if (statusTexto) {


        statusTexto.textContent =
            status;


        statusTexto.classList.remove(
            "status-normal",
            "status-alerta"
        );


        if (status === "Alerta") {


            statusTexto.classList.add(
                "status-alerta"
            );


        }
        else {


            statusTexto.classList.add(
                "status-normal"
            );

        }

    }


    if (contador) {


        contador.textContent =
            faltas +
            (
                faltas === 1
                    ? " falta"
                    : " faltas"
            );

    }

}