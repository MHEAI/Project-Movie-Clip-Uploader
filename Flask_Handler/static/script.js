document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('mediaForm');
    const playlistRadio = document.getElementById('playlist');
    const uploadRadio = document.getElementById('upload');
    const playlistSection = document.getElementById('playlistSection');
    const uploadSection = document.getElementById('uploadSection');
    const buttonText = document.getElementById('buttonText');
    const fileInput = document.getElementById('movie-file');
    const fileInfo = document.getElementById('fileInfo');
    const videoCountHelp = document.getElementById('videoCountHelp');
    function showProcessingComplete(message, isSuccess = true) {
    const statusElement = document.getElementById('processingStatus');
    const statusMessage = document.getElementById('statusMessage');
    const statusIcon = statusElement.querySelector('.status-icon');
    const statusTitle = statusElement.querySelector('.status-title');

    // Remove the 'hidden' class to show the status
    statusElement.classList.remove('hidden');

    if (isSuccess === true || isSuccess === "true") {
        statusElement.style.background = 'linear-gradient(135deg, #dcfdf7 0%, #f0fdf4 100%)';
        statusElement.style.borderColor = '#a7f3d0';
        statusIcon.style.backgroundColor = '#10b981';
        statusTitle.textContent = 'Processing Complete!';
        statusTitle.style.color = '#047857';
    } else {
        statusElement.style.background = 'linear-gradient(135deg, #fef2f2 0%, #fdf2f8 100%)';
        statusElement.style.borderColor = '#fecaca';
        statusIcon.style.backgroundColor = '#ef4444';
        statusTitle.textContent = 'Processing Failed';
        statusTitle.style.color = '#dc2626';
    }

    statusMessage.textContent = message;
}
    // Handle radio button toggle
    function handleOptionChange() {
        if (playlistRadio.checked) {
            playlistSection.classList.remove('hidden');
            uploadSection.classList.add('hidden');
            buttonText.textContent = 'Analyze Playlist';
            videoCountHelp.textContent = 'Specify how many videos to process from the playlist';
            fileInput.removeAttribute('required');
            document.getElementById('playlist-url').setAttribute('required', '');
        } else {
            playlistSection.classList.add('hidden');
            uploadSection.classList.remove('hidden');
            buttonText.textContent = 'Upload & Process';
            videoCountHelp.textContent = 'Specify how many video files you want to upload';
            document.getElementById('playlist-url').removeAttribute('required');
            fileInput.setAttribute('required', '');
        }
        fileInfo.classList.add('hidden');
        fileInfo.textContent = '';
    }

    // Show file info when selecting a file
    function handleFileChange(event) {
        const file = event.target.files[0];
        if (file) {
            const fileSizeMB = (file.size / 1024 / 1024).toFixed(2);
            fileInfo.textContent = `Selected: ${file.name} (${fileSizeMB} MB)`;
            fileInfo.classList.remove('hidden');
        } else {
            fileInfo.classList.add('hidden');
            fileInfo.textContent = '';
        }
    }

    // When submitting the form
    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const formData = new FormData(form);

        fetch('/process', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
    console.log('Processing complete:', data);
    showProcessingComplete(data.message, data.success);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    // Event listeners for radio buttons and file selection
    playlistRadio.addEventListener('change', handleOptionChange);
    uploadRadio.addEventListener('change', handleOptionChange);
    fileInput.addEventListener('change', handleFileChange);

    // Initialize on page load
    handleOptionChange();
});
