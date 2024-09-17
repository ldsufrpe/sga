document.addEventListener("DOMContentLoaded", function() {
    const listarArtigosForm = document.getElementById('listar-artigos-form');

    if (listarArtigosForm) {
        listarArtigosForm.addEventListener('submit', function(event) {
            if (!this.checkValidity()) {
                return;
            }

            event.preventDefault();

            this.submit(); // Enviar o formulário normalmente
        });

        document.querySelector('.btn-secondary').addEventListener('click', function(event) {
            event.preventDefault();
            resetFormFields();
            window.location.href = this.href;  // Redireciona para a rota original para limpar a busca
        });

        function resetFormFields() {
            const inputs = listarArtigosForm.querySelectorAll('input');
            inputs.forEach(function(input) {
                input.value = '';  // Limpar campos de entrada
            });

            // Resetar campos <select> para a primeira opção (que geralmente é "SELECIONE...")
            const selectElements = listarArtigosForm.querySelectorAll('select');
            selectElements.forEach(function(select) {
                select.selectedIndex = 0;
            });

            const textareas = listarArtigosForm.querySelectorAll('textarea');
            textareas.forEach(function(textarea) {
                textarea.value = '';  // Limpar textarea
            });
        }
    }
});
