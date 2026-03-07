document.getElementById('loginForm').addEventListener('submit', function(e) {
    // 1. FIXES "Broken pipe" (from your terminal image)
    // Prevents the browser from refreshing and killing the connection
    e.preventDefault(); 

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorBox = document.getElementById('error-message');
    const btn = document.getElementById('submitBtn');

    // Reset UI
    errorBox.style.display = 'none';
    btn.disabled = true;
    btn.innerText = 'Logging in...';

    // 2. The Fetch Request
    fetch('http://127.0.0.1:8000/api/auth/login/', {
        method: 'POST',
        headers: {
            // 3. FIXES "400 Bad Request"
            // Django REST Framework needs this to parse the request data
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        // Keys must match your Serializer (email, password)
        body: JSON.stringify({
            email: email,
            password: password
        })
    })
    .then(response => response.json().then(data => ({ status: response.status, body: data })))
    .then(res => {
        if (res.status === 200) {
            // SUCCESS: Store JWT tokens
            localStorage.setItem('access_token', res.body.access);
            localStorage.setItem('refresh_token', res.body.refresh);
            alert('Login Successful!');
            // window.location.href = '/home.html';
        } else {
            // ERROR: Show the validation message from your backend
            // Check for specific field errors or generic "non_field_errors"
            let msg = res.body.non_field_errors || res.body.detail || res.body.email || "Invalid login";
            errorBox.innerText = Array.isArray(msg) ? msg[0] : msg;
            errorBox.style.display = 'block';
        }
    })
    .catch(err => {
        errorBox.innerText = "Error: Check if backend server is running.";
        errorBox.style.display = 'block';
    })
    .finally(() => {
        btn.disabled = false;
        btn.innerText = 'Sign In';
    });
});