
import os
import argparse
import time
import re
import sys
from collections import deque

from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from urllib import robotparser



def scrape(domain):
    try:

        # initialise the file name which is going to be used to list all unique URLs
        file_name =  domain.replace("https://", "").replace("http://", "").replace("://", "").replace("/", "")
        

        # a queue of URLs to be scraped
        forProcessingURLs = deque([domain])
        # a set of urls that we have already scraped
        final_URLs = set()
        # a set of domains inside the target website
        domain_URLs = set()

        # used an array for a sorted list to be printed at the end!
        unique_URLs = []
        unique_URLs.append(domain)

        robots_url = domain + "robots.txt"
        robot = robotparser.RobotFileParser()
        robot.set_url(robots_url)
        robot_readable = False
        
        try:
            robot.read()
            robot_readable = True
            print("robots.txt is found within the domain ", domain)
            print("Directives are going to be followed from the file robots.txt")
        except:
            # continue scraping without directives from robots.txt
            print("Error handling the Robots.txt")
            print("The crawler will continue scraping all URLs without directives")

        # process urls one by one until we exhaust the queue


        # For a quick test
        # counter = 0

        while forProcessingURLs:
            ## for a quick test uncomment the 3 lines below.
            # if (counter > 100 ):
            #     break
            # counter+=1


            # move next url from the queue to the set of processed urls
            url = forProcessingURLs.popleft()
            final_URLs.add(url)
            # get url's content

            if (not domain in url):
                print("Outside URL: ", url)
                continue

            if (robot_readable):
                if (not robot.can_fetch("*", url)):
                    print("Restricted URL: ", url)
                    continue

            if url not in unique_URLs:
                unique_URLs.append(url)


            print("Processing URL: ", url)
            try:
                # Respecting the requested server with a waiting time limit of half a second between each request!
                time.sleep(0.5)
                response = requests.get(url)
            except:
                # if we get error within the request, we continue through other URLs.
                # this could be improved by using some strategies to avoid recursive errors.
                continue
            
            # extract base URL to resolve relative URLs
            parts = urlsplit(url)
            base = "{0.netloc}".format(parts)
            strip_base = base.replace("www.", "")
            base_url = "{0.scheme}://{0.netloc}".format(parts)
            path = url[:url.rfind('/')+1] if '/' in parts.path else url

            # create a BeautifulSoup for the web page
            soup = BeautifulSoup(response.text, "lxml")



            # loop through all links within a given page
            for link in soup.find_all('a'):
                # get url from a given anchor tag
                a = link.attrs["href"] if "href" in link.attrs else ''

                if a.startswith('/'):
                    found_link = base_url + a
                    domain_URLs.add(found_link)
                elif strip_base in a:
                    domain_URLs.add(a)
                elif not a.startswith('http'):
                    found_link = path + a
                    domain_URLs.add(found_link)
                

            # check if found URLs are not being processed yet, or add them to the queue within forProcessingURLs.
            for i in domain_URLs:
                if not i in forProcessingURLs and not i in final_URLs:
                    forProcessingURLs.append(i)


        # End of the scraped and the start of printing the result!

        timestr = time.strftime("%Y%m%d-%H%M%S")
        file_name = file_name + "_" + timestr + ".txt"
        print("The final list of all unique URLs are printed to file: ", )
        try:
            with open(file_name, 'w') as f:
                for item in unique_URLs:
                    f.write("%s\n" % item)
        except:
            print("Error writing the list of unique URLs to file", file_name)
            sys.exit()

    except:
        sys.exit()



def main(argv):
    text = 'A tool to collect all unique URLs from a given domain!'
    parser = argparse.ArgumentParser(description=text)
    parser.add_argument('--domain', '-d', required=True,
                        help='Specify a domain. i.e. "https://www.octoberbooks.org"')
    
    parser.parse_args()
    args = parser.parse_args()
    domain_name = args.domain

    print("Domain to be scraped:", domain_name)
    scrape(domain_name)


if __name__ == "__main__":
    main(sys.argv[1:])