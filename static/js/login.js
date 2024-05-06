function login(event) {
    event.preventDefault();
    const username = document.getElementById('usernameLog').value;
    const password = document.getElementById('passwordLog').value;

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `username=${username}&password=${password}`
    })
    .then(response => {
        if (response.ok) {
            window.location.href = '/upload';
        } else {
            alert('Login Failed');
        }
    });
}

function register(event) {
    event.preventDefault();
    const username = document.getElementById('usernameReg').value;
    const password = document.getElementById('passwordReg').value;

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `username=${username}&password=${password}`
    })
    .then(response => response.text())
    .then(data => alert(data));
}
