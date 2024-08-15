document.addEventListener("DOMContentLoaded", function() {
    fetchSensorData();
    setInterval(fetchSensorData, 30000); 
});

function fetchSensorData() {
    const userId = localStorage.getItem('user_id');  // Retrieving user_id from local storage
    if (!userId) {
        console.error('User ID not found');
        return;
    }

    fetch(`/most_recent_sensor_data/${userId}/`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            console.error('Error:', data.error);
            return;
        }
        console.log('Data:', data);
        document.getElementById('energy-consumption').innerText = data.energy || 'N/A';
        document.getElementById('power-consumption').innerText = data.power || 'N/A';
        document.getElementById('current-consumption').innerText = data.current || 'N/A';
        document.getElementById('voltage-consumption').innerText = data.voltage || 'N/A';

        // Check for anomalies
        checkForAnomalies(userId);
    })
    .catch(error => console.error('Error:', error));
}

function checkForAnomalies(userId) {
    fetch(`/check_anomalies/${userId}/`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
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
