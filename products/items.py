# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductsItem(scrapy.Item):
    # define the fields for your item here like:
    name = 'products'
    page = scrapy.Field()
    index = scrapy.Field()

    catalogue_number = scrapy.Field()
    chemical_name = scrapy.Field()
    cas_number = scrapy.Field()
    synonyms = scrapy.Field()
    molecular_formula = scrapy.Field()
    molecular_weight = scrapy.Field()

    order_products = scrapy.Field()
