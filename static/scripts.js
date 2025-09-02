// static/js/scripts.js
window.onload = function () {
    let grows = document.getElementsByClassName("grow-container")

    if (grows.length > 0) {
        togglePopupMenu(grows[0].id);
    }
}

function togglePopupMenu(div_id) {
    const element = document.getElementById(div_id);
    const currentDisplay = window.getComputedStyle(element).display;

    if (currentDisplay === "none") {
        element.style.display = "block";
    } else {
        element.style.display = "none";
    }    
}

function scheduleCheckboxChanged(effector_id) {
    const schedule_checkbox = document.getElementById('schedule-checkbox-' + effector_id);
    const bound_checkbox = document.getElementById('bound-checkbox-' + effector_id);
    const on_time_field = document.getElementById('on-time-' + effector_id);
    const off_time_field = document.getElementById('off-time-' + effector_id);

    if(schedule_checkbox.checked){
        bound_checkbox.checked = false;
        bound_checkbox.disabled = true;
        on_time_field.disabled = false;
        off_time_field.disabled = false;
    } else {
        bound_checkbox.disabled = false;
        on_time_field.disabled = true;
        off_time_field.disabled = true;
    }
}

function boundCheckboxChanged(effector_id) {
    const schedule_checkbox = document.getElementById('schedule-checkbox-' + effector_id);
    const bound_checkbox = document.getElementById('bound-checkbox-' + effector_id);
    const sensor_id_field = document.getElementById('bounded-sensor-id-' + effector_id);
    const threshold_field = document.getElementById('threshold-' + effector_id);

    if(bound_checkbox.checked){
        schedule_checkbox.checked = false;
        schedule_checkbox.disabled = true;
        sensor_id_field.disabled = false;
        threshold_field.disabled = false;
    } else {
        schedule_checkbox.disabled = false;
        sensor_id_field.disabled = true;
        threshold_field.disabled = true;
    }
}

// Funções de gráficos - Versão corrigida
function createSensorChartFromData(sensorId, sensorData, chartContainerId) {
    console.log('Criando gráfico para sensor:', sensorId, 'Dados:', sensorData);
    
    if (!sensorData || sensorData.length === 0) {
        console.error('Nenhum dado disponível para o sensor', sensorId);
        return;
    }

    const timestamps = [];
    const values = [];
    
    sensorData.forEach(dataPoint => {
        if (dataPoint && dataPoint.length >= 2) {
            const value = parseFloat(dataPoint[0]);
            let timestamp = dataPoint[1];
            
            if (timestamp && value !== undefined && !isNaN(value)) {
                let date;
                
                // Converter diferentes formatos de timestamp
                if (typeof timestamp === 'string') {
                    // Para formato "Sat, 06 Sep 2025 19:29:39 GMT"
                    try {
                        // Remover dia da semana e timezone para simplificar
                        const dateParts = timestamp.split(' ');
                        if (dateParts.length >= 5) {
                            // Formatar como "06 Sep 2025 19:29:39"
                            const dateString = `${dateParts[1]} ${dateParts[2]} ${dateParts[3]} ${dateParts[4]}`;
                            date = new Date(dateString);
                            
                            // Se ainda for inválido, tentar parse direto
                            if (isNaN(date.getTime())) {
                                date = new Date(timestamp);
                            }
                        } else {
                            date = new Date(timestamp);
                        }
                    } catch (e) {
                        console.warn('Erro ao converter data:', timestamp, e);
                        date = new Date(); // Usar data atual como fallback
                    }
                } else if (timestamp instanceof Date) {
                    date = timestamp;
                }
                
                if (date && !isNaN(date.getTime())) {
                    timestamps.push(date);
                    values.push(value);
                    console.log('Data convertida:', date, 'Valor:', value);
                } else {
                    console.warn('Data inválida para sensor', sensorId, timestamp);
                    // Adicionar fallback: usar timestamp sequencial
                    const fallbackDate = new Date(Date.now() - (values.length * 60000)); // 1 minuto entre pontos
                    timestamps.push(fallbackDate);
                    values.push(value);
                }
            }
        }
    });

    if (timestamps.length === 0) {
        console.error('Dados inválidos para o sensor', sensorId);
        return;
    }

    // Calcular valor máximo para o eixo Y
    const maxValue = Math.max(...values);
    // Garantir que o valor mínimo seja 0
    const minValue = 0;

    let canvas = document.getElementById(`sensor-chart-${sensorId}`);
    const container = document.getElementById(chartContainerId);
    
    if (!container) {
        console.error('Container do gráfico não encontrado:', chartContainerId);
        return;
    }
    
    if (!canvas) {
        canvas = document.createElement('canvas');
        canvas.id = `sensor-chart-${sensorId}`;
        canvas.style.width = '100%';
        canvas.style.height = '200px';
        canvas.style.margin = '10px 0';
        container.appendChild(canvas);
    }

    if (window.sensorCharts && window.sensorCharts[sensorId]) {
        window.sensorCharts[sensorId].destroy();
    }

    const ctx = canvas.getContext('2d');
    window.sensorCharts = window.sensorCharts || {};
    
    try {
        window.sensorCharts[sensorId] = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: `Sensor ${sensorId}`,
                    data: values.map((value, index) => ({
                        x: timestamps[index],
                        y: value
                    })),
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.1, // Reduzir a tensão para linhas mais retas
                    fill: false,   // Não preencher área sob a linha
                    pointRadius: 2,
                    pointBackgroundColor: 'rgb(75, 192, 192)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'minute',
                            displayFormats: {
                                minute: 'HH:mm',
                                hour: 'HH:mm'
                            },
                            tooltipFormat: 'DD/MM/YYYY HH:mm:ss'
                        },
                        title: {
                            display: true,
                            text: 'Tempo'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Valor'
                        },
                        beginAtZero: true, // Garante que começa em 0
                        suggestedMin: minValue, // Valor mínimo fixo em 0
                        suggestedMax: maxValue * 1.1 // Adiciona 10% de margem no topo
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Valor: ${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                }
            }
        });
        
        console.log('Gráfico criado com sucesso para sensor', sensorId);
    } catch (error) {
        console.error('Erro ao criar gráfico:', error);
    }
}

function showSensorChartModal(sensorId, sensorName, sensorData) {
    const modal = document.createElement('div');
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0,0,0,0.8)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '1000';

    createSensorChartFromData(sensorId, sensorData, `modal-chart-container-${sensorId}`);

    // Depois, abrir o modal
    togglePopupMenu('sensor-chart-container-' + sensorId);
}