# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NightcapclothingScraperItem(scrapy.Item):
    url = scrapy.Field()  # string
    external_id = scrapy.Field()  # string
    categories = scrapy.Field()  # list
    name = scrapy.Field()  # string
    price = scrapy.Field()  # string
    colors = scrapy.Field()  # list
    sizes = scrapy.Field()  # list
    details = scrapy.Field()  # list
    images = scrapy.Field()  # list
    fabric = scrapy.Field()  # string
    occasions = scrapy.Field()  # list
    length = scrapy.Field()  # string
    neck_line = scrapy.Field()  # string
    fit = scrapy.Field()  # string
    style = scrapy.Field()  # list
    gender = scrapy.Field()  # string
    aesthetics = scrapy.Field()  # string
    number_of_reviews = scrapy.Field()  # string
    review_description = scrapy.Field()  # list
    top_best_seller = scrapy.Field()  # string
    meta = scrapy.Field()  # json
    website_name = scrapy.Field()
    pass
