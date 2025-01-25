import requests
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime
import configparser
from utils import log_message
import json
import feedparser

def extract_items_from_rss(rss_url):
    """Extract all items from the RSS feed"""
    # Parse the RSS feed
    feed = feedparser.parse(rss_url)
    
    # Check if the feed was successfully parsed
    if feed.bozo:
        print(f"Error parsing RSS feed: {feed.bozo_exception}")
        return []
    return feed.entries

def find_files_by_string(directory_path, search_string):
    """
    This function takes a directory path and a string as input,
    and returns a list of files in the folder containing the string in their name.
    """
    matching_files = []

    # Check if the directory exists
    if not os.path.isdir(directory_path):
        return matching_files

    # Iterate over all files in the folder
    for filename in os.listdir(directory_path):
        # Check if the string is in the file name
        if search_string in filename:
            matching_files.append(filename)

    return matching_files


def parser_date(date_str):
    """
    Parse a date in the format 'Friday 31 May 2024' into a datetime object without using an external library.
    """
    months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
              'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']

    # Extract the parts of the date
    parts = date_str.split()
    day = int(parts[3])
    month = parts[4]
    year = int(parts[5])

    # Find the index of the month
    month_index = months.index(month) + 1

    # Create the datetime object
    date_obj = datetime(year, month_index, day)

    return date_obj


def extract_content(url, save_path, force_update=False):
    """Extract and save content from the given URL."""
    #print(f"extract_content('{url}', '{save_path}')")

    slug = url.split('/')[-1]

    episode_data = {
        'url': url,
        'slug': slug,
        'mp3': []
    }

    output_path = None

    #check if ouput folder already exists
    matching_files = find_files_by_string(directory_path=save_path, search_string=slug)
    if len(matching_files) == 0 or force_update:
        # Load page
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # extract metadata
        scripts = soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                # Charger le contenu JSON du script
                json_data = json.loads(script.string)
                
                # Vérifier si le graph contient un "@type":"RadioEpisode"
                for graph in json_data.get("@graph", []):
                    graph_type = graph.get("@type")
                    episode_data[graph_type]=json_data
            except (json.JSONDecodeError, AttributeError) as e:
                continue

        #extract date
        current_date = parser_date(soup.find_all("p", {"class": "CoverEpisode-publicationInfo"})[0].getText())
        episode_data['date']=current_date.isoformat()

        # Extract content
        texts = []
        htmls = []
        for div in soup.find_all("div", {"class": "Expression-container"}):
            htmls.append(div)
            texts.append(div.getText())
    
        #Generate path and create output folder
        output_path = os.path.join(save_path,current_date.strftime('%Y-%m-%d') + "-" + slug)
        
        # Save content in record data
        episode_data['content_from_url'] = "\n".join(texts)
        
        # Extract mp3 links
        for script in soup.find_all("script", {"type": "application/ld+json"}):
            mp3_regex = r'https?://[^\s]+\.mp3'
            urls = re.findall(mp3_regex, script.getText())
            for u in urls:
                if u not in episode_data['mp3']:
                    episode_data['mp3'].append(u)
      
    else:
        #episode already scrapped
        output_path = os.path.join(save_path, matching_files[0])

    # create output folder if necessary
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    #Download mp3
    if len(episode_data['mp3'])>0:
        mp3_path = os.path.join(output_path, 'content.mp3')
        if not os.path.exists(mp3_path):
            download_mp3(episode_data['mp3'][0], mp3_path)
    
    #ensure data is saved
    data_file_path = os.path.join(output_path,"data.json")
    if not os.path.exists(data_file_path) or force_update:
        # Save file
        with open(data_file_path, "w", encoding="utf-8") as file:
            json.dump(episode_data, file, ensure_ascii=False, indent=4)


def download_mp3(url, save_path):
    """Download MP3 from the given URL."""
    try:
        # Perform a GET request to download the file
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # Write the downloaded data to a binary file
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:  # Filter empty chunks
                        file.write(chunk)
            log_message(f"Download complete: {save_path}")
        else:
            log_message(f"Download failed. Status code: {
                        response.status_code}")
    except Exception as e:
        log_message(f"An error occurred: {e}")


def scrap(podcast_rss_url, save_path,force_update=False):
    # Extract and process links
    log_message("Starting podcast extraction process...")
    
    all_items = extract_items_from_rss(podcast_rss_url)

    log_message(f"{len(all_items)} episodes found on the website {podcast_rss_url}")

    
    for item in all_items:
        url = item.get('link')
        if url != "https://www.radiofrance.fr/application-mobile-radio-france":
            try:
                extract_content(url=url, save_path=save_path,force_update=force_update)
            except Exception as e:
                log_message(f"An error occurred: {e} for {url}")
                raise e

    log_message("Podcast extraction process completed.")

def main(force_update=False):
    # Load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

    try:
        save_path = config['DEFAULT']['SavePath']
        podcast_rss_url = config['DEFAULT']['PodcastRssUrl']
        scrap(podcast_rss_url=podcast_rss_url, save_path=save_path,force_update=force_update)
    except KeyError as e:
        log_message(f"Configuration error: {e}")

def test():
    # Load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

    try:
        save_path = config['DEFAULT']['SavePath']
        extract_content(url='https://www.radiofrance.fr/franceculture/podcasts/le-pourquoi-du-comment-philo/comment-les-noms-parlent-ils-du-monde-3883953', save_path=save_path, force_update=True)
    except KeyError as e:
        log_message(f"Configuration error: {e}")

if __name__ == "__main__":
   main(force_update=False)
   #test()
