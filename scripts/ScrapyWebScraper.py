from sys import platform
import csv
import os
import random
import string
import scrapy

# Driver
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

# Driver Exceptions
from selenium.common.exceptions import *

# Parser
from bs4 import BeautifulSoup
from bs4.element import Comment


# Display for headless mode
from pyvirtualdisplay import Display
# Only use this if running on a non linux machine
driverPath = '../Driver/chromedriver'

inline_tags = ["b", "big", "i", "small", "tt", "abbr", "acronym", "cite", "dfn",
               "em", "kbd", "strong", "samp", "var", "bdo", "map", "object", "q",
               "span", "sub", "sup"]


def prep_driver():
    if platform.startswith("linux"):
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        driver = webdriver.Chrome(chrome_options=options)
        return driver
    elif platform.startswith("darwin") or platform.startswith("win32"):
        driver = webdriver.Chrome(executable_path="../Driver/chromedriver")
        return driver


class LinkException(Exception):
    """Only called by link class. Add to switch statement as necessary"""

    def __init__(self, switch=-1):
        if switch == 0:
            self.value = "ERROR: Link type was not html or JavaScript"
        elif switch == 1:
            self.value = "ERROR: Link was Unclickable"
        elif switch == 2:
            self.value = "ERROR: Link is JavaScript based but an index value was not set"
        elif switch == -1:
            self.value = "No value was specified in LinkException Switch. " \
                         "Make sure you are properly calling this exception"

    def __str__(self) -> str:
        return str(self.value)


class Link(object):
    """Class that stores all of the information regarding a link. Each link has a type (either html of JavaScript),
    the href attribute (what the link redirects to), a fallback url, and an index value (used for JavaScript Links)"""

    def __init__(self, href_attribute, matcher="", calling_url="", index=-1):
        if calling_url == "" and index == -1:
            self.type = "html"
            self.hrefAttribute = href_attribute
            self.matcher = self.hrefAttribute.split(".")[1]
            self.text = ""
            return
        self.type = ""
        self.hrefAttribute = ""
        self.fallbackURL = calling_url
        self.matcher = matcher
        self.index = 0
        if (href_attribute.startswith("http") and href_attribute.split(".")[1] == matcher and len(href_attribute) > len(
                calling_url)):
            self.type = "html"
            self.hrefAttribute = href_attribute
        elif href_attribute.startswith("javascript"):
            self.type = "JavaScript"
            self.hrefAttribute = href_attribute
            self.index = index
        else:
            raise LinkException(0)
        self.name = ""
        self.gather_name(delimiter="-")

        self.text = ""

    @staticmethod
    def tag_visible(element) -> bool:
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def gather_text(self, driver) -> None:
        page_source_replaced = driver.page_source
        # Remove inline tags
        for it in inline_tags:
            page_source_replaced = page_source_replaced.replace("<" + it + ">", "")
            page_source_replaced = page_source_replaced.replace("</" + it + ">", "")

        # Create random string for tag delimiter
        random_string = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=75))
        soup = BeautifulSoup(page_source_replaced, 'lxml')

        # remove non-visible tags
        [s.extract() for s in soup(['style', 'script', 'head', 'title', 'meta', '[document]'])]
        visible_text = soup.getText(random_string).replace("\n", "")
        visible_text = visible_text.split(random_string)
        self.text = "\n".join(list(filter(lambda vt: vt.split() != [], visible_text)))

    def click_and_yield(self) -> list:
        driver = prep_driver()
        if self.type == "html":
            driver.get(self.hrefAttribute)
            self.gather_text(driver)
            new_links = self.get_new_links(driver, self.hrefAttribute)  # Yield new links
            driver.close()
            return new_links
        elif self.type == "JavaScript":
            if self.index is None:
                raise LinkException(2)
            driver.get(self.fallbackURL)
            new_links = self.get_new_links(driver, self.fallbackURL)  # Yield new links
            try:
                driver.find_elements_by_xpath("//a[@href]")[self.index].click_and_yield()
                self.gather_text(driver)
                return new_links
            except (WebDriverException, ElementNotVisibleException, ElementNotInteractableException,
                    ElementNotSelectableException):
                link = driver.find_elements_by_xpath("//a[@href]")[self.index]
                move = ActionChains(driver).move_to_element(link)
                move.perform()
                try:
                    link.click_and_yield()
                    self.gather_text(driver)
                    driver.close()
                    return new_links
                except (WebDriverException, ElementNotVisibleException, ElementNotInteractableException,
                        ElementNotSelectableException):
                    driver.close()
                    raise LinkException(1)
        else:
            raise LinkException(0)

    def gather_name(self, delimiter=" ") -> None:
        if self.type == "html":
            unfiltered_name = self.hrefAttribute[
                             len(self.hrefAttribute) - (len(self.hrefAttribute) - len(self.fallbackURL)):
                             len(self.hrefAttribute)]
            unfiltered_name = unfiltered_name.split("/")
            self.name = ""
            if len(unfiltered_name) != 1:
                for i in range(len(unfiltered_name)):
                    self.name += unfiltered_name[i] + delimiter
            else:
                self.name = unfiltered_name[0]
        elif self.type == "JavaScript":
            self.name = ""

    def write_file(self, filepath, counter):
        file_name = self.name
        if self.type == "html":
            file = open(str(filepath) + "/" + file_name + ".txt", "w")
        elif self.type == "JavaScript":
            file = open(str(filepath) + "/" + "JavaScript Link " + str(counter) + ".txt", "w")
        else:
            raise LinkException(0)
        file.write(self.text)
        file.close()

    def __str__(self) -> str:
        s = ""
        s += "Link Type:" + self.type + " "
        s += "hrefAttribute:" + self.hrefAttribute + " "
        s += "name:" + self.name + " "
        s += "FallbackURL(Only used for JS):" + self.fallbackURL + " "
        s += "Index (Only used for JS):" + str(self.index) + " "
        return s

    def get_new_links(self, driver, calling_url) -> list:
        elems = driver.find_elements_by_xpath("//a[@href]")
        new_requests = []
        for elem in elems:
            if not elem.get_attribute("href").lower().startswith(calling_url.lower()):
                continue
            try:
                link = Link(elem.get_attribute("href"), self.matcher, calling_url=calling_url, index=elems.index(elem))
                new_requests.append(link)
            except LinkException:
                print(elem.get_attribute("href") + " was not added as it did not match the main url")
        return new_requests


def check_path_exists(path):
    if os.path.exists(path):
        return True
    return False


if not check_path_exists("results"):
    os.mkdir("results")
if not check_path_exists("diagnostics"):
    os.mkdir("diagnostics")


def read_csv(filename) -> list:
    requests = []
    import codecs
    with codecs.open(filename, "r", encoding='utf-8', errors='ignore') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if reader.line_num != 1 and row[4] != "0":
                if row[4][:-1] == "/":
                    requests.append(row[4][:-1])
                else:
                    requests.append(row[4])
    return requests


class SchoolSpider(scrapy.Spider):
    name = "school_scraper"
    start_urls = [read_csv('../data/micro-sample13_coded.csv')[i] for i in range(1)]

    def parse(self, response):
        with open("seen_responses.txt", "a") as textfile:
            textfile.write(response.url + "\n")
        if "link" not in response.meta:
            link = Link(response.url)
        else:
            link = response.meta["link"]
        try:
            new_links = link.click_and_yield()
            for l in new_links:
                request = scrapy.Request(l.hrefAttribute, callback=self.parse)
                request.meta["link"] = l
                yield request
        except LinkException:
            print("Could not click link:" + str(link))
