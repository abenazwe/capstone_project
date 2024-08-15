document.getElementById('signupForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const name = document.getElementById('name').value;
    const email = document.getElementById('signupEmail').value;
    const password = document.getElementById('signupPassword').value;
   
    fetch('/signup/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({name, email, password }),
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
        alert('Sign up Successful! Check your Email.');
    })
    .catch(error => {
        console.error('Error during fetch:', error);
        alert('An error occurred while signing up. Please try again.');
    });
});
