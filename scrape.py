# Does not obey robots.txt yet, will implement something similar to 
# https://stackoverflow.com/questions/33596722/how-does-obey-robots-txt-using-python-2-7

from bs4 import BeautifulSoup
import urllib2
import os 

STARTING_WEBPAGES = ["https://csu.qc.ca/content/student-groups-associations", 
                     "https://www.concordia.ca/artsci/students/associations.html", 
                     "http://www.cupfa.org", 
                     "http://cufa.net"]
NUMBER_OF_PAGES_TO_CRAWL = 100 
CRAWLS_PER_START_PAGE = NUMBER_OF_PAGES_TO_CRAWL/len(STARTING_WEBPAGES)
RAW_WEBPAGE_OUTPUT_DIR = '/raw_webpages'
total_crawled_pages = 0 # Total for all pages

for webpage in STARTING_WEBPAGES:
    print "Crawling from: " + str(webpage)
    pages_to_crawl = []
    pages_to_crawl.append(webpage)
    crawled_pages = 0 # Total for this start page 

    while crawled_pages <= CRAWLS_PER_START_PAGE and len(pages_to_crawl) > 0:
        url = pages_to_crawl.pop(0)
        # Get content from webpage 
        try:
            content = urllib2.urlopen(url).read()
        except:
            continue
        soup = BeautifulSoup(content)

        # Output content to file 
        filename = RAW_WEBPAGE_OUTPUT_DIR + "/" + str(total_crawled_pages) + ".txt"
        raw_output = open(os.getcwd() + filename, 'w+')
        raw_output.write(str(soup.prettify))

        # Get links from webpage 
        for link in soup.find_all('a'):
            l = link.get('href')
            if l == None:
                continue
            elif 'mailto' in l:
                continue
            elif len(l) == 0:
                continue;
            elif l[0] == '/':
                l = url + l 
            pages_to_crawl.append(l)
        crawled_pages += 1 
        total_crawled_pages += 1

