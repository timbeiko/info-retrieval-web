# Does not obey robots.txt yet, will implement something similar to 
# https://stackoverflow.com/questions/33596722/how-does-obey-robots-txt-using-python-2-7

from bs4 import BeautifulSoup
import robotparser
import urlparse
import urllib2
import os 
import json
import io

AGENT_NAME = 'COMP479'
VISITED_PAGES = []
docID_to_URL = {}

STARTING_WEBPAGES = ["https://csu.qc.ca/content/student-groups-associations", 
                     "https://www.concordia.ca/artsci/students/associations.html", 
                     "http://www.cupfa.org", 
                     "http://cufa.net"]

NUMBER_OF_PAGES_TO_CRAWL = 100 # This is an upper bound, the crawler may stop before
CRAWLS_PER_START_PAGE = NUMBER_OF_PAGES_TO_CRAWL/len(STARTING_WEBPAGES)
RAW_WEBPAGE_OUTPUT_DIR = '/raw_webpages'
total_crawled_pages = 0 # Total for all pages

for webpage in STARTING_WEBPAGES:
    print "\nCrawling from: " + str(webpage) + "\n"
    
    pages_to_crawl = []
    pages_to_crawl.append(webpage)
    crawled_pages = 0 # Total for this start page 

    while crawled_pages <= CRAWLS_PER_START_PAGE and len(pages_to_crawl) > 0:
        url = pages_to_crawl.pop(0)
        url = url.encode('utf8')

        # Ensure we do not visit the same URLs multiple times 
        if url in VISITED_PAGES:
            print "Already visited " + str(url)
            continue 
        else:
            VISITED_PAGES.append(url)

        # Get root domain to check robots.txt 
        domain = "http://" + str(urlparse.urlparse(url).hostname) 
        parser = robotparser.RobotFileParser()
        parser.set_url(domain + "/robots.txt")

        # Try to get the robots.txt file, if none at this host, skip the website
        try: 
            parser.read()
        except:
            print "Cannot find a robots.txt file at " + str(domain) + "/robots.txt."
            continue

        # Only go to pages allowed by robots.txt
        if not parser.can_fetch(AGENT_NAME, url):            
            print "Cannot parse " + str(url)
            continue

        # Get content from webpage 
        try:
            content = urllib2.urlopen(url).read()
        except:            
            print "Cannot open contents of " + str(url)
            continue
        soup = BeautifulSoup(content)

        #saving the mapping of Document ID and web URL for this URL
        docID_to_URL[int(total_crawled_pages)] = str(url)

        # Output content to file 
        filename = RAW_WEBPAGE_OUTPUT_DIR + "/" + str(total_crawled_pages) + ".txt"
        raw_output = open(os.getcwd() + filename, 'w+')
        try: 
            raw_output.write(str(soup.prettify))
        except:             
            print "Cannot write contents of " + str(url)
            continue 

        # Get links from webpage 
        for link in soup.find_all('a'):
            l = link.get('href')
            if l == None:
                continue
            elif 'mailto' in l:
                continue
            elif len(l) == 0:
                continue;
            # Add domain to urls listed as "/something"
            elif l[0] == '/': 
                l = domain + l 
            pages_to_crawl.append(l)

        print "Parsing: " + str(url)

        crawled_pages += 1 
        total_crawled_pages += 1


json.dump(docID_to_URL, open('docID_URL_mapping.json', 'w'), indent=4)