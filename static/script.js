
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('mediaForm');
    const playlistRadio = document.getElementById('playlist');
    const uploadRadio = document.getElementById('upload');
    const playlistSection = document.getElementById('playlistSection');
    const uploadSection = document.getElementById('uploadSection');
    const buttonText = document.getElementById('buttonText');
    const supportText = document.getElementById('supportText');
    const fileInput = document.getElementById('movie-file');
    const fileInfo = document.getElementById('fileInfo');
    const videoCountHelp = document.getElementById('videoCountHelp');
    // Handle radio button changes
    function handleOptionChange() {
        if (playlistRadio.checked) {
            playlistSection.classList.remove('hidden');
            uploadSection.classList.add('hidden');
            buttonText.textContent = 'Analyze Playlist';
            supportText.textContent = 'Supports YouTube playlists and individual video URLs';
            videoCountHelp.textContent = 'Specify how many videos to process from the playlist';
            // Remove required from file input
            fileInput.removeAttribute('required');
            // Add required to playlist URL
            document.getElementById('playlist-url').setAttribute('required', '');
        } else {
            playlistSection.classList.add('hidden');
            uploadSection.classList.remove('hidden');
            buttonText.textContent = 'Upload & Process';
            supportText.textContent = 'Supports MP4, AVI, MOV, and other common video formats';
            videoCountHelp.textContent = 'Specify how many video files you want to upload';
            // Remove required from playlist URL
            document.getElementById('playlist-url').removeAttribute('required');
            // Add required to file input
            fileInput.setAttribute('required', '');
        }
        
        // Clear file info when switching options
        fileInfo.classList.add('hidden');
        fileInfo.textContent = '';
    }

    // Handle file selection
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

    // Event listeners
    playlistRadio.addEventListener('change', handleOptionChange);
    uploadRadio.addEventListener('change', handleOptionChange);
    fileInput.addEventListener('change', handleFileChange);

    // Initialize the form state
    handleOptionChange();
});
