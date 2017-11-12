# Need BeautifulSoup and urllib2 to crawl
import bs4
from bs4 import BeautifulSoup
import os 
import nltk
import sys

SCRAPE_DIRECTORY = os.getcwd() + "/raw_webpages"
OUTPUT_DIRECTORY = os.getcwd() + "/documents"

def writeChildren(soup, outfile):
    if type(soup) is bs4.element.NavigableString:
        outfile.write(soup + "\n")
    elif type(soup) is bs4.element.Comment:
        None
    else:
        for c in soup.children:
            writeChildren(c,outfile)

for filename in os.listdir(SCRAPE_DIRECTORY): 
    # Get scrape data
    scrape_file = open(SCRAPE_DIRECTORY + "/" + filename, 'r')
    soup = BeautifulSoup(scrape_file)
    outfile = open(OUTPUT_DIRECTORY + "/" + filename, 'w+')

    # Remove Javascript and CSS
    sections_to_remove = ["script", "style"]
    for d in soup.descendants:
        if d.name in sections_to_remove:
            d.extract()
    writeChildren(soup, outfile)