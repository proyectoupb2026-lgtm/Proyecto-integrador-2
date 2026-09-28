document.addEventListener('DOMContentLoaded', () => {
    const btnGenerate = document.getElementById('btn-generate-tables');
    const btnSimulate = document.getElementById('btn-simulate');
    const matricesPanel = document.getElementById('matrices-panel');
    const resultsPanel = document.getElementById('results-panel');
    const loader = document.getElementById('loader');
    const resultsContent = document.getElementById('results-content');

    btnGenerate.addEventListener('click', () => {
        const numNodes = parseInt(document.getElementById('num_nodes').value);
        const numBases = parseInt(document.getElementById('num_bases').value);
        
        generateDemandInputs(numNodes);
        generateCapacityInputs(numBases);
        generateTravelTimeMatrix(numNodes, numBases);
        
        matricesPanel.style.display = 'block';
        resultsPanel.style.display = 'none';
        
        // Scroll to matrices
        matricesPanel.scrollIntoView({ behavior: 'smooth' });
    });

    btnSimulate.addEventListener('click', async () => {
        const numNodes = parseInt(document.getElementById('num_nodes').value);
        const numBases = parseInt(document.getElementById('num_bases').value);
        const numAmbulances = parseInt(document.getElementById('num_ambulances').value);
        const maxTime = parseFloat(document.getElementById('max_time').value);
        const alpha = parseFloat(document.getElementById('alpha').value);
        
        // Collect demands
        const demands = [];
        for (let i = 0; i < numNodes; i++) {
            demands.push(parseFloat(document.getElementById(`demand_${i}`).value) || 0);
        }
        
        // Collect capacities
        const capacities = [];
        for (let j = 0; j < numBases; j++) {
            capacities.push(parseInt(document.getElementById(`capacity_${j}`).value) || 0);
        }
        
        // Collect travel times
        const t_ij = [];
        for (let i = 0; i < numNodes; i++) {
            const row = [];
            for (let j = 0; j < numBases; j++) {
                row.push(parseFloat(document.getElementById(`tt_${i}_${j}`).value) || 0);
            }
            t_ij.push(row);
        }
        
        const payload = {
            num_nodes: numNodes,
            num_bases: numBases,
            num_ambulances: numAmbulances,
            T_max: maxTime,
            alpha: alpha,
            demands: demands,
            capacities: capacities,
            t_ij: t_ij
        };

        // UI Updates
        resultsPanel.style.display = 'block';
        resultsContent.style.display = 'none';
        loader.style.display = 'block';
        resultsPanel.scrollIntoView({ behavior: 'smooth' });

        try {
            const response = await fetch('/api/simulate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            
            if (response.ok) {
                renderResults(data);
            } else {
                alert('Error: ' + data.error);
                resultsPanel.style.display = 'none';
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al comunicar con el servidor.');
            resultsPanel.style.display = 'none';
        } finally {
            loader.style.display = 'none';
        }
    });

    function generateDemandInputs(numNodes) {
        const container = document.getElementById('demands-container');
        container.innerHTML = '';
        const grid = document.createElement('div');
        grid.className = 'dynamic-inputs';
        
        for (let i = 0; i < numNodes; i++) {
            const item = document.createElement('div');
            item.className = 'dynamic-input-item';
            
            // Random default demand between 10 and 100 for wow factor out-of-the-box
            const defaultDemand = Math.floor(Math.random() * 90) + 10;
            
            item.innerHTML = `
                <label>Nodo ${i}</label>
                <input type="number" id="demand_${i}" value="${defaultDemand}" min="0">
            `;
            grid.appendChild(item);
        }
        container.appendChild(grid);
    }

    function generateCapacityInputs(numBases) {
        const container = document.getElementById('capacities-container');
        container.innerHTML = '';
        const grid = document.createElement('div');
        grid.className = 'dynamic-inputs';
        
        for (let j = 0; j < numBases; j++) {
            const item = document.createElement('div');
            item.className = 'dynamic-input-item';
            
            item.innerHTML = `
                <label>Base ${j}</label>
                <input type="number" id="capacity_${j}" value="2" min="1">
            `;
            grid.appendChild(item);
        }
        container.appendChild(grid);
    }

    function generateTravelTimeMatrix(numNodes, numBases) {
        const thead = document.getElementById('travel-times-head');
        const tbody = document.getElementById('travel-times-body');
        
        thead.innerHTML = '<th>Nodos \\ Bases</th>';
        for (let j = 0; j < numBases; j++) {
            thead.innerHTML += `<th>Base ${j}</th>`;
        }
        
        tbody.innerHTML = '';
        for (let i = 0; i < numNodes; i++) {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td><strong>Nodo ${i}</strong></td>`;
            for (let j = 0; j < numBases; j++) {
                // Random default travel time between 5 and 25 mins
                const defaultTT = Math.floor(Math.random() * 20) + 5;
                tr.innerHTML += `<td><input type="number" id="tt_${i}_${j}" value="${defaultTT}" min="0" step="0.5"></td>`;
            }
            tbody.appendChild(tr);
        }
    }

    function renderResults(data) {
        resultsContent.style.display = 'block';
        
        // KPIs
        document.getElementById('kpi-avg-time').textContent = data.simulation.avg_response_time.toFixed(2) + ' min';
        document.getElementById('kpi-coverage').textContent = data.simulation.coverage_percent.toFixed(1) + ' %';
        document.getElementById('kpi-objective').textContent = data.optimisation.objective.toFixed(2);
        
        // Allocation
        const list = document.getElementById('allocation-list');
        list.innerHTML = '';
        
        const alloc = data.optimisation.allocation;
        for (const [base, count] of Object.entries(alloc)) {
            const li = document.createElement('li');
            li.innerHTML = `
                <span>Base ${base}</span>
                <span class="allocation-badge">${count} Ambulancias</span>
            `;
            list.appendChild(li);
        }
    }
});
