# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class CharterItem(Item):
    """
    The url of the item, the text with tags stripped,
    and the depth as defined by DepthMiddleware. 
    """
    url = Field()
    text = Field()
    depth = Field()
    
    