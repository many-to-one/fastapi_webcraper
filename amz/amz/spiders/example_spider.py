import scrapy
import pandas as pd

class ExampleSpider(scrapy.Spider):

    name = "amazon"
    allowed_domains = ["amazon.pl"]
    # start_urls = ["https://www.amazon.com/s?k=laptops&page=22"] # Wyszukiwarka
    # start_urls = ["https://www.amazon.com/s?k=zabawki&page=8"] # i td
    # start_urls = ["https://www.amazon.com/s?k=tablets&rh=n%3A1232597011%2Cp_n_size_browse-bin%3A7817235011&crid=1Y6QHLGWI6DP1&nav_sdd=aps&rnid=1254615011&sprefix=tablets&ref=nb_sb_ss_w_sbl-tr-t1_k0_1_7_0"]

    def __init__(self, url=None, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.start_urls = [url] if url else ["https://default-url.com"]  # Use given URL or fallback

    def parse(self, response):

        if response.status == 403:
            self.log("Access forbidden - 403 error.")
            return
        
        products = []
        for product in response.css('div.s-main-slot div.s-result-item'):
            products.append(
                {
                    'title': product.css('span::text').get(),
                    'image_url': product.css('img.s-image::attr(src)').get(),  # Extract image URL
                    'price': product.css('span.a-price-whole::text').get(),
                    'rating': product.css('span.a-icon-alt::text').get(),
                    'reviews': product.css('span.a-size-base.s-underline-text::text').get(),
                    'url': product.css('a.a-link-normal::attr(href)').get(),
                }
            )

            df = pd.DataFrame(products)
            df.to_excel("products.xlsx", index=False, engine="openpyxl")

            # yield {
            #     'title': product.css('span::text').get(),
            #     'image_url': product.css('img.s-image::attr(src)').get(),  # Extract image URL
            #     'price': product.css('span.a-price-whole::text').get(),
            #     'rating': product.css('span.a-icon-alt::text').get(),
            #     'reviews': product.css('span.a-size-base.s-underline-text::text').get(),
            #     'url': product.css('a.a-link-normal::attr(href)').get(),
            # }
