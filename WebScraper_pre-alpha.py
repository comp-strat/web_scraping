import csv

'Driver'
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

'Driver Exceptions'
from selenium.common.exceptions import *

'Parser'
from bs4 import BeautifulSoup
from bs4.element import Comment

driverPath = 'Driver/chromedriver'

jsLinks = []


class School:
    """Class that holds schools. Each school is comprised of an ID number, Name, Geographical Address and a url that goes to the schools hompage. The matcher is used to
    filer out links that go to places outside the schools main domain, like facebook or instagram. The links attribute is an array used to store all of the links on the homepage using
    the Links class"""

    def __init__(self, id, name, address, mainURL):
        self.id = id
        self.name = name
        self.address = address
        self.mainURL = mainURL
        self.links = []
        self.matcher = self.mainURL.split(".")[1]

    def gatherLinks(self) -> None:
        driver = webdriver.Chrome(executable_path=driverPath)
        driver.get(self.mainURL)
        elems = driver.find_elements_by_xpath("//a[@href]")
        for elem in elems:
            try:
                link = Link(elem, self.mainURL, self.matcher)
                self.links.append(link)
                print(elem.get_attribute("href") + " " + str(link))
            except ValueError:
                print(elem.get_attribute("href") + " was not added as it did not match the main url")
        driver.close()

    def clickLinks(self, filePath="") -> bool:
        for link in self.links:
            link.click()
        return True

    def __str__(self) -> str:
        s = ""
        s += "mainURL:" + self.mainURL + " "
        s += "Matcher:" + self.matcher + " "
        s += "links:" + str(self.links) + " "
        s += "ID:" + self.id + " "
        s += "Name:" + self.name + " "
        s += "Address:" + self.address + " "
        return s


class Link():
    def __init__(self, elem, mainURL, matcher):
        self.type = ""
        self.url = ""
        self.fallbackURL = ""
        self.text = ""
        self.linkText = ""
        linkURL = elem.get_attribute("href")
        if (linkURL.startswith("http") and linkURL.split(".")[1] == matcher):
            self.type = "html"
            self.url = elem.get_attribute("href")

        elif (linkURL.startswith("javascript")):
            self.type = "JavaScript"
            self.url = elem.get_attribute("href")
            self.fallbackURL = mainURL
            jsLinks.append(self)
        else:
            raise ValueError()
        self.linkText = elem.text

    def tag_visible(self, element) -> bool:
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def text_from_html(self, body) -> str:
        soup = BeautifulSoup(body, 'html.parser')
        texts = soup.findAll(text=True)
        visible_texts = filter(self.tag_visible, texts)
        return u" ".join(t.strip() for t in visible_texts)

    def gatherText(self, driver):
        try:
            'Fast way to get all text'
            self.text = driver.find_element_by_tag_name("body").text
        except NoSuchElementException:
            'Slower, but more reliable'
            self.text = self.text_from_html(driver.page_source)

    def click(self) -> bool:
        driver = webdriver.Chrome(driverPath)
        if self.type == "html":
            driver.get(self.url)
            self.gatherText(driver)
            driver.close()
            return True
        elif self.type == "JavaScript":
            driver.get(self.fallbackURL)
            try:
                driver.find_element_by_link_text(self.linkText).click()
                self.gatherText(driver)
            except (ElementNotVisibleException, ElementNotInteractableException, ElementNotSelectableException):
                link = driver.find_elements_by_link_text(self.linkText)
                move = ActionChains(driver).move_to_element(link)
                move.perform()
                link.scrollIntoView(True)
                driver.find_element_by_link_text(self.linkText).click()
                self.gatherText(driver)
        else:
            raise ValueError("ERROR: Link did not have a type of html or javascript")

    def __str__(self) -> str:
        s = ""
        s += "Link Type:" + self.type + " "
        s += "LinkURL:" + self.url + " "
        s += "FallbackURL(Only used for JS):" + self.fallbackURL + " "
        return s


def readCSV(filename) -> list:
    schools = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if reader.line_num != 1:
                schools.append(School(row[0], row[1], row[2], row[3]))
    return schools


schools = readCSV('micro-sample_Apr17_rev3.csv')



for school in schools:
    school.gatherLinks()
    school.clickLinks()
