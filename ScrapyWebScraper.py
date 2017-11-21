import csv
# import datetime
import os
import random
import string

import scrapy

# Parser
from bs4 import BeautifulSoup
from bs4.element import Comment

# Driver
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

# Driver Exceptions
from selenium.common.exceptions import *

# Display for headless mode
from pyvirtualdisplay import Display

driverPath = 'Driver/chromedriver'

inline_tags = ["b", "big", "i", "small", "tt", "abbr", "acronym", "cite", "dfn",
               "em", "kbd", "strong", "samp", "var", "bdo", "map", "object", "q",
               "span", "sub", "sup", "li"]


def read_csv(filename) -> list:
    schools = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        i = 0
        for row in reader:
            if reader.line_num != 1:
                schools.append(School(row[0], row[1], row[2], row[4]))
                i += 1
                if i == 2:
                    break
    return schools


def prep_driver():
    display = Display(visible=0, size=(1920, 1080))
    display.start()
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    driver = webdriver.Chrome(chrome_options=options)
    return driver


class School(object):
    """Class that holds schools. Each school is comprised of an ID number, Name, Geographical Address and a url that
    goes to the schools hompage. The matcher is used to filer out links that go to places outside the schools main
    domain, like facebook or instagram. The links attribute is an array used to store all of the links on the homepage
    using the Links class"""

    def __init__(self, school_id, name, address, main_url):
        self.id = school_id
        self.name = name
        self.address = address
        self.mainURL = main_url
        self.links = []
        self.matcher = self.mainURL.split(".")[1]
        self.filePath = "results/" + self.name
        self.totalNumberofLinks = 0
        self.htmlLinks = 0
        self.htmlLinksClicked = 0
        self.scriptLinks = 0
        self.scriptLinksClicked = 0
        self.linksClicked = 0

    def gather_links(self) -> None:
        driver = prep_driver()
        driver.get(self.mainURL)
        elems = driver.find_elements_by_xpath("//a[@href]")

        for elem in elems:
            try:
                link = Link(elem.get_attribute("href"), self.mainURL, self.matcher, elems.index(elem))
                self.links.append(link)
                print(str(link))
            except LinkException:
                print(elem.get_attribute("href") + " was not added as it did not match the main url")
        driver.close()
        self.totalNumberofLinks += len(self.links)

    def click_links(self):
        if not check_path_exists(self.filePath):
            os.makedirs(self.filePath)
        for link in self.links:
            try:
                if link.type == "html":
                    self.htmlLinks += 1
                elif link.type == "JavaScript":
                    self.scriptLinks += 1
                link.click()
                self.linksClicked += 1
                if link.type == "html":
                    self.htmlLinksClicked += 1
                elif link.type == "JavaScript":
                    self.scriptLinksClicked += 1
            except LinkException:
                print("Could not click link:" + str(link))
        script_count = 0
        for link in self.links:
            if link.type == "html":
                link.write_file(self.filePath, 0)
            elif link.type == "JavaScript" and link.text != "":
                link.write_file(self.filePath, script_count)
                script_count += 1

    def __str__(self) -> str:
        s = ""
        s += "mainURL:" + self.mainURL + " "
        s += "Matcher:" + self.matcher + " "
        s += "links:" + str(self.links) + " "
        s += "ID:" + self.id + " "
        s += "Name:" + self.name + " "
        s += "Address:" + self.address + " "
        return s


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
    the href attribute (what the link redirects
    to), a fallback url, and an index value (used for JavaScript Links)"""

    def __init__(self, href_attribute, calling_url, matcher, index):
        self.type = ""
        self.hrefAttribute = ""
        self.fallbackURL = calling_url
        self.index = None
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
        self.gather_name(delimiter="-")
        self.text = ""
        self.name = ""

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
            page_source_replaced = page_source_replaced.replace("<" + it + ">", " ")
            page_source_replaced = page_source_replaced.replace("</" + it + ">", " ")

        # Create random string for tag delimiter
        random_string = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=75))
        soup = BeautifulSoup(page_source_replaced, 'lxml')

        # remove non-visible tags
        [s.extract() for s in soup(['style', 'script', 'head', 'title', 'meta', '[document]'])]
        visible_text = soup.getText(random_string).replace("\n", "")
        visible_text = visible_text.split(random_string)
        self.text = "\n".join(list(filter(lambda vt: vt.split() != [], visible_text)))

    def click(self) -> bool:
        driver = prep_driver()
        if self.type == "html":
            driver.get(self.hrefAttribute)
            self.gather_text(driver)
            driver.close()
            return True
        elif self.type == "JavaScript":
            if self.index is None:
                raise LinkException(2)
            driver.get(self.fallbackURL)
            try:
                driver.find_elements_by_xpath("//a[@href]")[self.index].click()
                self.gather_text(driver)
            except (WebDriverException, ElementNotVisibleException, ElementNotInteractableException,
                    ElementNotSelectableException):
                link = driver.find_elements_by_xpath("//a[@href]")[self.index]
                move = ActionChains(driver).move_to_element(link)
                move.perform()
                try:
                    link.click()
                    self.gather_text(driver)
                    driver.close()
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


def tag_visible(element) -> bool:
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def check_path_exists(path):
    if os.path.exists(path):
        return True
    return False


if not check_path_exists("results"):
    os.mkdir("results")
if not check_path_exists("diagnostics"):
    os.mkdir("diagnostics")


def gather_text(driver):
    page_source_replaced = driver.page_source
    # Remove inline tags
    for it in inline_tags:
        page_source_replaced = page_source_replaced.replace("<" + it + ">", "")
        page_source_replaced = page_source_replaced.replace("</" + it + ">", "")

    # Create random string for tag delimiter
    random_string = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=75))
    soup = BeautifulSoup(page_source_replaced, 'lxml')
    [s.extract() for s in soup(['style', 'script', 'head', 'title', 'meta', '[document]'])]  # remove non-visible tags
    visible_text = soup.getText(random_string).replace("\n", "")
    visible_text = visible_text.split(random_string)
    return "\n".join(list(filter(lambda vt: vt.split() != [], visible_text)))


class SchoolSpider(scrapy.Spider):
    name = "school_scraper"
    schools = read_csv('micro-sample13_coded.csv')
    start_urls = [schools[i].mainURL for i in range(10)]

    def __init__(self):
        scrapy.Spider.__init__(self)  # lol I doubt this is necessary, PyCharm
        self.seen = set()
        schools = read_csv('micro-sample13_coded.csv')
        # for school in schools:
        #     school.gather_links()
        #     school.click_links()
        self.mainURL = schools[0].mainURL
        if self.mainURL[-1] != "/":
            self.mainURL[-1] += "/"
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.options.add_argument('windows-size=1200x600')
        self.driver = None

    def parse(self, response):
        self.driver = prep_driver()
        self.driver.get(response.url)
        
        # Stuff to get name for results file
        file_name = response.url
        if file_name[-1] != "/":
            file_name += "/"
        if file_name == self.mainURL:
            file_name = "home"
        else:
            file_name = file_name.replace("/", "_")
            file_name = file_name[len(self.mainURL):-1]

        # Write results file
        file = open("test_scrapy_results/" + file_name + ".txt", "w")
        file_text = gather_text(self.driver)
        if len(file_text) > 0:
            file.write(file_text)
        file.close()

        # Get new links from current page
        elems = self.driver.find_elements_by_xpath("//a[@href]")
        new_links = []
        for elem in elems:
            if elem.get_attribute("href").lower().startswith(self.mainURL.lower()):
                new_links.append(elem.get_attribute("href"))
        self.driver.close()

        # Make new scrapy requests to parse the new links
        for elem in new_links:
            try:
                if elem not in self.seen:
                    self.seen.add(elem)
                    yield scrapy.Request(elem, callback=self.parse)
            except LinkException:
                print(elem + " was not added as it did not match the main url")
