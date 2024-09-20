document.addEventListener("DOMContentLoaded", function() {
    const areaSelector = document.getElementById('areaSelector');
    const subareaSelector = document.getElementById('subareaSelector');
    const anoInicioSelector = document.getElementById('anoInicioSelector');
    const anoFimSelector = document.getElementById('anoFimSelector');
    // const baseUrl = '/api/dashboard_data';
    // Referente ao ano atual
    const anoAtual = new Date().getFullYear();
    const tituloAnoAtualElem = document.getElementById('artigosAnoAtualTitulo');
    tituloAnoAtualElem.textContent = `Total de Artigos de ${anoAtual}`;

    // Referências aos elementos das métricas principais
    const totalArtigosElem = document.getElementById('totalArtigos');
    const mediaFatorImpactoElem = document.getElementById('mediaFatorImpacto');
    const artigosAnoAtualElem = document.getElementById('artigosAnoAtual');

    // Referências aos elementos das métricas filtradas
    const totalArtigosFiltradosElem = document.getElementById('totalArtigosFiltrados');
    const mediaFatorImpactoFiltradaElem = document.getElementById('mediaFatorImpactoFiltrada');
    // Função para salvar os graficos
//     function saveChartAsImage(chart, chartId) {
//     const originalWidth = chart.width;
//     const originalHeight = chart.height;
//
//     // Temporariamente aumentar o tamanho do canvas para melhorar a qualidade da exportação
//     chart.resize(2024, 2024);  // Aumente o tamanho conforme necessário
//
//     setTimeout(function() {
//         const image = chart.toBase64Image();
//
//         // Enviar a imagem para o servidor
//         fetch('/save-chart', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({
//                 chartId: chartId,
//                 imageData: image
//             })
//         }).then(response => response.json())
//           .then(data => {
//               console.log('Imagem salva no servidor:', data);
//               // Restaurar o tamanho original do gráfico
//               chart.resize(originalWidth, originalHeight);
//           });
//     }, 1000);  // Um pequeno atraso para garantir que o gráfico seja renderizado
// }


    // Inicialização dos gráficos
    const ctx1 = document.getElementById('chart1').getContext('2d');
    const chart1 = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Número de Artigos',
                backgroundColor: '#36A2EB',
                data: []
            }]
        }
    });
// saveChartAsImage(chart1, 'chart1');
    const ctx2 = document.getElementById('chart2').getContext('2d');
    const chart2 = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Classificação Qualis',
                backgroundColor: '#FF6384',
                data: []
            }]
        }
    });
    // saveChartAsImage(chart2, 'chart2');
    const ctx3 = document.getElementById('chart3').getContext('2d');
    const chart3 = new Chart(ctx3, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Número de Artigos por Revista',
                backgroundColor: '#FFCE56',
                data: []
            }]
        }
    });
    // saveChartAsImage(chart3, 'chart3');
    const ctx4 = document.getElementById('chart4').getContext('2d');
    const chart4 = new Chart(ctx4, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Artigos por Área Específica',
                backgroundColor: '#4BC0C0',
                data: []
            }]
        }
    });
    // saveChartAsImage(chart4, 'chart4');
    const ctx5 = document.getElementById('chart5').getContext('2d');
    const chart5 = new Chart(ctx5, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Fator de Impacto Médio por Ano',
                backgroundColor: 'rgba(153, 102, 255, 0.2)', // Cor de fundo da área preenchida
                borderColor: 'rgba(153, 102, 255, 1)', // Cor da linha
                pointBackgroundColor: 'rgba(153, 102, 255, 1)', // Cor dos pontos
                fill: true,
                data: []
            }]
        }
    });
// saveChartAsImage(chart5, 'chart5');
    const ctx6 = document.getElementById('chart6').getContext('2d');
    const chart6 = new Chart(ctx6, {
        type: 'pie',
        data: {
            labels: ['Sim', 'Não'],
            datasets: [{
                label: 'Artigos Internacionalizados',
                backgroundColor: ['#FF9F40', '#FFCD56'],
                data: []
            }]
        },
        options: {
            plugins: {
                datalabels: {
                    formatter: (value, ctx) => {
                        let sum = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                        let percentage = (value / sum * 100).toFixed(2) + "%";
                        return percentage;
                    },
                    color: '#fff',
                    font: {
                        weight: 'bold'
                    }
                }
            }
        },
        plugins: [ChartDataLabels]
    });
// saveChartAsImage(chart6, 'chart6');
    const ctx7 = document.getElementById('chart7').getContext('2d');
    const chart7 = new Chart(ctx7, {
        type: 'pie',
        data: {
            labels: [],
            datasets: [{
                label: 'Classificação Qualis',
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
                data: []
            }]
        },
        options: {
            plugins: {
                datalabels: {
                    formatter: (value, ctx) => {
                        let sum = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                        let percentage = (value / sum * 100).toFixed(2) + "%";
                        return percentage;
                    },
                    color: '#fff',
                    font: {
                        weight: 'bold'
                    }
                }
            }
        },
        plugins: [ChartDataLabels]
    });
    // saveChartAsImage(chart7, 'chart7');
    const ctx8 = document.getElementById('chart8').getContext('2d');
    const chart8 = new Chart(ctx8, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Número de Artigos por Área de Avaliação Qualis',
                backgroundColor: '#8e44ad',
                data: []
            }]
        }
    });
// saveChartAsImage(chart8, 'chart8');
    // Função para carregar métricas principais
    function loadPrimaryMetrics() {
        fetch(baseUrl)
            .then(response => response.json())
            .then(data => {
                if (data.metrics) {
                    totalArtigosElem.textContent = data.metrics.total_artigos;
                    mediaFatorImpactoElem.textContent = data.metrics.media_fator_impacto;
                    artigosAnoAtualElem.textContent = data.metrics.artigos_ano_atual;
                }
            })
            .catch(error => console.error('Erro ao carregar as métricas principais:', error));
    }

    // Função para carregar dados filtrados e atualizar gráficos
    function fetchAndUpdateCharts(areaId = '', subareaId = '', anoInicio = '', anoFim = '') {
        const url = `${baseUrl}?area_id=${areaId}&subarea_id=${subareaId}&ano_inicio=${anoInicio}&ano_fim=${anoFim}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.metrics) {
                    // Atualizar as métricas filtradas
                    totalArtigosFiltradosElem.textContent = data.metrics.total_artigos_filtrados;
                    mediaFatorImpactoFiltradaElem.textContent = data.metrics.media_fator_impacto_filtrada;
                }

                if (data.chart1) {
                    chart1.data.labels = data.chart1.labels;
                    chart1.data.datasets[0].data = data.chart1.datasets[0].data;
                    chart1.update();
                }

                if (data.chart2) {
                    chart2.data.labels = data.chart2.labels;
                    chart2.data.datasets[0].data = data.chart2.datasets[0].data;
                    chart2.update();
                }

                if (data.chart3) {
                    chart3.data.labels = data.chart3.labels;
                    chart3.data.datasets[0].data = data.chart3.datasets[0].data;
                    chart3.update();
                }

                if (data.chart4) {
                    chart4.data.labels = data.chart4.labels;
                    chart4.data.datasets[0].data = data.chart4.datasets[0].data;
                    chart4.update();
                }

                if (data.chart5) {
                    chart5.data.labels = data.chart5.labels;
                    chart5.data.datasets[0].data = data.chart5.datasets[0].data;
                    chart5.update();
                }

                if (data.chart6) {
                    chart6.data.datasets[0].data = data.chart6.datasets[0].data;
                    chart6.update();
                }

                if (data.chart7) {
                    chart7.data.labels = data.chart7.labels;
                    chart7.data.datasets[0].data = data.chart7.datasets[0].data;
                    chart7.update();
                }

                if (data.chart8) {
                    chart8.data.labels = data.chart8.labels;
                    chart8.data.datasets[0].data = data.chart8.datasets[0].data;
                    chart8.update();
                }
            })
            .catch(error => console.error('Erro ao carregar os dados filtrados:', error));
    }

    // Inicializar as métricas principais
    loadPrimaryMetrics();

    // Atualizar os gráficos ao mudar os seletores
    areaSelector.addEventListener('change', function() {
        fetchAndUpdateCharts(this.value, subareaSelector.value, anoInicioSelector.value, anoFimSelector.value);
    });

    subareaSelector.addEventListener('change', function() {
        fetchAndUpdateCharts(areaSelector.value, this.value, anoInicioSelector.value, anoFimSelector.value);
    });

    anoInicioSelector.addEventListener('change', function() {
        fetchAndUpdateCharts(areaSelector.value, subareaSelector.value, this.value, anoFimSelector.value);
    });

    anoFimSelector.addEventListener("change", function() {
        fetchAndUpdateCharts(areaSelector.value, subareaSelector.value, anoInicioSelector.value, this.value);
    });

    // Carregar os gráficos com todos os dados na inicialização
    fetchAndUpdateCharts();
 // saveChartAsImage(chart1, 'chart1');

});
