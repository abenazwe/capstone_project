document.addEventListener("DOMContentLoaded", function() {
    const nameInput = document.getElementById("name-meter");
    const locationInput = document.getElementById("meter-location");
    const submitButton = document.getElementById("addmeter");

    submitButton.addEventListener('click', function(event) {
        event.preventDefault();
        addMeter();
    });
    
    function addMeter() {
        const name = nameInput.value.trim();
        const location = locationInput.value.trim();
    
        if (name === "" || location === "") {
            alert("Please fill in all fields.");
            return;
        }
    
        const meterData = {
            name: name,
            location: location
        };
    
        fetch('/add_meter', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(meterData)
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                return response.json().then(err => {throw err});
            }
        })
        .then(data => {
            alert("Meter added successfully!");
            if (data.product) {
                updateDashboard(data.product);
            }
            nameInput.value = "";
            locationInput.value = "";
        })
        .catch(error => {
            console.error('Error:', error);
            alert("An error occurred while adding the meter.");
        });
    }
    
    function updateDashboard(product) {
        const recordsBody = document.getElementById('recordsBody');
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${product.product_id}</td>
            <td>${product.name}</td>
            <td>${product.location}</td>
            <td><button onclick="window.location.href='/viewdetails/${product.id}'">View Details</button></td>
        `;
        recordsBody.appendChild(row);
    }
    
});
