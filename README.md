# Podcast Scraper

This Python script scrapes and downloads podcast episodes from the France Culture series like "Le Pourquoi du Comment : Philo". It retrieves all the episode links from multiple pages, extracts their content (text and MP3), and saves them locally.

## Features

- Extracts podcast episode links from multiple pages
- Downloads podcast MP3 files
- Saves the podcast text content and metadata
- Configurable `save_path` and `podcast_url` via `config.ini`

## Requirements

You can install the necessary dependencies via the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### Dependencies

- `requests` - for making HTTP requests
- `beautifulsoup4` - for parsing HTML content
- `lxml` - used as a backend parser for BeautifulSoup

## Usage

### 1. Clone the repository
Clone the repository to your local machine:
```bash
git clone https://github.com/yourusername/podcast-scraper.git
cd radiofrance_podcasts_to_text
```

### 2. Install dependencies
Install the required Python libraries:
```bash
pip install -r requirements.txt
```

### 3. Edit the `config.ini` file
Update the `config.ini` file to configure the save location and podcast URL:

```ini
[DEFAULT]
SavePath = /path/to/your/podcasts
PodcastUrl = https://www.radiofrance.fr/franceculture/podcasts/le-pourquoi-du-comment-philo
```

- **SavePath**: The directory where you want to save the downloaded podcasts.
- **PodcastUrl**: The base URL of the podcast series.

### 4. Run the script
Execute the scraper to download the episodes and their content:
```bash
python scraper.py
```

The script will download the podcasts and save them in the directory you specified in the `config.ini` file.

## Example Output Structure

After running the script, the folder structure will look something like this:

```
/path/to/your/podcasts/
    ├── 2024-09-22-episode-1-slug/
    │   ├── content.txt
    │   ├── content.mp3
    ├── 2024-09-23-episode-2-slug/
    │   ├── content.txt
    │   ├── content.mp3
    └── 2024-09-24-episode-3-slug/
        ├── content.txt
        ├── content.mp3
```

- **content.txt**: Contains the extracted text description of the episode.
- **content.mp3**: Contains the downloaded podcast episode audio.