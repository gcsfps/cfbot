document.addEventListener('DOMContentLoaded', () => {
    const exportBtn = document.getElementById('exportBtn');
    const addBtn = document.getElementById('addBtn');
    const status = document.getElementById('status');
    const progress = document.getElementById('progress');
    const progressText = document.getElementById('progressText');
    
    // Elementos de configuração
    const batchSize = document.getElementById('batchSize');
    const minDelay = document.getElementById('minDelay');
    const maxDelay = document.getElementById('maxDelay');
    const pauseAfter = document.getElementById('pauseAfter');
    
    function updateStatus(message, show = true) {
        status.textContent = message;
        status.style.display = show ? 'block' : 'none';
    }
    
    function updateProgress(processed, total, show = true) {
        progressText.textContent = `${processed} processados de ${total}`;
        progress.style.display = show ? 'block' : 'none';
    }
    
    function getSettings() {
        return {
            batchSize: parseInt(batchSize.value),
            minDelay: parseFloat(minDelay.value),
            maxDelay: parseFloat(maxDelay.value),
            pauseAfter: parseInt(pauseAfter.value)
        };
    }
    
    function downloadCSV(followers) {
        // Cria o conteúdo CSV
        const csvContent = 'Username\n' + followers.join('\n');
        
        // Cria o blob com BOM para suporte UTF-8
        const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
        
        // Cria o link de download
        const url = window.URL.createObjectURL(blob);
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `instagram_followers_${timestamp}.csv`;
        
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        
        // Limpa
        window.URL.revokeObjectURL(url);
        document.body.removeChild(link);
    }
    
    // Esconde elementos de status inicialmente
    updateStatus('', false);
    updateProgress(0, 0, false);
    
    exportBtn.addEventListener('click', async () => {
        try {
            exportBtn.disabled = true;
            addBtn.disabled = true;
            updateStatus('Exportando seguidores...');
            updateProgress(0, 0, true);
            
            const settings = getSettings();
            const params = new URLSearchParams(settings).toString();
            
            const response = await fetch(`http://localhost:5000/export_followers?${params}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Resposta do servidor não é JSON válido');
            }
            
            const data = await response.json();
            
            if (data.success) {
                downloadCSV(data.followers);
                updateStatus('Seguidores exportados com sucesso!');
                updateProgress(data.followers.length, data.followers.length);
            } else {
                throw new Error(data.error || 'Erro desconhecido');
            }
        } catch (error) {
            console.error('Erro ao exportar:', error);
            updateStatus(`Erro: ${error.message}`);
            updateProgress(0, 0, false);
        } finally {
            exportBtn.disabled = false;
            addBtn.disabled = false;
        }
    });
    
    addBtn.addEventListener('click', async () => {
        try {
            exportBtn.disabled = true;
            addBtn.disabled = true;
            updateStatus('Iniciando processo...');
            updateProgress(0, 0, true);
            
            const settings = getSettings();
            const response = await fetch('http://localhost:5000/start', {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Resposta do servidor não é JSON válido');
            }
            
            const data = await response.json();
            
            if (data.success) {
                // Inicia polling de status
                const statusInterval = setInterval(async () => {
                    try {
                        const statusResponse = await fetch('http://localhost:5000/status', {
                            method: 'GET',
                            headers: {
                                'Accept': 'application/json'
                            }
                        });
                        
                        if (!statusResponse.ok) {
                            throw new Error(`HTTP error! status: ${statusResponse.status}`);
                        }
                        
                        const contentType = statusResponse.headers.get('content-type');
                        if (!contentType || !contentType.includes('application/json')) {
                            throw new Error('Resposta do servidor não é JSON válido');
                        }
                        
                        const statusData = await statusResponse.json();
                        
                        updateProgress(statusData.processed, statusData.total);
                        updateStatus(statusData.status);
                        
                        if (!statusData.running && statusData.finished) {
                            clearInterval(statusInterval);
                            exportBtn.disabled = false;
                            addBtn.disabled = false;
                        }
                    } catch (error) {
                        console.error('Erro ao verificar status:', error);
                        clearInterval(statusInterval);
                        updateStatus(`Erro: ${error.message}`);
                        exportBtn.disabled = false;
                        addBtn.disabled = false;
                    }
                }, 1000);
            } else {
                throw new Error(data.error || 'Erro desconhecido');
            }
        } catch (error) {
            console.error('Erro ao iniciar:', error);
            updateStatus(`Erro: ${error.message}`);
            updateProgress(0, 0, false);
            exportBtn.disabled = false;
            addBtn.disabled = false;
        }
    });
});
