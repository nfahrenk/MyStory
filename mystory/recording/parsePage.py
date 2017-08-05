from bs4 import BeautifulSoup
from urlparse import urljoin

def processHtml(url, contents):
    # Remove all script tags and replace links with absolute links
    soup = BeautifulSoup(contents)
    for match in soup.findAll('script'):
        match.decompose()
    for tag in soup.findAll():
        if tag.get('href'):
            tag['href'] = urljoin('http://publy.nickfahrenkrog.me/', tag['href'])
        elif tag.get('src'):
            tag['src'] = urljoin('http://publy.nickfahrenkrog.me/', tag['src'])
    return str(soup)