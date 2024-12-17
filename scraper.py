import requests
from bs4 import BeautifulSoup
import re
import os
from datetime import datetime
import configparser
from utils import log_message


def extract_links(url):
    """Extract all links from a given URL and return them as a list."""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    links = []
    for div in soup.find_all("span", {"class": "CardTitle"}):
        for link in div.find_all('a', href=True):
            href = link['href']
            links.append(href)

    return links


def generate_page(page, podcast_url):
    """Generate the URL for a given page number using the podcast URL from the config."""
    url = f"{podcast_url}?p={page}"
    return url


def extract_all_links(current_page=1, max_pages=10, podcast_url=""):
    """Extract links from multiple pages starting from the given URL."""
    all_links = []
    pages_visited = 0

    while pages_visited < max_pages:
        current_url = generate_page(current_page, podcast_url)
        links = extract_links(current_url)
        for link in links:
            if link not in all_links:
                all_links.append(link)
        current_page += 1
        pages_visited += 1

    return all_links


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


def extract_content(url, save_path):
    """Extract and save content from the given URL."""
    slug = url.split('/')[-1]

    if len(find_files_by_string(directory_path=save_path, search_string=slug)) == 0:
        # Load page
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract date
        try:
            date = parser_date(soup.find_all(
                "p", {"class": "CoverEpisode-publicationInfo"})[0].getText())

            # Generate path
            path = os.path.join(
                save_path, date.strftime('%Y-%m-%d') + "-" + slug)

            # Extract content
            texts = []
            htmls = []
            for div in soup.find_all("div", {"class": "Expression-container"}):
                htmls.append(div)
                texts.append(div.getText())
        except Exception as e:
            log_message(f"An error occurred: {e} for {url}")
            raise e
        
        # Save content
        os.makedirs(path)
        filename = os.path.join(path, 'content.txt')
        with open(filename, 'w', encoding='utf-8') as file:
            file.write("\n".join(texts))

        # Optionally save HTML content
        '''
        filename = f"{path}/content.html"
        with open(filename, 'w', encoding='utf-8') as file:
            texts = []
            for html in htmls:
                texts.append(str(html)) 
            file.write("\n".join(texts))
        '''

        # Extract mp3 links
        mp3s = []
        for script in soup.find_all("script", {"type": "application/ld+json"}):
            mp3_regex = r'https?://[^\s]+\.mp3'
            urls = re.findall(mp3_regex, script.getText())
            for u in urls:
                if u not in mp3s:
                    mp3s.append(u)

        for mp3 in mp3s:
            mp3_path = os.path.join(path, 'content.mp3')
            download_mp3(mp3, mp3_path)


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


def scrap(podcast_url, save_path):
    # Extract and process links
    log_message("Starting podcast extraction process...")
    all_links = extract_all_links(
        current_page=1, max_pages=5, podcast_url=podcast_url)
    log_message(f"{len(all_links)} episodes found on the website.")

    for link in all_links:
        url = "https://www.radiofrance.fr" + link
        extract_content(url=url, save_path=save_path)

    log_message("Podcast extraction process completed.")


if __name__ == "__main__":
    # Load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

    try:
        save_path = config['DEFAULT']['SavePath']
        podcast_url = config['DEFAULT']['PodcastUrl']
        scrap(podcast_url=podcast_url, save_path=save_path)
    except KeyError as e:
        log_message(f"Configuration error: {e}")
