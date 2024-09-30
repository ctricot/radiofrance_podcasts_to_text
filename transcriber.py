import requests
import os
import configparser
import time

def audio_transcription(filepath: str, gladia_key: str):
    # Split the filename and extension to create the transcription file path
    filename, file_ext = os.path.splitext(filepath)
    transcription_filepath = f"{filepath}.txt"

    # Check if the transcription file already exists
    if os.path.exists(transcription_filepath):
        print(f"Transcription file already exists for {transcription_filepath}, skipping transcription.")
        return  # Exit the function if the .txt file already exists

    # If the file doesn't exist, proceed with transcription
    headers = {'x-gladia-key': f'{gladia_key}'}

    with open(filepath, 'rb') as audio:
        # Prepare data for the API request
        files = {
            # Specify audio file type
            'audio': (filename, audio, f'audio/{file_ext[1:]}'),
            'toggle_diarization': (None, True),  # Toggle diarization option
            'diarization_max_speakers': (None, 2),  # Set the max number of speakers for diarization
            'output_format': (None, 'txt')  # Specify output format as text
        }

        print(f'Sending request to Gladia API for {filepath}')

        while True:
            try:
                # Make a POST request to Gladia API
                response = requests.post(
                    'https://api.gladia.io/audio/text/audio-transcription/', headers=headers, files=files)

                if response.status_code == 200:
                    # If the request is successful, parse the JSON response
                    response = response.json()

                    # Extract the transcription from the response
                    prediction = response['prediction']

                    # Write the transcription to a text file in the same directory as the MP3
                    with open(transcription_filepath, 'w') as f:
                        f.write(prediction)

                    print(f"Transcription saved at {transcription_filepath}")
                    return response

                elif response.status_code == 429:
                    # Handle the "Too Many Requests" error by waiting 60 minutes
                    print("Received 429 Too Many Requests error. Waiting for 60 minutes before retrying...")
                    time.sleep(60 * 60)  # Wait for 60 minutes before retrying

                else:
                    # If the request fails with another status code, print the error details
                    print(f"Request failed for {filepath}. Error: {response.status_code}")
                    print(f"Response content: {response.text}")
                    return response.json()

            except requests.exceptions.RequestException as e:
                # Handle any request exceptions
                print(f"An error occurred: {e}")
                return None

def transcribe_all_mp3_in_directory(directory: str, gladia_key: str):
    # Walk through the directory and all subdirectories
    for root, dirs, files in os.walk(directory):
        for file in files:
            # Check if the file is an MP3
            if file.lower().endswith('.mp3'):
                filepath = os.path.join(root, file)
                # Call the transcription function for each MP3 file
                audio_transcription(filepath=filepath, gladia_key=gladia_key)

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')
save_path = config['DEFAULT']['SavePath']
gladia_key = config['DEFAULT']['GladiaKey']

# Start transcribing all MP3 files in the folder
transcribe_all_mp3_in_directory(directory=save_path, gladia_key=gladia_key)