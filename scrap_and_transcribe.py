from scraper import scrap
from transcriber import transcribe
import configparser
from utils import log_message


def main():
    # Load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

    try:
        save_path = config['DEFAULT']['SavePath']
        podcast_url = config['DEFAULT']['PodcastUrl']
        gladia_key = config['DEFAULT']['GladiaKey']
        scrap(podcast_url=podcast_url, save_path=save_path)
        transcribe(save_path=save_path, gladia_key=gladia_key)
    except KeyError as e:
        log_message(f"Configuration error: {e}")

if __name__ == "__main__":
    main()