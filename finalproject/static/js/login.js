function authenticateUser(email, password) {
    const apiUrl = 'http://127.0.0.1:8000/login/';

    return fetch(apiUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json());
}

document.getElementById('loginForm').addEventListener('submit', function (event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
   
    authenticateUser(email, password)
        .then(response => {
            if (response.message === "Login successful") {
                localStorage.setItem('token', response.token);
                localStorage.setItem('role', response.role);
                localStorage.setItem('email', response.email);
                localStorage.setItem('name', response.name);
                localStorage.setItem('user_id', response.user_id);  // Store user_id

                if (response.role === 'Administrator') {
                    window.location.href = '/admin_dashboard';
                } else {
                    window.location.href = '/user_page';
                }
            } else {
                document.getElementById('loginMessage').innerHTML = response.error || "Login failed. Please try again";
            }
        })
        .catch(error => {
            console.log(error);
            document.getElementById('loginMessage').innerHTML = error.message;
        });
});
