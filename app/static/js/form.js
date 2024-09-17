document.addEventListener("DOMContentLoaded", function() {
    // Prevenir a submissão do formulário ao pressionar Enter em um campo específico
    document.querySelector('form').addEventListener('keypress', function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
        }
    });

    const doiInput = document.querySelector('input[name="doi"]');
    const tituloInput = document.querySelector('input[name="titulo"]');
    const anoInput = document.querySelector('input[name="ano"]');
    const revistaInput = document.querySelector('input[name="revista"]');
    const issnInput = document.querySelector('input[name="issn"]');
    const autoresInput = document.querySelector('input[name="autores"]');
    const areaSelect = document.querySelector('select[name="area_id"]');
    const classificacaoInput = document.querySelector('input[name="classificacao"]');

    function updateClassificacao() {
        const issn = issnInput.value.trim();
        const area_avaliacao = areaSelect.options[areaSelect.selectedIndex].text;

        if (issn && area_avaliacao) {
            fetch('/get_classificacao', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({issn: issn, area_avaliacao: area_avaliacao}),
            })
            .then(response => response.json())
            .then(data => {
                if (data.classificacao) {
                    classificacaoInput.value = data.classificacao;
                } else if (data.error) {
                    alert(data.error);
                }
            })
            .catch(error => {
                console.error('Erro ao buscar a classificação:', error);
            });
        }
    }

    issnInput.addEventListener('blur', updateClassificacao);
    areaSelect.addEventListener('change', updateClassificacao);

    doiInput.addEventListener('blur', function() {
        const doi = this.value.trim();

        if (doi) {
            fetch('/check_doi', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({doi: doi}),
            })
            .then(response => response.json())
            .then(data => {
                if (data.exists) {
                    alert(data.message);
                } else {
                    fetch('/fetch_metadata', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({doi: doi}),
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            alert(data.error);
                        } else {
                            tituloInput.value = data.titulo || '';
                            anoInput.value = data.ano || '';
                            revistaInput.value = data.revista || '';
                            issnInput.value = data.issn || '';
                            autoresInput.value = data.autores || '';
                        }
                    })
                    .catch(error => {
                        console.error('Erro ao buscar metadados:', error);
                    });
                }
            })
            .catch(error => {
                console.error('Erro ao verificar o DOI:', error);
            });
        }
    });

    document.querySelector('form').addEventListener('submit', function(event) {
        if (!this.checkValidity()) {
            return;
        }

        event.preventDefault();

        const form = this;
        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Artigo enviado com sucesso!');
                clearValidationErrors();  // Limpar as mensagens de erro
                resetFormFields();  // Limpar todos os campos do formulário
            } else if (data.errors) {
                let errorMessage = 'Erro ao enviar o formulário:\n';
                for (let field in data.errors) {
                    errorMessage += `${data.errors[field]}\n`;
                }
                alert(errorMessage);
            }
        })
        .catch(error => {
            console.error('Erro ao processar o formulário:', error);
            alert('Ocorreu um erro ao processar o formulário. Tente novamente.');
        });
    });

    function clearValidationErrors() {
        const errorElements = document.querySelectorAll('span[style="color: red;"]');
        errorElements.forEach(function(element) {
            element.textContent = '';  // Limpar o conteúdo das mensagens de erro
        });
    }

function resetFormFields() {
    // Limpar todos os campos do formulário
    const inputs = document.querySelectorAll('input');
    inputs.forEach(function(input) {
        if (input.type === 'checkbox' || input.type === 'radio') {
            input.checked = false;  // Desmarcar checkboxes e radio buttons
        } else {
            input.value = '';  // Limpar campos de entrada
        }
    });

    // Resetar campos <select> para a primeira opção (que geralmente é "SELECIONE...")
    const selectElements = document.querySelectorAll('select');
    selectElements.forEach(function(select) {
        select.selectedIndex = 0;
    });

    // Se houver textarea ou outros campos, limpar também
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(function(textarea) {
        textarea.value = '';  // Limpar textarea
    });
}
});
