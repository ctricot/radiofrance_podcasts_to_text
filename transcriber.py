import requests
import os
import configparser

def audio_transcription(filepath: str, gladia_key: str):
    # Split the filename and extension to create the transcription file path
    filename, file_ext = os.path.splitext(filepath)
    transcription_filepath = f"{filepath}.txt"

    # Vérifier si le fichier de transcription existe déjà
    if os.path.exists(transcription_filepath):
        print(f"Transcription file already exists for {transcription_filepath}, skipping transcription.")
        return  # Quitter la fonction si le fichier .txt existe déjà

    # Si le fichier n'existe pas, continuer avec la transcription
    headers = {'x-gladia-key': f'{gladia_key}'}

    with open(filepath, 'rb') as audio:
        # Prepare data for API request
        files = {
            # Specify audio file type
            'audio': (filename, audio, f'audio/{file_ext[1:]}'),
            'toggle_diarization': (None, True),  # Toggle diarization option
            # Set the maximum number of speakers for diarization
            'diarization_max_speakers': (None, 2),
            'output_format': (None, 'txt')  # Specify output format as text
        }

        print(f'Sending request to Gladia API for {filepath}')

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

        else:
            print(f"Request failed for {filepath}. Error: {response.status_code}")
            return response.json()


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


# Lancer la transcription de tous les fichiers MP3 du dossier
transcribe_all_mp3_in_directory(directory=save_path, gladia_key=gladia_key)