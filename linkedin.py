import logging
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters, ExperienceLevelFilters
from linkedin_scraper import Person, Company, actions
from selenium import webdriver

# Change root logger level (default is WARN)
#logging.basicConfig(level = logging.INFO)

jobs = []
driver = webdriver.Chrome("/usr/bin/chromedriver")
user = input("Username:")
passw = input("Password:")
actions.login(driver, user, passw)

def on_data(data: EventData):
    #get number of employees in the company
    print('[ON_DATA]', data.title, data.company, data.date, data.link, len(data.description))
    company_name = data.company.replace(" ", "-").lower()
    company = Company("https://www.linkedin.com/company/" + company_name + "/", driver=driver,
                      close_on_complete=False)
    jobs.append([data.title, data.company, data.link, str(company.company_size)])

def on_error(error):
    print('[ON_ERROR]', error)

def on_end():
    print('[ON_END]')
    print (jobs)

scraper = LinkedinScraper(
    chrome_executable_path='/usr/bin/chromedriver', # Custom Chrome executable path (e.g. /foo/bar/bin/chromedriver)
    chrome_options=None,  # Custom Chrome options here
    headless=True,  # Overrides headless mode only if chrome_options is None
    max_workers=1,  # How many threads will be spawned to run queries concurrently (one Chrome driver for each thread)
    slow_mo=1.3,  # Slow down the scraper to avoid 'Too many requests (429)' errors
)

# Add event listeners
scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)

queries = [
    #Query(
    #    options=QueryOptions(
    #        optimize=True,  # Blocks requests for resources like images and stylesheet
    #        limit=27  # Limit the number of jobs to scrape
    #    )
    #)
    Query(
        query='Machine Learning Engineer',
        options=QueryOptions(
            locations=['Bengaluru, Karnataka, India'],
            optimize=True,
            limit=5,
            filters=QueryFilters(
                #company_jobs_url='https://www.linkedin.com/jobs/search/?f_C=1441%2C17876832%2C791962%2C2374003%2C18950635%2C16140%2C10440912&geoId=92000000',  # Filter by companies
                relevance=RelevanceFilters.RELEVANT,
                #time=TimeFilters.MONTH,
                #type=[TypeFilters.FULL_TIME, TypeFilters.INTERNSHIP],
                experience=None,
            )
        )
    ),
]

scraper.run(queries)