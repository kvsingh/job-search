# Scrape linkedin jobs for a job title and organize them based on
# glassdoor ratings. Dump data into a pickle file

from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters, ExperienceLevelFilters
import requests, pickle
from bs4 import BeautifulSoup
import re

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
        'Content-Type': 'text/html',
    }

glassdoor_not_found = 0
jobs = []

def get_glassdoor_url(company_name):
    url = "https://www.google.com/search?q=" + company_name + " glassdoor"
    html_text = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html_text, 'html.parser')

    try:
        foo = soup.find_all("a", attrs={"href": re.compile("https://www.glassdoor.co.in/Reviews/*")})
        foo = foo[0]['href'][7:]
        foo2 = foo.find("htm")
        foo = foo[:foo2 + 3]
        return foo
    except:
        return None

def get_rating(url):
    html_text = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html_text, 'html.parser')
    foo = soup.find_all("div", class_="v2__EIReviewsRatingsStylesV2__ratingNum v2__EIReviewsRatingsStylesV2__large")
    rating = float(foo[0].get_text())
    links = soup.find_all("button", attrs={"data-test" : re.compile("pagination-link-*")})
    return [rating, len(links)]

def on_data(data: EventData):
    print('[ON_DATA]', data.title, data.company, data.date, data.link, len(data.description))
    company_name = data.company
    try:
        url = get_glassdoor_url(company_name)
        rating, doo = get_rating(url)
    except:
        global glassdoor_not_found
        glassdoor_not_found += 1
        rating = 0.0
    jobs.append([data.title, data.company, data.link, rating])
    '''if (len(jobs)%10==0):
        pickle.dump(jobs, open('jobs-big.p', 'wb'))
        print (str(len(jobs)) + " jobs done")'''

def on_error(error):
    print('[ON_ERROR]', error)

def on_end():
    print('[ON_END]')
    #global glassdoor_not_found
    #print (glassdoor_not_found)
    pickle.dump(jobs, open('jobs-big.p', 'wb'))

scraper = LinkedinScraper(
    chrome_executable_path='/usr/bin/chromedriver', # Custom Chrome executable path (e.g. /foo/bar/bin/chromedriver)
    chrome_options=None,  # Custom Chrome options here
    headless=True,  # Overrides headless mode only if chrome_options is None
    max_workers=1,  # How many threads will be spawned to run queries concurrently (one Chrome driver for each thread)
    slow_mo=5.0,  # Slow down the scraper to avoid 'Too many requests (429)' errors
    #slow_mo=0.4,  # Slow down the scraper to avoid 'Too many requests (429)' errors
)

# Add event listeners
scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)

queries = [
    Query(
        query='Machine Learning Engineer',
        options=QueryOptions(
            locations=['Bengaluru, Karnataka, India'],
            optimize=True,
            limit=1000,
            filters=QueryFilters(
                #company_jobs_url='https://www.linkedin.com/jobs/search/?f_C=1441%2C17876832%2C791962%2C2374003%2C18950635%2C16140%2C10440912&geoId=92000000',  # Filter by companies
                relevance=RelevanceFilters.RELEVANT,
                time=TimeFilters.MONTH,
                #type=[TypeFilters.FULL_TIME, TypeFilters.INTERNSHIP],
                experience=None,
            )
        )
    ),
]

scraper.run(queries)
