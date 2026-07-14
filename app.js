const DATA_URL = 'data/prices.json';

let priceData = null;
let priceChart = null;
let currentPurity = '24K';
let currentDays = 10;

const $ = id => document.getElementById(id);

const fmt = n => n == null ? '--' : '₹' + Number(n).toLocaleString('en-IN');

const els = {
    lastUpdated: $('last-updated'),
    price24k: $('price-24k'),
    price22k: $('price-22k'),
    price18k: $('price-18k'),
    change24k: $('change-24k'),
    change22k: $('change-22k'),
    weightTable: $('weight-table'),
    historyTable: $('history-table'),
    chart: $('price-chart'),
};

function parseChange(str) {
    if (!str) return { text: '--', cls: 'neutral' };
    const n = parseFloat(str.replace(/[^\d.\-]/g, ''));
    if (isNaN(n)) return { text: str, cls: 'neutral' };
    const abs = Math.abs(n);
    return {
        text: (n < 0 ? '↓ ' : n > 0 ? '↑ ' : '') + '₹' + abs.toLocaleString('en-IN'),
        cls: n < 0 ? 'down' : n > 0 ? 'up' : 'neutral'
    };
}

function renderKPICards(current) {
    // 24K
    els.price24k.textContent = fmt(current['24K_per_gram']);
    const c24 = parseChange(current['24K_change']);
    els.change24k.textContent = c24.text;
    els.change24k.className = 'card-change ' + c24.cls;

    // 22K
    els.price22k.textContent = fmt(current['22K_per_gram']);
    const c22 = parseChange(current['22K_change']);
    els.change22k.textContent = c22.text;
    els.change22k.className = 'card-change ' + c22.cls;

    // 18K
    els.price18k.textContent = fmt(current['18K_per_gram']);
}

function renderWeightTable(perWeight) {
    if (!perWeight) {
        els.weightTable.innerHTML = '<tr><td colspan="4" style="text-align:center;color:#94a3b8;padding:32px">No data</td></tr>';
        return;
    }
    els.weightTable.innerHTML = Object.entries(perWeight).map(([w, p]) => `
        <tr>
            <td>${w} gram${w > 1 ? 's' : ''}</td>
            <td>${fmt(p['24K'])}</td>
            <td>${fmt(p['22K'])}</td>
            <td>${fmt(p['18K'])}</td>
        </tr>
    `).join('');
}

function renderHistoryTable(history) {
    if (!history || !history.length) {
        els.historyTable.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#94a3b8;padding:32px">No history</td></tr>';
        return;
    }
    els.historyTable.innerHTML = history.slice(0, 14).map((item, i) => {
        const prev = history[i + 1];
        let ch24 = '--', cls24 = 'change-flat';
        let ch22 = '--', cls22 = 'change-flat';

        if (prev && prev['24K'] != null && item['24K'] != null) {
            const d = item['24K'] - prev['24K'];
            ch24 = (d < 0 ? '-' : '+') + '₹' + Math.abs(d).toLocaleString('en-IN');
            cls24 = d < 0 ? 'change-down' : d > 0 ? 'change-up' : 'change-flat';
        }
        if (prev && prev['22K'] != null && item['22K'] != null) {
            const d = item['22K'] - prev['22K'];
            ch22 = (d < 0 ? '-' : '+') + '₹' + Math.abs(d).toLocaleString('en-IN');
            cls22 = d < 0 ? 'change-down' : d > 0 ? 'change-up' : 'change-flat';
        }

        return `<tr>
            <td>${item.date}</td>
            <td>${fmt(item['24K'])}</td>
            <td class="${cls24}">${ch24}</td>
            <td>${fmt(item['22K'])}</td>
            <td class="${cls22}">${ch22}</td>
        </tr>`;
    }).join('');
}

function renderChart(history) {
    if (!history || !history.length) return;

    const sorted = [...history].sort((a, b) => new Date(a.date) - new Date(b.date));
    const data = sorted.slice(-currentDays);

    const labels = data.map(d => {
        const dt = new Date(d.date);
        return dt.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
    });

    const values = data.map(d => d[currentPurity]);
    const color = currentPurity === '24K' ? '#f59e0b' : '#6366f1';

    const config = {
        type: 'line',
        data: {
            labels,
            datasets: [{
                data: values,
                borderColor: color,
                backgroundColor: color + '15',
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointHoverRadius: 6,
                borderWidth: 2.5,
                pointBackgroundColor: color,
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1a1a2e',
                    titleFont: { size: 12, family: 'Inter' },
                    bodyFont: { size: 14, family: 'Inter', weight: '600' },
                    padding: { top: 10, bottom: 10, left: 14, right: 14 },
                    cornerRadius: 10,
                    displayColors: false,
                    callbacks: {
                        label: ctx => currentPurity + ': ₹' + ctx.parsed.y.toLocaleString('en-IN')
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 11, family: 'Inter' }, color: '#94a3b8', maxTicksLimit: 7 }
                },
                y: {
                    grid: { color: '#f1f5f9' },
                    ticks: {
                        font: { size: 11, family: 'Inter' },
                        color: '#94a3b8',
                        callback: v => '₹' + (v / 1000).toFixed(1) + 'k'
                    }
                }
            }
        }
    };

    if (priceChart) priceChart.destroy();
    priceChart = new Chart(els.chart, config);
}

function updateTimestamp(ts) {
    if (!ts) { els.lastUpdated.textContent = 'No data'; return; }
    const d = new Date(ts);
    const now = new Date();
    const mins = Math.floor((now - d) / 60000);
    const hrs = Math.floor(mins / 60);
    const text = mins < 1 ? 'Just now' : mins < 60 ? `${mins}m ago` : hrs < 24 ? `${hrs}h ago` : d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
    els.lastUpdated.textContent = 'Updated ' + text;
}

async function loadData() {
    try {
        els.lastUpdated.textContent = 'Loading...';
        const r = await fetch(DATA_URL + '?t=' + Date.now());
        if (!r.ok) throw new Error('Fetch failed');
        priceData = await r.json();

        renderKPICards(priceData.current);
        renderWeightTable(priceData.current.per_weight);
        renderHistoryTable(priceData.history);
        renderChart(priceData.history);
        updateTimestamp(priceData.last_updated);
    } catch (e) {
        console.error(e);
        els.lastUpdated.textContent = 'Failed to load';
    }
}

// Purity toggle
document.querySelectorAll('.toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentPurity = btn.dataset.purity;
        if (priceData) renderChart(priceData.history);
    });
});

// Range toggle
document.querySelectorAll('.range-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.range-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentDays = parseInt(btn.dataset.days);
        if (priceData) renderChart(priceData.history);
    });
});

// Init
loadData();
setInterval(loadData, 5 * 60 * 1000);
