document.getElementById('dataPostForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const product_id = document.getElementById('product_id').value;
    const voltage = document.getElementById('voltage').value;
    const current = document.getElementById('current').value;
    const power = document.getElementById('power').value;
    const energy = document.getElementById('energy').value;
    const kVA = document.getElementById('kVA').value;
    const power_factor = document.getElementById('power_factor').value;
    const billing = document.getElementById('billing').value;

    fetch('/data_post/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id, voltage, current, power, energy, kVA, power_factor, billing
        }),
    })
    .then(response => {
        console.log("This is the response: ", response);
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        console.log("Response data: ", data);
        alert('Data saved successfully!');
        if (data.anomaly_detected) {
            alert('Anomaly Detected! A False Data Injection Attack Has Been Detected.');
        }
    })
    .catch(error => {
        console.error('Error during fetch:', error);
        alert('An error occurred while posting data. Please try again.');
    });
});
