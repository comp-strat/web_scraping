import scrapy
import csv
from bs4 import BeautifulSoup
import uuid 

inline_tags = ["b", "big", "i", "small", "tt", "abbr", "acronym", "cite", "dfn",
                       "em", "kbd", "strong", "samp", "var", "bdo", "map", "object", "q",
                                      "span", "sub", "sup"]
class QuotesSpider(scrapy.Spider):
        name = "quotes"
        def start_requests(self):
            urls = []
            with open("test_urls.csv", "r") as f:
                reader = csv.reader(f, delimiter="\t",quoting=csv.QUOTE_NONE)
                r,nr= 0, 0
                for i, line in enumerate(reader):
                    if i == 0:
                        continue
                    urllst = line[0].split(",",1)
                    if "http" in urllst[1]:
                        urls.append(urllst[1])
                        r+=1
                    else:
                        nr+=1
                print("COUNT IS THIS ", r, "AND THIS ",nr)
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)


        def parse(self, response):
            page = response.url.split("/")[-2]
            filename = '%s.html' % page
            with open(filename, 'wb') as f:
                f.write(response.body)
            self.log('Saved file %s' % filename)
            
            # adding the sublink tracer subroutine
            txt_body = response.body
            # Remove inline tags
            txt_body = BeautifulSoup(txt_body, "lxml").text
            #for it in inline_tags:
            #    txt_body = txt_body.replace("<" + it + ">", "")
            #    txt_body = txt_body.replace("</" + it + ">", "")
            # Create random string for tag delimiter
            # random_string = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=75))
            random_string = str(uuid.uuid4().hex.upper())
            soup = BeautifulSoup(txt_body, 'lxml')

            # remove non-visible tags
            [s.extract() for s in soup(['style', 'script', 'head', 'title', 'meta', '[document]'])]
            visible_text = soup.getText(random_string).replace("\n", "")
            visible_text = visible_text.split(random_string)
            visible_text = "\n".join(list(filter(lambda vt: vt.split() != [], visible_text)))
            visible_text = list(normalize("NFKC",elem.replace("\t","")).encode("utf-8").decode("utf-8") for elem in visible_text.split(random_string))
            for it in inline_tags:
                [s.extract() for s in soup("</" + it + ">")]
            txtfilename = '%s.txt' % page
            with open(txtfilename, 'w') as f:
                f.write(visible_text)


