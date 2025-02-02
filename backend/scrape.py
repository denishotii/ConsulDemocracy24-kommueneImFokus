
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data['url']
    options = data['options']
    result = {}

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    if options.get('title'):
        result['title'] = soup.title.string if soup.title else 'No title found'
    if options.get('images'):
        result['images'] = [img['src'] for img in soup.find_all('img') if 'src' in img.attrs]
    if options.get('links'):
        result['links'] = [a['href'] for a in soup.find_all('a') if 'href' in a.attrs]

    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5001)