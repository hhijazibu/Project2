function uploadFile(event) {
    event.preventDefault();
    const file = document.getElementById('fileUpload').files[0];
    const formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(data => alert(data));
}
