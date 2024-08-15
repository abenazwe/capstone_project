
document.addEventListener("DOMContentLoaded", function() {
    fetchProducts();
    setInterval(fetchProducts, 60000); // Poll every 60 seconds
});

let displayedProductIds = new Set();

function fetchProducts() {
    fetch('/products', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
    })
    .then(response => response.json())
    .then(data => {
        const recordsBody = document.getElementById('recordsBody');
        data.forEach(product => {
            if (!displayedProductIds.has(product.product_id)) {
                displayedProductIds.add(product.product_id);
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${product.product_id}</td>
                    <td>${product.location}</td>
                    <td><button onclick="window.location.href='/viewdetails/${product.product_id}'">View Details</button></td>
                `;
                recordsBody.appendChild(row);
            }
        });
    })
    .catch(error => console.error('Error:', error));
}
