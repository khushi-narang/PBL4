/**
 * Main Application JavaScript
 * Handles UI interactions and display of results
 */
document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const saveTranslationBtn = document.getElementById('saveTranslationBtn');
    const statusElement = document.getElementById('status');
    const processingDiv = document.getElementById('processingDiv');
    const resultsDiv = document.getElementById('resultsDiv');
    const noResultsDiv = document.getElementById('noResultsDiv');
    const errorDiv = document.getElementById('errorDiv');
    const errorMessage = document.getElementById('errorMessage');
    const recognizedTextElement = document.getElementById('recognizedText');
    const glossTextElement = document.getElementById('glossText');
    const videosDiv = document.getElementById('videosDiv');
    const noVideosDiv = document.getElementById('noVideosDiv');
    const saveBtn = document.getElementById('saveBtn');
    const canvas = document.getElementById('audioVisualizer');
    
    // Initialize the audio recorder
    const audioRecorder = new AudioRecorder(canvas);
    
    // Latest translation data
    let currentTranslation = null;
    
    // Add event listeners for the recorder buttons
    startBtn.addEventListener('click', async () => {
        try {
            await audioRecorder.startRecording();
            statusElement.textContent = 'Recording... Speak clearly into your microphone';
            statusElement.classList.add('text-danger');
            startBtn.disabled = true;
            stopBtn.disabled = false;
            
            // Hide results and errors
            resultsDiv.classList.add('d-none');
            errorDiv.classList.add('d-none');
            saveBtn.classList.add('d-none');
        } catch (error) {
            console.error('Error starting recording:', error);
            showError('Could not access microphone. Please check your browser permissions.');
        }
    });
    
    stopBtn.addEventListener('click', () => {
        audioRecorder.stopRecording();
        statusElement.textContent = 'Processing audio...';
        statusElement.classList.remove('text-danger');
        statusElement.classList.add('text-warning');
        stopBtn.disabled = true;
        startBtn.disabled = true;
        
        // Show processing indicator
        processingDiv.classList.remove('d-none');
        
        // Hide videos while processing
        videosDiv.classList.add('d-none');
        noVideosDiv.classList.add('d-none');
    });
    
    // Save translation button event
    saveTranslationBtn.addEventListener('click', () => {
        if (currentTranslation && currentTranslation.translation_id) {
            window.location.href = `/translation/${currentTranslation.translation_id}`;
        }
    });
    
    // Event handler for when audio processing is complete
    audioRecorder.onProcessingComplete = (data) => {
        // Hide processing indicator
        processingDiv.classList.add('d-none');
        
        // Enable recording button again
        startBtn.disabled = false;
        
        if (data.error) {
            // Show error message
            showError(data.error);
            return;
        }
        
        // Store the translation data
        currentTranslation = data;
        
        // Show results
        resultsDiv.classList.remove('d-none');
        noResultsDiv.classList.add('d-none');
        
        // Display recognized text
        recognizedTextElement.textContent = data.text;
        
        // Display ISL gloss
        glossTextElement.innerHTML = '';
        data.gloss.forEach(word => {
            const glossItem = document.createElement('span');
            glossItem.className = 'badge bg-primary me-2 mb-2';
            glossItem.textContent = word;
            glossTextElement.appendChild(glossItem);
        });
        
        // Show save button if we have a translation ID
        if (data.translation_id) {
            saveBtn.classList.remove('d-none');
        }
        
        // Display videos
        displayVideos(data.videos);
        
        // Update status
        statusElement.textContent = 'Translation complete!';
        statusElement.classList.remove('text-warning');
        statusElement.classList.add('text-success');
    };
    
    // Function to display videos
    function displayVideos(videos) {
        videosDiv.innerHTML = '';
        
        if (!videos || videos.length === 0) {
            videosDiv.classList.add('d-none');
            noVideosDiv.classList.remove('d-none');
            return;
        }
        
        videos.forEach(video => {
            const videoCol = document.createElement('div');
            videoCol.className = 'col-md-4 col-lg-3 mb-4';
            
            const videoCard = document.createElement('div');
            videoCard.className = 'card h-100';
            
            const cardHeader = document.createElement('div');
            cardHeader.className = 'card-header';
            cardHeader.textContent = video.gloss;
            
            const cardBody = document.createElement('div');
            cardBody.className = 'card-body text-center';
            
            const videoElement = document.createElement('video');
            videoElement.className = 'w-100';
            videoElement.controls = true;
            videoElement.autoplay = false;
            videoElement.loop = true;
            
            const source = document.createElement('source');
            source.src = video.video_path;
            source.type = 'video/mp4';
            
            videoElement.appendChild(source);
            cardBody.appendChild(videoElement);
            videoCard.appendChild(cardHeader);
            videoCard.appendChild(cardBody);
            videoCol.appendChild(videoCard);
            videosDiv.appendChild(videoCol);
        });
        
        videosDiv.classList.remove('d-none');
        noVideosDiv.classList.add('d-none');
    }
    
    // Function to show error messages
    function showError(message) {
        errorMessage.textContent = message;
        errorDiv.classList.remove('d-none');
        resultsDiv.classList.add('d-none');
        noResultsDiv.classList.add('d-none');
        videosDiv.classList.add('d-none');
        noVideosDiv.classList.remove('d-none');
        
        statusElement.textContent = 'Error occurred';
        statusElement.className = 'text-danger';
    }
});
