import re
from ast import keyword

import time
from unicodedata import category
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import NightcapclothingScraperItem
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from scrapy import Selector
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pathlib import Path
from webdriver_manager.chrome import ChromeDriverManager

# this method configures initial settings for selenium chrome webdriver


ALLOWED_CATEGORIES = ["denim", "ready-to-wear-all"]
FIT_KEYWORDS = ["Maternity", "Petite", "Plus Size", "Curvy", "Tall"]
NECK_LINE_KEYWORDS = ["Scoop", "Round Neck," "U Neck", "U-Neck", "V Neck",
                      "V-neck", "V Shape", "V-Shape", "Deep", "Plunge", "Square",
                      "Straight", "Sweetheart", "Princess", "Dipped", "Surplice",
                      "Halter", "Asymetric", "One-Shoulder", "One Shoulder",
                      "Turtle", "Boat", "Off- Shoulder", "Collared", "Cowl", "Neckline"]

OCCASIONS_KEYWORDS = ["office", "work", "smart", "workwear", "wedding", "nuptials",
                      "night out", "evening", "spring", "summer", "day", "weekend",
                      "outdoor", "outdoors", "adventure", "black tie", "gown",
                      "formal", "cocktail", "date night", "vacation", "vacay", "fit",
                      "fitness", "athletics", "athleisure", "work out", "sweat",
                      "swim", "swimwear", "lounge", "loungewear"]

LENGTH_KEYWORDS = ["length", "mini", "short", "maxi", "crop", "cropped", "sleeves",
                   "tank", "top", "three quarter", "ankle", "long"]
FABRIC_KEYWORDS = ["Velvet", "Silk", "Satin", "Cotton", "Lace", "Sheer", "Organza", "Chiffon", "Spandex",
                   "Polyester", "Poly", "Linen", "Nylon", "Viscose", "Georgette", "Ponte", "Smock", "Smocked",
                   "Shirred",
                   "Rayon", "Bamboo", "Knit", "Crepe", "Leather", ]

STYLE_KEYWORDS = ["bohemian", "embellished", "sequin", "floral", "off shoulder",
                  "puff sleeve", "bodysuit", "shell", "crop", "corset", "tunic",
                  "bra", "camisole", "polo", "aviator", "shearling", "sherpa",
                  "biker", "bomber", "harrington", "denim", "jean", "leather",
                  "military", "quilted", "rain", "tuxedo", "windbreaker", "utility",
                  "duster", "faux fur", "overcoat", "parkas", "peacoat", "puffer",
                  "skater", "trench", "Fleece", "a line", "bodycon", "fitted",
                  "high waist", "high-low", "pencil", "pleat", "slip", "tulle",
                  "wrap", "cargo", "chino", "skort", "cigarette", "culottes",
                  "flare", "harem", "relaxed", "skinny", "slim", "straight leg",
                  "tapered", "wide leg", "palazzo", "stirrup", "bootcut", "boyfriend",
                  "loose", "mom", "jeggings", "backless", "bandage", "bandeau",
                  "bardot", "one-shoulder", "slinger", "shift", "t-shirt", "smock",
                  "sweater", "gown"]

AESTHETIC_KEYWORDS = ["E-girl", "VSCO girl", "Soft Girl", "Grunge", "CottageCore",
                      "Normcore", "Light Academia", "Dark Academia ", "Art Collective",
                      "Baddie", "WFH", "Black", "fishnet", "leather"]
empty = ''
WEBSITE_NAME = "nightcapclothing"

class NightcapclothingSpider(scrapy.Spider):
    name = 'nightcapclothing'

    # rules = (
    #     Rule(LinkExtractor(allow=r'product/'), callback='parse_product'),
    # )

    def start_requests(self):
        base_url = "https://www.nightcapclothing.com"
        yield scrapy.Request(url=base_url, callback=self.parse_categories)

    def __init__(self, *a, **kw):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        super().__init__(*a, **kw)

    def parse_categories(self, response):
        categories = response.css(
            "ul.submenu.submenu--items-12 a.submenu-item--link.submenu-item__title::attr('href')").getall()
        categories.pop(0)
        # Categories were not right before, Now only 5 categories which are required are being selected
        categories = categories[0:5]
        for url in categories:
            print(url)
            main_category_url = response.urljoin(url)
            yield scrapy.Request(url=main_category_url, callback=self.find_all_products,
                                 meta={"categories": url.split("/")[-1]})

    def find_all_products(self, response):
        self.driver.get(response.request.url)
        time.sleep(5)
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        SCROLL_PAUSE_TIME = 8
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        customeResponse = Selector(text=self.driver.page_source)
        product_links = customeResponse.css("div#MainContent a::attr('href')").getall()
        product_links = list(dict.fromkeys(product_links))
        for link in product_links:
            # Removed additional "/" from link
            mainurl = "https://nightcapclothing.com" + link
            yield scrapy.Request(url=mainurl, callback=self.parse_product,
                                 meta={"categories": response.meta.get("categories", [])}, )

    def parse_product(self, response):
        self.driver.get(response.request.url)
        time.sleep(5)
        custom_response = Selector(text=self.driver.page_source)
        url = response.request.url
        categories = [response.meta.get("categories", [])]
        brand = "Night Cap"
        product_name = custom_response.css("h1.product-title::text").get()
        product_name = product_name.strip() if product_name is not None else ""
        name = f"{brand} {product_name}"
        price = custom_response.css('strike.product-compare-price span.money::text').get()
        if (price is None):
            price = custom_response.css('div.product-normal-price span.money::text').get()
        price = price.replace(" ", "")
        sizes = custom_response.css(
            "div.productForm-block.productForm-block--options-inline div:nth-child(1) select.single-option-selector *::text").getall()
        colors = custom_response.css(
            "div.productForm-block.productForm-block--options-inline div:nth-child(2) select.single-option-selector *::text").getall()
        details = custom_response.css("div.product-container *::text").getall()
        details = self.clean_details(details)
        # Changed the fabric method given in the end and used it here
        fabric = self.find_fabric_from_details(details)
        images = custom_response.xpath('(//div[@class="slick-list draggable"])[2] //img /@srcset').getall()
        a = []
        if images == []:
            images = custom_response.css(
                "div.js-slide.product-image--100.product-image.product-image--fit.fade-in.lazyloaded a::attr('href')").getall()
        a = []
        for i in images:
            i = i.strip()
            if " " in i:
                i = i.split(" ")[0]
            a.append(i)
        images = a
        for i in images:
            external_id = i.split("v=")[1]
            break
        images = list(set(images))
        a = []
        for i in images:
            a.append("https:" + i)
        images = a
        fit = self.find_from_target_string_single(details, FIT_KEYWORDS)
        neck_line = self.find_from_target_string_single(details, NECK_LINE_KEYWORDS)
        length = self.find_from_target_string_multiple(details, name, categories, LENGTH_KEYWORDS)
        gender = "women"
        number_of_reviews = ""
        review_description = []
        top_best_seller = ""
        meta = {}

        occasions = self.find_from_target_multiple_list(details, name, categories, OCCASIONS_KEYWORDS)
        style = self.find_from_target_multiple_list(details, name, categories, STYLE_KEYWORDS)
        # aesthetics = self.find_from_target_string_multiple(details, name, categories, AESTHETIC_KEYWORDS)

        item = NightcapclothingScraperItem()
        item["url"] = url
        item["external_id"] = external_id
        item["categories"] = categories
        item["name"] = name
        item["price"] = price
        item["colors"] = colors
        item["sizes"] = sizes
        item["details"] = details
        item["fabric"] = fabric
        item["images"] = images
        item["fit"] = fit
        item["neck_line"] = neck_line
        item["length"] = length
        item["gender"] = gender
        item["number_of_reviews"] = number_of_reviews
        item["review_description"] = review_description
        item["top_best_seller"] = top_best_seller
        item["meta"] = meta
        item["occasions"] = occasions
        item["style"] = style
        # item["aesthetics"] = aesthetics
        item["website_name"] = WEBSITE_NAME
        yield item

    def find_from_target_string_single(self, source_data, target_keywords):
        for each_element in source_data:
            if any(keyword.lower() in each_element.lower() for keyword in target_keywords):
                return each_element

        return ""

    def find_from_target_multiple_list(self, details, name, categories, target_keywords):
        target_list = details[:]
        target_list.extend(name)
        target_list.extend(categories)
        final_list = []

        for each_element in target_list:
            if any(keyword.lower() in each_element.lower() for keyword in target_keywords):
                final_list.append(each_element)

        return final_list

    def find_from_target_string_multiple(self, details, name, categories, target_keywords):
        target_list = details[:]
        target_list.extend(name)
        target_list.extend(categories)

        for element in target_list:
            if any(keyword.lower() in element.lower() for keyword in target_keywords):
                return element
        return ""

    def clean_details(self, details):
        d = []
        for i in details:
            i = i.strip()
            if i is None:
                d.append("")
            elif i == "FINAL SALE":
                continue
            elif i == "Final Sale":
                continue
            elif "fits" in i.lower():
                continue
            else:
                d.append(i)

        details = d
        details = [detail for detail in details if detail != ""]
        return details

    # Changed this method to find the exact word of fabrics instead of whole string.
    def find_fabric_from_details(self, details):
        s = ' '.join(details)
        s.replace("/", " ")
        s = s.lower()
        l = s.split()
        k = []
        for i in l:
            if (s.count(i) >= 1 and (i not in k)):
                k.append(i)
        product_details = (' '.join(k))
        fabrics_founded = re.findall(r"""(\d+ ?%\s?)?(
            velvet\b|silk\b|satin\b|cotton\b|lace\b|
            sheer\b|organza\b|chiffon\b|spandex\b|polyester\b|
            poly\b|linen\b|nylon\b|viscose\b|Georgette\b|Ponte\b|
            smock\b|smocked\b|shirred\b|Rayon\b|Bamboo\b|Knit\b|Crepe\b|
            Leather\b|polyamide\b|Acrylic\b|Elastane\b)""", product_details, flags=re.IGNORECASE | re.MULTILINE)
        p = (' '.join([' '.join(tups) for tups in fabrics_founded])).strip()
        return p.replace("  "," ")





