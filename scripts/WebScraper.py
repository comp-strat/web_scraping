import csv
import datetime
import os
from sys import platform

'Driver'
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

'Driver Exceptions'
from selenium.common.exceptions import *

'Parser'
from bs4 import BeautifulSoup
from bs4.element import Comment

"Display for headless mode"
from pyvirtualdisplay import Display

"Only use this if running on a non linux machine"
driverPath = 'Driver/chromedriver'

inline_tags = ["b", "big", "i", "small", "tt", "abbr", "acronym", "cite", "dfn",
               "em", "kbd", "strong", "samp", "var", "bdo", "map", "object", "q",
               "span", "sub", "sup"]


def readCSV(filename) -> list:
    schools = []
    with open(filename, newline='', encoding="Latin-1") as csvFile:
        reader = csv.reader(csvFile, delimiter=',')
        for row in reader:
            try:
                if reader.line_num != 1:
                    schools.append(School(row[0], row[1], row[2], row[4]))
            except ValueError:
                print("ERROR: School " + str(row[1]) + " was not scraped as it did not have a URL")
    return schools


def prepDriver():
    if platform.startswith("linux"):
        display = Display(visible=0, size=(1920, 1080))
        display.start()
        chromeOptions = webdriver.ChromeOptions()
        chromeOptions.add_argument('headless')
        chromeOptions.add_argument('window-size=1920x1080')
        chromeOptions.add_argument('--no-sandbox')
        driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=chromeOptions)
        return driver
    elif platform.startswith("darwin") or platform.startswith("win32"):
        driver = webdriver.Chrome(executable_path="Driver/chromedriver")
        return driver


class School(object):
    """Class that holds schools. Each school is comprised of an ID number, Name, Geographical Address and a url that goes to the schools hompage. The matcher is used to
    filer out links that go to places outside the schools main domain, like facebook or instagram. The links attribute is an array used to store all of the links on the homepage using
    the Links class"""

    def __init__(self, id, name, address, mainURL):
        if mainURL == str(0):
            raise ValueError("ERROR: URL cannot be 0")
        self.id = id
        self.name = name
        self.address = address
        self.mainURL = mainURL
        self.links = []
        self.matcher = self.mainURL.split(".")[1]
        self.filePath = "results/" + self.name
        self.totalNumberofLinks = 0
        self.htmlLinks = 0
        self.htmlLinksClicked = 0
        self.scriptLinks = 0
        self.scriptLinksClicked = 0
        self.linksClicked = 0

    def gatherLinks(self) -> None:
        driver = prepDriver()
        driver.get(self.mainURL)
        elems = driver.find_elements_by_xpath("//a[@href]")
        for elem in elems:
            try:
                link = Link(elem.get_attribute("href"), self.mainURL, self.matcher, elems.index(elem))
                self.links.append(link)
                print(str(link))
            except LinkException:
                print(elem.get_attribute(
                    "href") + " was not added as it did not match the main url or was not longer than main url")
        driver.close()
        self.totalNumberofLinks = len(self.links)

    def clickLinks(self):
        if not checkPathExists(self.filePath):
            os.makedirs(self.filePath)
        counter = 1
        for link in self.links:
            try:
                if link.type == "html":
                    self.htmlLinks += 1
                elif link.type == "JavaScript":
                    self.scriptLinks += 1
                print("Clicking Link " + str(counter) + " out of " + str(self.totalNumberofLinks))
                link.click()
                counter += 1
                self.linksClicked += 1
                if link.type == "html":
                    self.htmlLinksClicked += 1
                elif link.type == "JavaScript":
                    self.scriptLinksClicked += 1
            except LinkException:
                print("Could not click link:" + str(link))
        scriptCount = 0
        print("Done Clickling links")
        for link in self.links:
            print("Writing link to file")
            if link.type == "html":
                link.writeFile(self.filePath, 0)
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
    "Only called by link class. Add to switch statement as necessary"

    def __init__(self, switch=1):
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
        self.text = ""
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
        page_source_replaced = driver.page_source
        # Remove inline tags
        for it in inline_tags:
            page_source_replaced = page_source_replaced.replace("<" + it + ">", "")
            page_source_replaced = page_source_replaced.replace("</" + it + ">", "")

        # Create random string for tag delimiter
        random_string = "".join(map(chr, os.urandom(75)))
        soup = BeautifulSoup(page_source_replaced, 'lxml')
        # remove non-visible tags
        [s.extract() for s in soup(['style', 'script', 'head', 'title', 'meta', '[document]'])]
        visible_text = soup.getText(random_string).replace("\n", "")
        visible_text = visible_text.split(random_string)
        self.text = "\n".join(list(filter(lambda vt: vt.split() != [], visible_text)))

    def click(self) -> bool:
        driver = prepDriver()
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
        if delimiter == "/":
            raise ValueError("ERROR: Delimiter cannot be a slash")
        if self.type == "html":
            unfilteredName = self.hrefAttribute[self.hrefAttribute.index(self.matcher):len(self.hrefAttribute)]
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
schools = readCSV("data/micro-sample13_coded.csv")
numberofLinksClicked = 0
totalNumberOfLinks = 0
htmlLinks = 0
htmlLinksClicked = 0
scriptLinks = 0
scriptLinksClicked = 0
"Time doesn't really account for timezones now, many be an issue later"
now = datetime.datetime.now()
formattedTime = now.strftime("%Y-%m-%d %H:%M:%S")
diagnosticsFile = open("diagnostics/" + str(formattedTime) + ".txt", "w")
diagnosticsFile.write("Program was run at " + formattedTime + "\n")
i = 0
startTime = datetime.datetime.now()
for school in schools:
    school.gatherLinks()
    schoolStartTime = datetime.datetime.now()
    school.clickLinks()
    schoolTimeElapsed = datetime.datetime.now() - startTime
    totalNumberOfLinks += school.totalNumberofLinks
    numberofLinksClicked += school.linksClicked
    htmlLinks += school.htmlLinks
    htmlLinksClicked += school.htmlLinksClicked
    scriptLinks += school.scriptLinks
    scriptLinks += school.scriptLinksClicked
    diagnosticsFile.write(
        "School " + str(school.name) + " had " + str(school.totalNumberofLinks) + " links and " + str(
            school.linksClicked) + " were clicked(" + str(
            (school.linksClicked / school.totalNumberofLinks) * 100) + "%)\n")
    try:
        diagnosticsFile.write(
            "There were " + str(school.htmlLinks) + " html links and " + str(
                school.htmlLinksClicked) + " were clicked(" + str(
                round((school.htmlLinksClicked / school.htmlLinks) * 100, 3)) + "%)\n"
        )
    except ZeroDivisionError:
        diagnosticsFile.write("This school had 0 html links \n")

    try:
        diagnosticsFile.write(
            "There were " + str(school.scriptLinks) + " JavaScript links and " + str(
                school.scriptLinksClicked) + " were clicked(" + str(round(
                (school.scriptLinksClicked / school.scriptLinks) * 100, 3)) + "%)\n"
        )
    except ZeroDivisionError:
        diagnosticsFile.write("This school had 0 JavaScript Links \n")

    diagnosticsFile.write("It took " + str(schoolTimeElapsed) + " to click on the links for this school\n")
timeElapsed = datetime.datetime.now() - startTime

diagnosticsFile.write("Total number of links:" + str(totalNumberOfLinks) + "\n")
diagnosticsFile.write("Number of Links Clicked:" + str(numberofLinksClicked) + "\n")
diagnosticsFile.write("% of links clicked:" + str(numberofLinksClicked / totalNumberOfLinks) + "\n")
diagnosticsFile.write("Number of HTML Links" + str(htmlLinks) + "\n")
diagnosticsFile.write("% of HTML Links Clicked" + str(htmlLinks / htmlLinksClicked) + "\n")
diagnosticsFile.write("Number of JavaScript Links" + str(scriptLinks) + "\n")
diagnosticsFile.write("% of JavaScript Links Clicked" + str(scriptLinks / scriptLinksClicked) + "\n")
diagnosticsFile.write("Time taken to click all links + " + str(timeElapsed))
diagnosticsFile.close()
