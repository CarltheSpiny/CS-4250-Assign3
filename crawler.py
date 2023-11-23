from bs4 import BeautifulSoup
from urllib.request import urlopen
from queue import Queue
from pymongo import MongoClient

target_url = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"
alt_target_url = '/sci/computer-science/faculty-and-staff/permanent-faculty.shtml'
start_url = "https://www.cpp.edu/sci/computer-science/"

class Frontier:
    def __init__(self):
        self.url_queue = Queue()
        self.visited_urls = set()

    def add_url(self, url):
        if url not in self.visited_urls:  # If url is not in the visited urls
            #print("Added URL to frontier(queue): " + url)
            self.url_queue.put(url)  # put the url in the url_queue
            # self.visited_urls.add(url) # Add this url into the queue too

    def next_url(self):
        potential_url = self.url_queue.get()
        while potential_url in self.visited_urls:  # while the next url is already in visited urls
            print("the next url has already been visited: ", potential_url)
            potential_url = self.url_queue.get()
        return potential_url

    def done(self):
        return self.url_queue.empty()

    def clear(self):
        self.url_queue.queue.clear()


def connectDataBase():
    DB_NAME = "web_crawler_db"
    DB_HOST = "localhost"
    DB_PORT = 21017
    try:
        client = MongoClient("mongodb://localhost:27017")
        db = client[DB_NAME]

        return db

    except:
        print ("Could not connect to the database")

def storePage(url, content, collection):
    bs = BeautifulSoup(content, "html.parser")
    page = {
        "url": url,
        "content": bs.prettify()
    }
    collection.insert_one(page)
    print("Page stored in collection")

def urlFixerUpper(url):
    domain = "https://www.cpp.edu"
    if (not domain in url):
        return domain + url
    else:
        return url


# Gets a URL and returns the html content. Best used with beautiful soup
def retrieveURL(url):
    try:
        response = urlopen(url)
        #print("html retrieved")
        return response.read()
    except Exception as e:
        print("Error getting url: " + e)
    return


# Checks if the url passed is target url. Considers relative addresses
def isTargetURL(html):
    target_header = 'Permanent Faculty'
    target_bs = BeautifulSoup(html, "html.parser")
    html_data = target_bs.find_all('h1', {'class': 'cpp-h1'})
    for element in html_data:
        for item in element:
            if target_header in item.text:
                return True

    return False


# parse the html data and return all links inside
def parse(html, current_frontier):
    print("parsing html for links")
    parsed_bs = BeautifulSoup(html, "html.parser")
    links = []
    for link in parsed_bs.find_all('a'):
        links.append(link.get('href'))
    #print("List of Unfixed Links", links)
    #print("Will parse through this many links", len(links))

    count = 0
    for index, new_link in enumerate(links):
        if (count >= len(links)):
            #print("reached count of links in list")
            return links
        else:
            count += 1
            adjusted_url = urlFixerUpper(new_link)
            if adjusted_url not in current_frontier.visited_urls:
                # print("Removing unadjusted link: ", new_link)
                links.pop(index)

                links.insert(index, adjusted_url)
                # print("added new link into queue: " + adjusted_url)

    #print("List of fixed Links: ", links)
    return links


def getHref(html):
    for link in html:
        return link.get('href')


def main():
    frontier = Frontier();
    frontier.add_url(start_url)
    db = connectDataBase()
    db_collection = db["crawled_pages"]
    while not frontier.done():
        current_url = frontier.next_url()
        print("Crawling this url: ", current_url)
        current_html = retrieveURL(current_url)

        if isTargetURL(current_html):
            storePage(current_url, current_html, db_collection)
            print('found url')
            frontier.clear()

        else:
            frontier.visited_urls.add(current_url)
            #print("added " + current_url + " to the visited urls")
            for url in parse(current_html, frontier):
                frontier.add_url(url)
            print("Finished processing the url")




if __name__ == '__main__':
    main()
