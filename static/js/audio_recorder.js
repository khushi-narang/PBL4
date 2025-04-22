/**
 * Audio Recorder Module
 * Handles recording audio from the user's microphone using MediaRecorder API
 */
class AudioRecorder {
    constructor(visualizerCanvas) {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.stream = null;
        this.isRecording = false;
        this.audioContext = null;
        this.audioAnalyser = null;
        this.visualizerCanvas = visualizerCanvas;
        this.canvasContext = visualizerCanvas ? visualizerCanvas.getContext('2d') : null;
        
        // Callback for when processing is complete
        this.onProcessingComplete = null;
        
        // Bind methods
        this.startRecording = this.startRecording.bind(this);
        this.stopRecording = this.stopRecording.bind(this);
        this.onDataAvailable = this.onDataAvailable.bind(this);
        this.setupVisualizer = this.setupVisualizer.bind(this);
    }
    
    /**
     * Request microphone access and start recording
     */
    async startRecording() {
        try {
            // Request access to the microphone
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Create MediaRecorder instance with proper MIME type
            const options = { mimeType: 'audio/webm' };
            this.mediaRecorder = new MediaRecorder(this.stream, options);
            
            // Log the selected format
            console.log('MediaRecorder created with options:', options);
            
            // Set up event handlers
            this.mediaRecorder.ondataavailable = this.onDataAvailable.bind(this);
            
            // Clear previous recordings
            this.audioChunks = [];
            
            // Start recording
            this.mediaRecorder.start();
            this.isRecording = true;
            
            // Setup visualizer if canvas exists
            if (this.visualizerCanvas && this.canvasContext) {
                this.setupVisualizer();
            }
            
            console.log('Recording started');
        } catch (error) {
            console.error('Error starting recording:', error);
            throw new Error('Could not access the microphone. Please ensure you have given permission.');
        }
    }
    
    /**
     * Stop recording and process the audio
     */
    stopRecording() {
        if (!this.mediaRecorder || this.mediaRecorder.state === 'inactive') {
            return;
        }
        
        // Stop the recording
        this.mediaRecorder.stop();
        this.isRecording = false;
        
        // Stop all tracks in the stream
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
        
        // Clear visualizer if it exists
        if (this.visualizerCanvas && this.canvasContext) {
            this.canvasContext.clearRect(0, 0, this.visualizerCanvas.width, this.visualizerCanvas.height);
        }
        
        // Clean up audio context
        if (this.audioContext) {
            this.audioContext.close().catch(err => console.error('Error closing audio context:', err));
            this.audioContext = null;
            this.audioAnalyser = null;
        }
        
        console.log('Recording stopped');
        
        // Final processing happens in onDataAvailable after the mediaRecorder.stop()
    }
    
    /**
     * Handle recorded audio data
     */
    onDataAvailable(event) {
        if (event.data.size > 0) {
            this.audioChunks.push(event.data);
            
            // When recording stops, we'll have the complete audio
            if (this.mediaRecorder.state === 'inactive') {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                
                // Create a FormData object to send to the server
                const formData = new FormData();
                formData.append('audio', audioBlob, 'recording.webm');
                
                // Debug - show the blob info
                console.log('Audio Blob info:', {
                    type: audioBlob.type,
                    size: audioBlob.size
                });
                
                // Send the audio to the server for processing
                fetch('/process-audio', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(data => {
                            throw new Error(data.error || 'Server responded with an error');
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Server response:', data);
                    
                    // Call the callback function if it exists
                    if (typeof this.onProcessingComplete === 'function') {
                        this.onProcessingComplete(data);
                    }
                })
                .catch(error => {
                    console.error('Error sending audio to server:', error);
                    
                    // Call the callback function with the error
                    if (typeof this.onProcessingComplete === 'function') {
                        this.onProcessingComplete({ 
                            error: error.message || 'Failed to process audio' 
                        });
                    }
                });
            }
        }
    }
    
    /**
     * Setup audio visualizer
     */
    setupVisualizer() {
        if (!this.visualizerCanvas || !this.canvasContext || !this.stream) return;
        
        // Create audio context and connect to stream
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const source = this.audioContext.createMediaStreamSource(this.stream);
        
        // Create analyser node
        this.audioAnalyser = this.audioContext.createAnalyser();
        this.audioAnalyser.fftSize = 256;
        source.connect(this.audioAnalyser);
        
        const bufferLength = this.audioAnalyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        const width = this.visualizerCanvas.width;
        const height = this.visualizerCanvas.height;
        
        // Clear canvas
        this.canvasContext.clearRect(0, 0, width, height);
        
        // Draw the visualization
        const draw = () => {
            if (!this.isRecording || !this.audioAnalyser) return;
            
            requestAnimationFrame(draw);
            
            this.audioAnalyser.getByteFrequencyData(dataArray);
            
            this.canvasContext.fillStyle = 'rgb(32, 33, 36)'; // Dark background
            this.canvasContext.fillRect(0, 0, width, height);
            
            const barWidth = (width / bufferLength) * 2.5;
            let x = 0;
            
            for (let i = 0; i < bufferLength; i++) {
                const barHeight = (dataArray[i] / 255) * height;
                
                // Use a gradient for the bars
                const gradient = this.canvasContext.createLinearGradient(0, height, 0, 0);
                gradient.addColorStop(0, '#0D6EFD');  // Bootstrap primary
                gradient.addColorStop(1, '#6EA8FE');  // Lighter shade
                
                this.canvasContext.fillStyle = gradient;
                this.canvasContext.fillRect(x, height - barHeight, barWidth, barHeight);
                
                x += barWidth + 1;
            }
        };
        
        draw();
    }
}

// The initialization is now handled in app.js instead of here
// No automatic initialization to allow proper canvas reference passing
