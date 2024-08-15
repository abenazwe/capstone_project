document.addEventListener("DOMContentLoaded", function() {
    fetchSensorData();
    setInterval(fetchSensorData, 5000); // Poll every 5 seconds
});

function getProductIdFromUrl() {
    const url = window.location.pathname;
    const urlParts = url.split('/');
    const productId = urlParts[2];
    return productId;
}

function fetchSensorData() {
    const productId = getProductIdFromUrl();
    console.log("Product ID:", productId);

    fetch(`/sensor_data_details/${productId}/`)
    .then(response => response.json())
    .then(data => {
        if (data) {
            document.getElementById('energy-consumption').innerText = data.energy;
            document.getElementById('power-consumption').innerText = data.power;
            document.getElementById('current-consumption').innerText = data.current;
            document.getElementById('voltage-consumption').innerText = data.voltage;

            // Check for anomalies
            checkForAnomalies(data.user_id);
        } else {
            console.error('No data found for this product ID');
        }
    })
    .catch(error => console.error('Error:', error));
}

function checkForAnomalies(user_id) {
    fetch(`/check_anomalies/${user_id}/`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok'+ response.statusText);
        }
        return response.json();
    })
    .then(data => {
        if (data.anomaly_detected) {
            alert('Anomaly Detected! A False Data Injection Attack Has Been Detected.');
        }
    })
    .catch(error => console.error('Error checking for anomalies:', error));
}
