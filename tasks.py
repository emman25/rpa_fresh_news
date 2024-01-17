
from robocorp.tasks import task
from robocorp import workitems
import json

from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP
from RPA.Robocorp.Vault import Vault
from RPA.Tables import Tables
from RPA.FileSystem import FileSystem
from RPA.Robocorp.WorkItems import WorkItems
from RPA.Excel.Files import Files
from RPA.Browser.Selenium import WebElement, By
from RPA.FileSystem import FileSystem

from pathlib import Path
from datetime import datetime, timedelta
import os
import time
from datetime import datetime, timedelta
import calendar
import re
import logging
from typing import List

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


FILE_PATH = 'output/files/data.xlsx'
PICS_DIR = 'output/pics/'
SITE_URL = 'https://www.nytimes.com/'
HEADERS = ['Title', 'Date', 'Description', 'filename', 'Search', 'Paid']

class NewsSource:
    def __init__(self) -> None:
        self.browser = Selenium()
        self.excel_lib = Files()
        self.filesystem_lib = FileSystem()

        self.search_phrase: str = ''
        self.news_category: str = ''
        self.num_months: int = 0
        self.sort_news = ''
        self.news_type = ''
        self.retries = 3


    @classmethod
    def builder(cls) -> 'NewsSource':
        """Create a new instance of the class

        Returns:
            cls: An instance of a class
        """
        return cls()
    
    def build(self) -> 'NewsSource':
        """Build and return the current object

        Returns:
            self: The current object instance.
        """
        return self

    def with_search_phrase(self, search_phrase) -> 'NewsSource':
        """Set the search phrase for filtering news.

        Args:
            search_phrase (str): The search phrase to filter news.

        Returns:
            self: The instance with the updated search phrase.
        """
        self.search_phrase = search_phrase
        return self

    def with_news_category(self, news_category) -> 'NewsSource':
        """Set the news category for filtering news.

        Args:
            news_category (str): The news category to filter news.

        Returns:
            self: The instance with the updated news category.
        """
        self.news_category = news_category
        return self

    def with_num_months(self, num_months: int) -> 'NewsSource':
        """Set the number of months for date range filtering.

        Args:
            num_months (int): The number of months to filter news by date.

        Returns:
            self: The instance with the updated number of months.
        """
        self.num_months = num_months
        return self

    

    def open_site(self) -> None:
        """Opens the specified website and maximizes the browser window.

        Args:
            None

        Returns:
            None
        """
        self.browser.open_available_browser(SITE_URL)
        self.browser.maximize_browser_window

    def search_phrase_web(self) -> None:
        """Performs a search for the specified search phrase on the website.

        Args:
            None

        Returns:
            None
        """
        self.browser.wait_until_element_is_visible('css:#app > div:nth-child(4) > div.NYTAppHideMasthead.css-1r6wvpq.e1m0pzr40 > header > section.css-9kr9i3.e1m0pzr42 > div.css-qo6pn.ea180rp0 > div.css-10488qs > button > svg')
        self.browser.click_button('css:#app > div:nth-child(4) > div.NYTAppHideMasthead.css-1r6wvpq.e1m0pzr40 > header > section.css-9kr9i3.e1m0pzr42 > div.css-qo6pn.ea180rp0 > div.css-10488qs > button')
        self.browser.input_text('css:#search-input > form > div > input', self.search_phrase)
        self.browser.click_button('css:#search-input > form > button')
        self.browser.wait_until_element_is_visible('css=#site-content > div > div.css-1npexfx > div.css-nhmgdh > p')
        time.sleep(1)

    def select_news_category(self) -> None:
        """Selects the specified news category on the website.

        Args:
            None

        Returns:
            None
        """
        try:
            self.browser.click_button('css:#site-content > div > div.css-1npexfx > div.css-1az02az > div > div > div:nth-child(2) > div > div > button')
        
            self.browser.click_button_when_visible(locator=f"//label/input[contains(@value,'{self.news_category}')]")

            logger.info(f"Selected News Category: {self.news_category}")

        except Exception as e:
            self.browser.click_button_when_visible(locator=f"//label/input[contains(@value,'Any')]")

            logger.info(f"Failed to select category: {self.news_category}: {e}")

    
    def select_type(self) -> None:
        """Selects the type on the website.

        Args:
            None

        Returns:
            None
        """
        try:
        
            self.browser.click_button('css:#site-content > div > div.css-1npexfx > div.css-1az02az > div > div > div:nth-child(3) > div > div > button')
            
            self.browser.click_button_when_visible(locator=f"//label/input[contains(@value,'any')]")

            logger.info(f"Selected type: any")

        except Exception as e:
    
            logger.info(f"Failed to select type: any: {e}")

   
    def select_date_range(self) -> None:
        """Selects a date range for filtering news articles.

        This method calculates the start and end dates based on the provided
        number of months and applies the date range filter on the website.

        Args:
            None

        Returns:
            None
        """
        try:
            option = int(self.num_months)
            today = datetime.today()
            if option < 2:
                option = 0
            elif option > 3:
                option = 3-2

            end_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])
            start_date = (end_date - timedelta(days=option * 30)).replace(day=1)

            self.browser.click_button('css:#site-content > div > div.css-1npexfx > div.css-1az02az > div > div > div.css-wsup08 > div > div > button')
            
            self.browser.click_button('css:#site-content > div > div.css-1npexfx > div.css-1az02az > div > div > div.css-wsup08 > div > div > div > ul > li:nth-child(6) > button')
            
            self.browser.input_text('css:#startDate', start_date.strftime('%d/%m/%Y'))
            
            self.browser.input_text('css:#endDate', end_date.strftime('%d/%m/%Y'))

            logger.info(f"Successfully applied date range")

            return
        except Exception as e:

            logger.info(f"Failed to apply date range: {e}")

            return

    def contains_money(self, text: str) -> bool:
        """Checks if the given text contains mentions of money.

        Args:
            text (str): The text to be checked.

        Returns:
            bool: True if the text contains mentions of money, False otherwise.
    """
        money_pattern = r"\$\d+(\.\d{1,2})?|\d+\s(dollars|USD)"
        return bool(re.search(money_pattern, text))

    def count_search_phrase(self, title: str, description: str) -> int:
        """Counts the occurrences of a search phrase in the title and description.

        Args:
            title (str): The title of the news article.
            description (str): The description of the news article.

        Returns:
            int: The total count of the search phrase in the title and description.
        """
        title = str(title).lower()
        description = str(description).lower()
        search_phrase = str(self.search_phrase).lower()

        title_count = title.count(search_phrase)

        description_count = description.count(search_phrase)

        total_count = title_count + description_count

        return total_count    

    def replace_alpha_with_underscore(self, word) -> str:
        """Replace non-alphanumeric characters in a word with underscores.

        Args:
            word (str): The word to be processed.

        Returns:
            str: The word with non-alphanumeric characters replaced by underscores.
        """
        result = re.sub(r'[^a-zA-Z0-9]', '_', word)
        return result

    def news_items(self) -> list:
        """Retrieve news items from the website.

        Args:
            None

        Returns:
            List[dict]: A list of dictionaries containing news item data.
                Each dictionary includes 'date', 'title', 'description',
                'filename', 'url', 'count', and 'is_paid' attributes.
        """
        try:
            self.scroll_to_end()
            
            list_of_news: List[WebElement] = self.browser.find_elements("//li[@class='css-1l4w6pd']")


            logger.info(list_of_news)
            logger.info(len(list_of_news))

            
            list_of_data = []

            for i in list_of_news:
                date = i.find_element(value="css-17ubb9w", by=By.CLASS_NAME)
                title = i.find_element(value='css-2fgx4k', by=By.CLASS_NAME)
                description = i.find_element(value="css-16nhkrn",by=By.CLASS_NAME)
                image = i.find_element(value="css-rq4mmj", by=By.CLASS_NAME).get_attribute("src")
                
                filename = self.replace_alpha_with_underscore(f"{title.text}{date.text}")+".png"
                list_of_data.append({
                    'date': date.text,
                    'title': title.text,
                    'description': description.text,
                    'filename': filename,
                    'url': image,
                    'count': self.count_search_phrase(title.text, description.text),
                    'is_paid': self.contains_money(description.text)
                })

            logger.info("Fetched news items successfully")
                
            return list_of_data
        except Exception as e:
            logger.info(f"No fetched news items: {e}")

            return []

    def scroll_to_end(self):
        """Scroll to the bottom of the page and click a button if visible.

        This method continuously scrolls to the bottom of the page and clicks a button
        if it becomes visible. It does this in a loop until the button is no longer
        visible or an exception is raised.

        Returns:
            None
        """
        
        while True:
            try:
                self.browser.execute_javascript("window.scrollTo(0, document.body.scrollHeight);")
                self.browser.click_button_when_visible('css:#site-content > div > div:nth-child(2) > div.css-1t62hi8 > div > button')
                time.sleep(1)

            except:
                break
            
        time.sleep(3)


    def store_excel(self, data: dict) -> None:
        """Store data in an Excel file.

        Args:
            data (dict): The data to be stored in the Excel file.

        Returns:
            None
        """
        try:
            excel = Files()

            if not Path(FILE_PATH).is_file():
                logger.info("Create WorkBook with headers")
                excel.create_workbook(FILE_PATH)
                excel.create_worksheet(name='Data', header=HEADERS)
                excel.append_rows_to_worksheet([HEADERS], name="Data")
                excel.save_workbook()
            else:
                excel.open_workbook(FILE_PATH)
                logger.info("Opened workbook")
        
            excel.append_rows_to_worksheet([[data["title"], data["date"], data["description"], data["filename"], data['count'], data['is_paid']]], name="Data")


            excel.save_workbook()
            excel.close_workbook()

            logger.info(f"Wrote to excel: {FILE_PATH}")
        
        except Exception as e:
            logger.info(f"Failed to write to excel: {FILE_PATH}: {e}")


    def download_pics(self, url: str, name: str) -> None:
        """Download an image from a URL and save it with the given name.

    Args:
        url (str): The URL of the image to download.
        name (str): The name to be used when saving the downloaded image.
    """
        try:
            http = HTTP()
            http.download(url=url, target_file=f'{PICS_DIR}{name}', overwrite=True)

            logger.info(f"Downloaded image: {PICS_DIR}{name}")

            return
        except Exception as e:
            logger.info(f"Failed to download: {e}")

            return
        

    def create_directories(self):
        """Create necessary directories if they do not exist.

    This method creates directories 'output/pics' and 'output/files' if they
    do not already exist.

    Args:
        None

    Returns:
        None
    """
        fs = FileSystem()
        directories = ["output/pics", "output/files"]
        for directory in directories:
            if not fs.does_file_exist(directory):
                fs.create_directory(directory)
                logger.info(f"Directory {directory} created.")
            else:
                logger.info(f"Directory {directory} already exists.")

    def run_workflow(self):
        """Execute the workflow to collect news data and save it.

        This method executes the workflow which includes opening the site, searching for
        news, selecting a category, selecting a date range, fetching news items,
        creating directories, storing data in Excel, and downloading images.

        Args:
            None
        
        Returns:
            None
        """
        for attempt in range(self.retries):
            try:
                self.open_site()
                self.search_phrase_web()
                self.select_news_category()
                self.select_type()
                self.select_date_range()
                items = self.news_items()
                self.create_directories()

                for item in items:
                    self.store_excel(item)
                    self.download_pics(item['url'], item['filename'])

                logger.info("Completed the automation")
                break
            except Exception as e:
                logger.info(f"Error in attempt {attempt + 1}: {str(e)}")
                if attempt < self.retries - 1:
                    logger.info(f"Retrying in 1 minute...")
                    time.sleep(60)
                else:
                    logger.info("Max retries reached. Exiting.")
            

@task
def run_news_data_task() -> None:
    payload = {}
    
    try:
        raise_exception = True
        for item in workitems.inputs:
            payload = item.payload
            if(payload is not None):
                raise_exception = False
        
        if raise_exception:
            raise Exception("Load config")
        
        logger.info(f"Loaded payload from work item: {payload}")

    except Exception as e:
        with open('configuration.json', 'r') as config_file:
            payload = json.load(config_file)
            logger.info(f"Loaded payload from configuration.json: {payload}")

    newsSource = NewsSource.builder()\
    .with_search_phrase(payload['search_phrase'])\
    .with_news_category(payload['news_category'])\
    .with_num_months(payload['num_months'])\
    .build()

    newsSource.run_workflow()

