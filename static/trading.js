// ─── State ────────────────────────────────────────────────────────────
let currentSymbol = 'TSLA';
let currentSide   = 'BUY';
let currentType   = 'LIMIT';

const MAX_ROWS = 12; // max price levels to display per side

// ─── Symbol ───────────────────────────────────────────────────────────
function setSymbol(symbol) {
    currentSymbol = symbol;

    document.querySelectorAll('.symbol-tab').forEach(btn => {
        btn.classList.toggle('active', btn.textContent === symbol);
    });

    document.getElementById('submit-symbol').textContent = symbol;
    refreshAll();
}

// ─── Side (Buy / Sell) ────────────────────────────────────────────────
function setSide(side) {
    currentSide = side;

    document.getElementById('btn-buy').classList.toggle('active', side === 'BUY');
    document.getElementById('btn-sell').classList.toggle('active', side === 'SELL');

    const submitBtn = document.getElementById('submit-btn');
    submitBtn.className = `submit-btn ${side === 'BUY' ? 'buy' : 'sell'}`;
    submitBtn.firstChild.textContent = side === 'BUY' ? 'Buy ' : 'Sell ';
}

// ─── Order Type ───────────────────────────────────────────────────────
function setType(type) {
    currentType = type;

    document.querySelectorAll('.type-tab').forEach(btn => {
        btn.classList.toggle('active', btn.id === `tab-${type}`);
    });

    // Hide price input for pure market orders
    document.getElementById('price-group').style.display =
        type === 'MARKET' ? 'none' : 'flex';
}

// ─── Status message ───────────────────────────────────────────────────
let statusTimer = null;

function showStatus(message, type) {
    const el = document.getElementById('status-msg');
    el.textContent  = message;
    el.className    = `status-msg ${type}`;

    clearTimeout(statusTimer);
    statusTimer = setTimeout(() => { el.className = 'status-msg'; }, 4000);
}

// ─── Order Book ───────────────────────────────────────────────────────
function renderBook(data) {
    const asksEl   = document.getElementById('asks-rows');
    const bidsEl   = document.getElementById('bids-rows');
    const spreadEl = document.getElementById('spread-value');
    const priceEl  = document.getElementById('current-price');

    priceEl.textContent = `$${(data.price || 0).toFixed(2)}`;

    // Build sorted arrays
    const asks = Object.entries(data.asks)
        .map(([p, qtys]) => ({ price: parseFloat(p), size: qtys.reduce((a, b) => a + b, 0) }))
        .sort((a, b) => a.price - b.price)   // ascending; CSS column-reverse flips display
        .slice(0, MAX_ROWS);

    const bids = Object.entries(data.bids)
        .map(([p, qtys]) => ({ price: parseFloat(p), size: qtys.reduce((a, b) => a + b, 0) }))
        .sort((a, b) => b.price - a.price)   // descending: best bid first
        .slice(0, MAX_ROWS);

    // Depth bars scaled to the max size on each side
    const maxAsk = asks.reduce((m, r) => Math.max(m, r.size), 0) || 1;
    const maxBid = bids.reduce((m, r) => Math.max(m, r.size), 0) || 1;

    // Running totals
    let askTotal = 0;
    let bidTotal = 0;

    asksEl.innerHTML = asks.map(row => {
        askTotal += row.size;
        const pct = ((row.size / maxAsk) * 100).toFixed(1);
        return `
            <div class="book-row ask" style="--depth:${pct}%">
                <span>$${row.price.toFixed(2)}</span>
                <span>${row.size.toLocaleString()}</span>
                <span>${askTotal.toLocaleString()}</span>
            </div>`;
    }).join('');

    bidsEl.innerHTML = bids.map(row => {
        bidTotal += row.size;
        const pct = ((row.size / maxBid) * 100).toFixed(1);
        return `
            <div class="book-row bid" style="--depth:${pct}%">
                <span>$${row.price.toFixed(2)}</span>
                <span>${row.size.toLocaleString()}</span>
                <span>${bidTotal.toLocaleString()}</span>
            </div>`;
    }).join('');

    // Spread
    const bestAsk = asks[0]?.price;
    const bestBid = bids[0]?.price;
    if (bestAsk && bestBid) {
        const spread    = bestAsk - bestBid;
        const spreadPct = ((spread / bestAsk) * 100).toFixed(3);
        spreadEl.textContent = `$${spread.toFixed(2)} (${spreadPct}%)`;
    } else {
        spreadEl.textContent = '—';
    }
}

function fetchBook() {
    fetch(`/api/orderbook/${currentSymbol}`)
        .then(r => r.json())
        .then(renderBook)
        .catch(err => console.error('Order book fetch failed:', err));
}

// ─── Trades ───────────────────────────────────────────────────────────
function renderTrades(data) {
    const el = document.getElementById('trades-list');
    const entries = Object.entries(data).reverse(); // most recent first

    if (!entries.length) {
        el.innerHTML = '<div class="empty-state">No trades yet</div>';
        return;
    }

    el.innerHTML = entries.map(([id, t]) => {
        const side  = t.type === 'MARKET' ? 'ask' : 'bid';
        return `
            <div class="trade-row">
                <span class="trade-price ${side}">$${parseFloat(t.price).toFixed(2)}</span>
                <span>${t.quantity.toLocaleString()}</span>
                <span>#${id}</span>
            </div>`;
    }).join('');
}

function fetchTrades() {
    fetch('/api/trades')
        .then(r => r.json())
        .then(renderTrades)
        .catch(err => console.error('Trades fetch failed:', err));
}

// ─── Place Order ──────────────────────────────────────────────────────
function placeOrder() {
    const priceInput = document.getElementById('price');
    const qtyInput   = document.getElementById('quantity');

    const price    = currentType === 'MARKET' ? 0 : parseFloat(priceInput.value);
    const quantity = parseInt(qtyInput.value);

    if (currentType !== 'MARKET' && (isNaN(price) || price <= 0)) {
        showStatus('Enter a valid price.', 'error');
        return;
    }
    if (isNaN(quantity) || quantity <= 0) {
        showStatus('Enter a valid quantity.', 'error');
        return;
    }

    const payload = {
        symbol:   currentSymbol,
        side:     currentSide,
        type:     currentType,
        price:    price,
        quantity: quantity,
    };

    const btn = document.getElementById('submit-btn');
    btn.disabled = true;

    fetch('/api/order', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload),
    })
    .then(r => {
        if (!r.ok) return r.json().then(e => { throw new Error(e.detail); });
        return r.json();
    })
    .then(data => {
        showStatus(`Order #${data.order_id} placed successfully.`, 'success');
        priceInput.value = '';
        qtyInput.value   = '';
        refreshAll();
    })
    .catch(err => showStatus(err.message, 'error'))
    .finally(()  => { btn.disabled = false; });
}

// ─── Refresh ──────────────────────────────────────────────────────────
function refreshAll() {
    fetchBook();
    fetchTrades();
}

// ─── Init ─────────────────────────────────────────────────────────────
refreshAll();
setInterval(refreshAll, 2000);
