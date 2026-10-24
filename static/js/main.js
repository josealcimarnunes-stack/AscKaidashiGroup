document.addEventListener('DOMContentLoaded', () => {
    console.log("AscKaidashi Group Panel initialized.");
});

function abrirSubModulo(modulo, acao) {
    alert(`Módulo: [${modulo}] -> Executando Ação: [${acao}]`);
    // Aqui no futuro vamos fazer requisições AJAX/Fetch para carregar as telas dinamicamente sem dar refresh!
}
document.addEventListener('DOMContentLoaded', () => {
    console.log("AscKaidashi Group Panel initialized.");

    const btnSalvar = document.getElementById('btn-salvar-prompt');
    if (btnSalvar) {
        btnSalvar.addEventListener('click', () => {
            const estiloAtual = new URLSearchParams(window.location.search).get('estilo') || 'casual';
            const textoPrompt = document.getElementById('input-prompt-texto').value;

            // Envia os dados via POST para o Flask sem dar refresh na página
            fetch(`/familia/perfil/mamae?estilo=${estiloAtual}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: textoPrompt })
            })
            .then(response => response.json())
            .then(data => {
                alert('Prompt salvo com sucesso!');
            })
            .catch(error => {
                console.error('Erro ao salvar:', error);
                alert('Erro ao salvar o prompt.');
            });
        });
    }
});