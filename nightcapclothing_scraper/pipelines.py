# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy_dynamodb import DynamoDbPipeline
import boto3

class NightcapclothingScraperPipeline:
    def process_item(self, item, spider):
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table('Product')
        table.put_item(
            Item={"url": str(item["url"]), "Product#name": item["name"], "Product#category": item["categories"][0],
                  "categories": {"SS": item["categories"]}, "price": item["price"], "sizes": {"SS": item["sizes"]},
                  "details": {"SS": item["details"]}, "fabric": {"SS": item["fabric"]},
                  "images": {"SS": item["images"]}, "fit": item["fit"], "neck_line": item["neck_line"],
                  "length": item["length"], "gender": item["gender"],
                  "number_of_reviews": item["number_of_reviews"], "review_description": item["review_description"],
                  "top_best_seller": item["top_best_seller"], "meta": item["meta"],
                  "occasions": item["occasions"], "style": item["style"], "website_name": item["website_name"]})
        return item

