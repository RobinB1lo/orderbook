let currentSymbol = "TSLA";

function updateSymbol() {
    currentSymbol = document.getElementById('symbol').value;
    document.getElementById('current-symbol').textContent = currentSymbol;
    updateOrderBook();
    updateTrades();
}

function updateOrderBook() {
    const symbol = document.getElementById('symbol').value;
    document.getElementById('current-symbol').textContent = symbol;
    
    fetch(`/api/orderbook/${symbol}`)
        .then(response => response.json())
        .then(data => {
            let html = `<h3>Current Price: $${(data.price || 100).toFixed(2)}</h3>`;
            
            html += '<h3>Bids</h3><table>';
            Object.entries(data.bids)
                .sort((a, b) => parseFloat(b[0]) - parseFloat(a[0]))
                .forEach(([price, quantities]) => {
                    const total = quantities.reduce((sum, qty) => sum + qty, 0);
                    html += `<tr><td>$${parseFloat(price).toFixed(2)}</td><td>${total}</td></tr>`;
                });
            
            html += '</table><h3>Asks</h3><table>';
            Object.entries(data.asks)
                .sort((a, b) => parseFloat(a[0]) - parseFloat(b[0]))
                .forEach(([price, quantities]) => {
                    const total = quantities.reduce((sum, qty) => sum + qty, 0);
                    html += `<tr><td>$${parseFloat(price).toFixed(2)}</td><td>${total}</td></tr>`;
                });
            
            document.getElementById('order-book').innerHTML = html + '</table>';
        })
        .catch(error => {
            console.error('Error fetching order book:', error);
            document.getElementById('order-book').innerHTML = 'Failed to load order book';
        });
}
function placeOrder() {
    const order = {
        symbol: currentSymbol,
        side: document.getElementById('side').value,
        type: document.getElementById('type').value,
        price: parseFloat(document.getElementById('price').value),
        quantity: parseInt(document.getElementById('quantity').value)
    };

    if (isNaN(order.price) || isNaN(order.quantity) || order.quantity <= 0) {
        alert("Please enter valid price and quantity");
        return;
    }

    fetch('/api/order', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(order)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.detail); });
        }
        return response.json();
    })
    .then(data => {
        alert(`Order placed successfully! ID: ${data.order_id}`);
        updateOrderBook();
        updateTrades();
    })
    .catch(error => {
        alert(`Order failed: ${error.message}`);
    });
}

function updateTrades() {
    fetch(`/api/trades`)
        .then(response => response.json())
        .then(data => {
            let html = '<h3>Trades</h3><table>';
            
            Object.entries(data).forEach(([tradeId, trade]) => {
                html += `<tr>
                            <td>ID: ${tradeId}</td>
                            <td>Price: $${parseFloat(trade.price).toFixed(2)}</td>
                            <td>Quantity: ${trade.quantity}</td>
                            <td>Type: ${trade.type}</td>
                         </tr>`;
            });

            html += '</table>';
            document.getElementById('trades').innerHTML = html;
        })
        .catch(error => {
            console.error('Error fetching trades:', error);
            document.getElementById('trades').innerHTML = 'Failed to load trades';
        });
}


updateOrderBook();
updateTrades();
setInterval(() => {
    updateOrderBook();
    updateTrades();
}, 2000);