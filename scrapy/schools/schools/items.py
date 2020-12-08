# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class CharterItem(Item):
    """
    Represents the object parsed by the spider.
    Depth is defined by DepthMiddleware. 
    """
    url = Field() # str
    text = Field() # str   
    depth = Field() # int
    is_pdf = Field() # bool
    is_doc = Field() # bool
    is_im = Field() # bool
    status = Field() # int
    school_id = Field() # float this is school id or ncessch
    timestamp = Field() # datetime
    date_archived = Field() # datetime
    # Collecting Media
    image_urls = Field()
    images = Field()
    
    file_urls = Field()
    files = Field()