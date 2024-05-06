// Function to register a new user
function register() {
    const username = document.getElementById('usernameReg').value;
    const password = document.getElementById('passwordReg').value;

    fetch(`${apiUrl}/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => alert(data.message))
    .catch(error => console.error('Error:', error));
}

// Function to log in a user
function login() {
    const username = document.getElementById('usernameLog').value;
    const password = document.getElementById('passwordLog').value;

    fetch(`${apiUrl}/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.access_token) {
            sessionStorage.setItem('jwt', data.access_token);
            alert('Logged in successfully');
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}

// Function to upload a file
function uploadFile() {
    const file = document.getElementById('fileUpload').files[0];
    const formData = new FormData();
    formData.append('file', file);

    fetch(`${apiUrl}/upload`, {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + sessionStorage.getItem('jwt')
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => alert(data.message))
    .catch(error => console.error('Error:', error));
}

// Set the base URL for the API
const apiUrl = 'http://127.0.0.1:5000/';
