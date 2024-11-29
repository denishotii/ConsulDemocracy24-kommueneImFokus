import requests
from bs4 import BeautifulSoup

urls = [
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    'https://mitmachen.siegburg.de/angebotslandkarte',
    'https://mitmachen.jena.de/projekts',
    'https://mitreden.ilzerland.bayern/projekts'
=======
    #'https://mitmachen.siegburg.de/angebotslandkarte',
    'https://mitmachen.jena.de/projekts',
    #'https://mitreden.ilzerland.bayern/projekts'
>>>>>>> 402f046 (Seperate py)
=======
    #'https://mitmachen.siegburg.de/angebotslandkarte',
    'https://mitmachen.jena.de/projekts',
    #'https://mitreden.ilzerland.bayern/projekts'
>>>>>>> 402f046 (Seperate py)
=======
    'https://mitmachen.siegburg.de/angebotslandkarte',
    'https://mitmachen.jena.de/projekts',
    'https://mitreden.ilzerland.bayern/projekts'
>>>>>>> ba7167e (Roughly ready scraping)
]

def def_42(urls):
    urls_and_data = {}

    for url in urls:
        response = requests.get(url)
        if response.status_code != 200:
            print("Failed to retrieve the webpage. Status code:", response.status_code)

        soup = BeautifulSoup(response.content, 'html.parser')

        link_and_content = scraper(soup, url)
        urls_and_data[url] = link_and_content

    return urls_and_data


def scraper(soup, url):
    if 'siegburg' in url:
        return siegburg_data(soup)
    elif 'jena' in url:
        return jena_data(soup)
    elif 'ilzerland' in url:
        return ilzerland_data(soup)
    
    return "No scraper defined for this URL"

def siegburg_data(soup):
    links = []

    a_tags = soup.find_all('a')

    for tag in a_tags:
        href = tag.get('href')
        
        if href and '/proposals/' in href and not 'new' in href:
            link = 'https://mitmachen.siegburg.de' + href
    
            if not link in links:
                links.append(link)
    
    link_and_content = content_scraper(soup, links, 'siegburg')

    return link_and_content


def jena_data(soup):
    links = []

    a_tags = soup.find_all('a',  class_='resource-item--title')

    for tag in a_tags:
        href = tag.get('href')
        
        if href:
            link = 'https://mitmachen.jena.de' + href
            
            if not link in links:
                links.append(link)
    
    link_and_content = content_scraper(soup, links, 'jena')

    return link_and_content

def ilzerland_data(soup):
    links = []

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    a_tags = soup.find_all('a',  class_='resource-item--title')
=======
    a_tags = soup.find_all('a',  class_='resources-list--inner')
>>>>>>> 402f046 (Seperate py)
=======
    a_tags = soup.find_all('a',  class_='resources-list--inner')
>>>>>>> 402f046 (Seperate py)
=======
    a_tags = soup.find_all('a',  class_='resource-item--title')
>>>>>>> ba7167e (Roughly ready scraping)

    for tag in a_tags:
        href = tag.get('href')
        
        if href:
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
            link = 'https://mitreden.ilzerland.bayern' + href
=======
            link = 'https://mitmachen.ilzerland.de' + href
            
>>>>>>> 402f046 (Seperate py)
=======
            link = 'https://mitmachen.ilzerland.de' + href
            
>>>>>>> 402f046 (Seperate py)
=======
            link = 'https://mitreden.ilzerland.bayern' + href
>>>>>>> ba7167e (Roughly ready scraping)
            if not link in links:
                links.append(link)
    
    link_and_content = content_scraper(soup, links, 'ilzerland')
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    
=======
    print(link_and_content)
>>>>>>> 402f046 (Seperate py)
=======
    print(link_and_content)
>>>>>>> 402f046 (Seperate py)
=======
    
>>>>>>> ba7167e (Roughly ready scraping)
    return link_and_content

def content_scraper(soup, links, identifier):
    link_and_data = {}

    for link in links:
        response = requests.get(link)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            match identifier:
                case 'jena':
                    title = soup.find_all('title')
                    content = soup.find_all('div', class_='flex-layout')

                    text_content = title[0].get_text(strip=True) + ': ' + content[0].get_text(strip=True)
                case 'siegburg':
                    divs = soup.find_all('div', class_='flex-layout')
                    content = divs[1]

                    text_content = content.get_text(strip=True)
                case 'ilzerland':
                    title = soup.find_all('title')
                    content = soup.find_all('div', class_='custom-page-content')
                    text_content = title[0].get_text(strip=True) + ': ' + content[0].get_text(strip=True)
                
                case _:
                    text_content = "Wrong identifier"

            link_and_data[link] = text_content

        else:
            message = "Failed to retrieve the webpage. Status code:", response.status_code
            link_and_data[link] = message
    
    return link_and_data