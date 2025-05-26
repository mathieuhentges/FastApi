document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('upload-form');
    const spinner = document.getElementById('spinner');
    const messageDiv = document.getElementById('message');
    const MAX_FILE_SIZE = 2 * 1024 * 1024; // 2MB

    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        const formData = new FormData(form);

        spinner.style.display = 'block';
        messageDiv.textContent = '';
        messageDiv.style.color = '';

        try {
            const fileInput = document.getElementById('file');
            const files = fileInput.files;
            if (files.length !== 1) {
                messageDiv.textContent = '❌ Please upload exactly one file.';
                messageDiv.style.color = 'red';
                return;
}
            const file = files[0];
            if (file && file.size > MAX_FILE_SIZE) {
                messageDiv.textContent = 'File too large. Maximum size is 2MB.';
                messageDiv.style.color = 'red';
                return;
            }

            const response = await fetch('/submitApplication', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                messageDiv.textContent = `File "${data.filename}" uploaded to application ${data.name}.`;
                messageDiv.style.color = 'green';
                form.reset();
            } else {
                messageDiv.textContent = `Error: ${data.detail}`;
                messageDiv.style.color = 'red';
            }

        } catch (error) {
            messageDiv.textContent = 'Unexpected error occurred.';
            messageDiv.style.color = 'red';
        } finally {
            spinner.style.display = 'none';
        }
    });
});