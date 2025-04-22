import os
import logging
import tempfile
import subprocess
import json

# Import speech_recognition with error handling
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logging.error("SpeechRecognition package not available. Speech-to-text functionality will be limited.")
    # Create a mock sr module with the necessary classes for the code to run
    class MockRecognizer:
        def adjust_for_ambient_noise(self, source):
            pass
        
        def record(self, source):
            return None
        
        def recognize_google(self, audio_data):
            return "This is a placeholder text since speech recognition is not available"
    
    class MockAudioFile:
        def __init__(self, filename):
            self.filename = filename
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
    
    class sr:
        @staticmethod
        def Recognizer():
            return MockRecognizer()
        
        @staticmethod
        def AudioFile(filename):
            return MockAudioFile(filename)
        
        class UnknownValueError(Exception):
            pass
        
        class RequestError(Exception):
            pass

logger = logging.getLogger(__name__)

def convert_speech_to_text(audio_file):
    """
    Convert speech in audio file to text using speech recognition.
    
    Args:
        audio_file: The audio file from the request.
        
    Returns:
        str: The recognized text from the audio.
    """
    input_filename = None
    output_filename = None
    
    try:
        if not SPEECH_RECOGNITION_AVAILABLE:
            logger.warning("SpeechRecognition not available. Using dummy text.")
            return "This is placeholder text since speech recognition is not available"
            
        recognizer = sr.Recognizer()
        
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_input:
            audio_file.save(temp_input.name)
            input_filename = temp_input.name
            logger.debug(f"Saved audio to temporary file: {input_filename}")
            
        # Create a temporary WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_output:
            output_filename = temp_output.name
        
        # Set default temp_filename to input_filename in case conversion fails
        temp_filename = input_filename
        
        # Convert audio to WAV format using ffmpeg if available
        try:
            logger.debug(f"Converting audio file to WAV format")
            # Try to convert using ffmpeg - if not available will go to except block
            cmd = ['ffmpeg', '-y', '-i', input_filename, '-ar', '16000', '-ac', '1', output_filename]
            logger.debug(f"Running command: {' '.join(cmd)}")
            
            # Use a shorter timeout to avoid hanging
            result = subprocess.run(cmd, check=True, capture_output=True, timeout=10)
            
            # Process was successful, use the output file
            temp_filename = output_filename
            logger.debug(f"Converted to WAV format successfully at {temp_filename}")
            
            # Check if the output file exists and has content
            if os.path.exists(temp_filename) and os.path.getsize(temp_filename) > 0:
                logger.debug(f"WAV file exists and has size: {os.path.getsize(temp_filename)} bytes")
            else:
                logger.error(f"WAV file doesn't exist or is empty: {temp_filename}")
                # Use original file instead of raising exception
                temp_filename = input_filename
                
        except Exception as e:
            logger.warning(f"Couldn't convert with ffmpeg: {str(e)}. Using direct file.")
            # temp_filename is already set to input_filename
            
        # Use the audio file as the source for recognition
        logger.debug(f"Starting speech recognition on file: {temp_filename}")
        with sr.AudioFile(temp_filename) as source:
            # Adjust for ambient noise and record the audio
            logger.debug("Adjusting for ambient noise")
            recognizer.adjust_for_ambient_noise(source)
            
            logger.debug("Recording audio data")
            audio_data = recognizer.record(source)
            
            # Use Google's speech recognition
            logger.debug("Sending to Google Speech Recognition")
            text = recognizer.recognize_google(audio_data)
            logger.debug(f"Recognized text: {text}")
            
            # Return the recognized text
            return text
            
    except sr.UnknownValueError:
        logger.error("Speech Recognition could not understand the audio")
        return None
    except sr.RequestError as e:
        logger.error(f"Could not request results from Speech Recognition service: {e}")
        return None
    except Exception as e:
        logger.error(f"Error in speech-to-text conversion: {str(e)}")
        # For debugging, return a message instead of None
        return f"I couldn't understand that. Error: {str(e)}"
    finally:
        # Clean up the temporary files
        try:
            if input_filename and os.path.exists(input_filename):
                os.unlink(input_filename)
                logger.debug(f"Removed temporary input file: {input_filename}")
            if output_filename and os.path.exists(output_filename):
                os.unlink(output_filename)
                logger.debug(f"Removed temporary output file: {output_filename}")
        except Exception as e:
            logger.warning(f"Error cleaning up temporary files: {str(e)}")
