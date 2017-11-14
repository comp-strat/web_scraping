import csv
import datetime
import os

'Driver'
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

'Driver Exceptions'
from selenium.common.exceptions import *

'Parser'
from bs4 import BeautifulSoup
from bs4.element import Comment

'Statistics'

driverPath = 'Driver/chromedriver'


def readCSV(filename) -> list:
    schools = []
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if reader.line_num != 1:
                schools.append(School(row[0], row[1], row[2], row[3]))
    return schools


class School(object):
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
        self.filePath = "results/" + self.name
        self.totalNumberofLinks = 0
        self.linksClicked = 0

    def gatherLinks(self) -> None:
        driver = webdriver.Chrome(executable_path=driverPath)
        driver.get(self.mainURL)
        elems = driver.find_elements_by_xpath("//a[@href]")

        for elem in elems:
            try:
                link = Link(elem.get_attribute("href"), self.mainURL, self.matcher, elems.index(elem))
                self.links.append(link)
                print(str(link))
            except ValueError:
                print(elem.get_attribute("href") + " was not added as it did not match the main url")
        driver.close()
        self.totalNumberofLinks += len(self.links)

    def clickLinks(self):
        if not checkPathExists(self.filePath):
            os.makedirs(self.filePath)
        for link in self.links:
            try:
                link.click()
                self.linksClicked += 1
            except ValueError:
                print("Could not click link:" + str(link))
        htmlCount = 0
        scriptCount = 0
        for link in self.links:
            if link.type == "html":
                link.writeFile(self.filePath, htmlCount)
                htmlCount += 1
            elif link.type == "JavaScript" and link.text != "":
                link.writeFile(self.filePath, scriptCount)
                scriptCount += 1

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
    def __init__(self, switch=-1):
        if switch == 0:
            self.value = "ERROR: Link type was not html or JavaScript"
        elif switch == 1:
            self.value = "ERROR: Link was Unclickable"
        elif switch == 2:
            self.value = "ERROR: Link is JavaScript based but an index value was not set"
        elif switch == -1:
            self.value = "No value was specified in LinkException Switch. Make sure you are properly calling this expception"

    def __str__(self) -> str:
        return str(self.value)


class Link(object):
    """Class that stores all of the information regarding a link. Each link has a type (either html of JavaScript), the href attribute (what the link redirects
    to), a fallback url, and an index value (used for JavaScript Links)"""

    def __init__(self, hrefAttribute, callingURL, matcher, index):
        self.type = ""
        self.hrefAttribute = ""
        self.fallbackURL = callingURL
        self.index = None
        self.matcher = matcher
        self.index = 0
        if (hrefAttribute.startswith("http") and hrefAttribute.split(".")[1] == matcher and len(hrefAttribute) > len(
                callingURL)):
            self.type = "html"
            self.hrefAttribute = hrefAttribute
        elif (hrefAttribute.startswith("javascript")):
            self.type = "JavaScript"
            self.hrefAttribute = hrefAttribute
            self.index = index
        else:
            raise LinkException(0)
        self.gatherName(delimiter="-")

    def tag_visible(self, element) -> bool:
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def gatherText(self, driver) -> None:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        texts = soup.findAll(text=True)
        visible_texts = list(filter(self.tag_visible, texts))
        for i in range(len(visible_texts)):
            if "\n" in visible_texts[i]:
                visible_texts[i] = visible_texts[i].replace("\n", "")
        filtered_text = list(filter(lambda a: a != "", visible_texts))
        self.text = u" ".join(t.strip() for t in filtered_text)

    def click(self) -> bool:
        driver = webdriver.Chrome(driverPath)
        if self.type == "html":
            driver.get(self.hrefAttribute)
            self.gatherText(driver)
            driver.close()
            return True
        elif self.type == "JavaScript":
            if self.index is None:
                raise LinkException(2)
            driver.get(self.fallbackURL)
            try:
                driver.find_elements_by_xpath("//a[@href]")[self.index].click()
                self.gatherText(driver)
            except (WebDriverException, ElementNotVisibleException, ElementNotInteractableException,
                    ElementNotSelectableException):
                link = driver.find_elements_by_xpath("//a[@href]")[self.index]
                move = ActionChains(driver).move_to_element(link)
                move.perform()
                try:
                    link.click()
                    self.gatherText(driver)
                    driver.close()
                except (WebDriverException, ElementNotVisibleException, ElementNotInteractableException,
                        ElementNotSelectableException):
                    driver.close()
                    raise LinkException(1)
        else:
            raise LinkException(0)

    def gatherName(self, delimiter=" ") -> None:
        if self.type == "html":
            unfilteredName = self.hrefAttribute[
                             len(self.hrefAttribute) - (len(self.hrefAttribute) - len(self.fallbackURL)):
                             len(self.hrefAttribute)]
            unfilteredName = unfilteredName.split("/")
            self.name = ""
            if len(unfilteredName) != 1:
                for i in range(len(unfilteredName)):
                    self.name += unfilteredName[i] + delimiter
            else:
                self.name = unfilteredName[0]
        elif self.type == "JavaScript":
            self.name = ""

    def writeFile(self, filepath, counter):
        fileName = self.name
        if self.type == "html":
            file = open(str(filepath) + "/" + fileName + ".txt", "w")
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


def checkPathExists(path):
    if os.path.exists(path):
        return True
    return False


if not checkPathExists("results"):
    os.mkdir("results")
if not checkPathExists("diagnostics"):
    os.mkdir("diagnostics")

schools = readCSV('micro-sample_Apr17_rev3.csv')
numberofLinksClicked = 0
totalNumberOfLinks = 0
"Time doesn't really account for timezones now, many be an issue later"
now = datetime.datetime.now()
formattedTime = now.strftime("%Y-%m-%d %H:%M:%S")
diagnosticsFile = open(formattedTime + ".txt", "w")
diagnosticsFile.write("Program was run at " + formattedTime + "\n")
for school in schools:
    school.gatherLinks()
    school.clickLinks()
    totalNumberOfLinks += school.totalNumberofLinks
    numberofLinksClicked += school.linksClicked
    diagnosticsFile.write(
        "School " + str(school.name) + " had " + str(school.totalNumberofLinks) + " links and " + str(school.linksClicked) +
        " were clicked which is " + str(school.linksClicked / school.totalNumberofLinks) + "%\n")
diagnosticsFile.write("Total number of links:"+ str(totalNumberOfLinks) +"\n")
diagnosticsFile.write("Number of Links Clicked:" + str(numberofLinksClicked) +"\n")
diagnosticsFile.write("% of links clicked:" + str(numberofLinksClicked/totalNumberOfLinks) +"\n")
diagnosticsFile.close()