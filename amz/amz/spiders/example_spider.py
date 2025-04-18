import scrapy
import time
import random
import pandas as pd



class ExampleSpider(scrapy.Spider):
    name = "amazon"

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_url = url if url else "https://default-url.com"
        self.current_page = 1
        self.scraped_urls = set()
        self.data = []  # List to store all scraped offers

    def start_requests(self):
        paginated_url = f"{self.base_url}&page={self.current_page}"
        yield scrapy.Request(url=paginated_url, callback=self.parse)

    def parse(self, response):
        products = response.css('div.s-main-slot div.s-result-item')
        new_products_found = False

        for product in products:
            product_url = product.css('a.a-link-normal::attr(href)').get()

            if product_url and product_url not in self.scraped_urls:
                new_products_found = True
                self.scraped_urls.add(product_url)

                product_data = {
                    'title': product.css('span::text').get(),
                    'image_url': product.css('img.s-image::attr(src)').get(),
                    'price': product.css('span.a-price-whole::text').get(),
                    'rating': product.css('span.a-icon-alt::text').get(),
                    'reviews': product.css('span.a-size-base.s-underline-text::text').get(),
                    'url': product_url
                }

                self.data.append(product_data)  # Add product to list
                yield product_data

        if new_products_found:
            self.current_page += 1
            next_page_url = f"{self.base_url}&page={self.current_page}"
            random_delay = random.uniform(1, 10)  # Random delay between 1 and 3 seconds
            time.sleep(random_delay)  # Sleep for a random time to avoid being blocked
            self.logger.info(f"Scraping page {self.current_page}...")

            yield scrapy.Request(url=next_page_url, callback=self.parse)
        else:
            self.logger.info("No new products found. Saving to Excel.")
            self.save_to_excel()  # Call the save function when scraping stops

    def save_to_excel(self):
        # Convert data to a Pandas DataFrame
        df = pd.DataFrame(self.data)

        # Save to an Excel file
        df.to_excel("scraped_offers.xlsx", index=False, engine="openpyxl")

        self.logger.info("Data saved to 'scraped_offers.xlsx'.")


# ********************************************************************************



# class ExampleSpider(scrapy.Spider):
#     name = "amazon"

#     def __init__(self, url=None, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.base_url = url if url else "https://default-url.com"
#         self.current_page = 1  # Start from page 1
#         self.scraped_urls = set()  # Track scraped product URLs
#         self.data = []  # Initialize an empty list to store product data

#     def start_requests(self):
#         paginated_url = f"{self.base_url}&page={self.current_page}"
#         yield scrapy.Request(url=paginated_url, callback=self.parse)

#     def parse(self, response):
#         products = response.css('div.s-main-slot div.s-result-item')  # Select all products
#         new_products_found = False  # Flag to check if new products are found

#         for product in products:
#             product_url = product.css('a.a-link-normal::attr(href)').get()

#             if product_url and product_url not in self.scraped_urls:
#                 new_products_found = True
#                 self.scraped_urls.add(product_url)  # Add to the set of scraped URLs

#                 # yield {
#                 #     'title': product.css('span::text').get(),
#                 #     'image_url': product.css('img.s-image::attr(src)').get(),
#                 #     'price': product.css('span.a-price-whole::text').get(),
#                 #     'rating': product.css('span.a-icon-alt::text').get(),
#                 #     'reviews': product.css('span.a-size-base.s-underline-text::text').get(),
#                 #     'url': product_url,
#                 # }

#                 products_data= {
#                         'title': product.css('span::text').get(),
#                         'image_url': product.css('img.s-image::attr(src)').get(),  
#                         'price': product.css('span.a-price-whole::text').get(),
#                         'rating': product.css('span.a-icon-alt::text').get(),
#                         'reviews': product.css('span.a-size-base.s-underline-text::text').get(),
#                         'url': product.css('a.a-link-normal::attr(href)').get(),
#                     }
                
#                 self.data.append(products_data)  # Append the product data to the list

#                 yield products_data

#         if new_products_found:  # If new products were found, continue to the next page
#             self.current_page += 1
#             next_page_url = f"{self.base_url}&page={self.current_page}"
#             random_delay = random.uniform(1, 10)  # Random delay between 1 and 3 seconds
#             time.sleep(random_delay)  # Sleep for a random time to avoid being blocked
#             self.logger.info(f"Scraping page {self.current_page}...")

#             yield scrapy.Request(url=next_page_url, callback=self.parse)
#         else:  # No new products found, stop scraping
#             self.logger.info("No new products found, stopping spider.")
#             self.save_to_excel()  # Save data to Excel when done
#             self.logger.info("Data saved to products.xlsx")


#     def save_to_excel(self):
#         df = pd.DataFrame(self.data)
#         df.to_excel("products.xlsx", index=False, engine="openpyxl")
#         self.logger.info("Data saved to products.xlsx")


# *******************************************************************************************


# class ExampleSpider(scrapy.Spider):

#     name = "amazon"
#     allowed_domains = ["amazon.pl"]
#     # start_urls = ["https://www.amazon.com/s?k=laptops&page=22"] # Wyszukiwarka
#     # start_urls = ["https://www.amazon.com/s?k=zabawki&page=8"] # i td
#     # start_urls = ["https://www.amazon.com/s?k=tablets&rh=n%3A1232597011%2Cp_n_size_browse-bin%3A7817235011&crid=1Y6QHLGWI6DP1&nav_sdd=aps&rnid=1254615011&sprefix=tablets&ref=nb_sb_ss_w_sbl-tr-t1_k0_1_7_0"]

#     def __init__(self, url=None, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        url = "https://www.amazon.pl/s?k=laptops"
#        self.base_url = url if url else ["https://default-url.com"]  
#        self.num_pages = 2

#     def start_requests(self):
#         for page in range(1, self.num_pages + 1):
#             url = f"{self.base_url}&page={page}"
#             yield scrapy.Request(url=url, callback=self.parse)

#     def parse(self, response):

#         if response.status == 403:
#             self.log("Access forbidden - 403 error.")
#             return
        
#         # products = []

#         for product in response.css('div.s-main-slot div.s-result-item'):
#         #     products.append(
#         #         {
#         #             'title': product.css('span::text').get(),
#         #             'image_url': product.css('img.s-image::attr(src)').get(),  
#         #             'price': product.css('span.a-price-whole::text').get(),
#         #             'rating': product.css('span.a-icon-alt::text').get(),
#         #             'reviews': product.css('span.a-size-base.s-underline-text::text').get(),
#         #             'url': product.css('a.a-link-normal::attr(href)').get(),
#         #         }
#         #     )

#         #     df = pd.DataFrame(products)
#         #     df.to_excel("products.xlsx", index=False, engine="openpyxl")

#             yield {
#                 'title': product.css('span::text').get(),
#                 'image_url': product.css('img.s-image::attr(src)').get(),  # Extract image URL
#                 'price': product.css('span.a-price-whole::text').get(),
#                 'rating': product.css('span.a-icon-alt::text').get(),
#                 'reviews': product.css('span.a-size-base.s-underline-text::text').get(),
#                 'url': product.css('a.a-link-normal::attr(href)').get(),
#             }
