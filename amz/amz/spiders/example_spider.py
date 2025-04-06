import scrapy

class ExampleSpider(scrapy.Spider):
    name = "example"
    allowed_domains = ["amazon.pl"]
    # start_urls = ["https://www.amazon.com/s?k=laptops"] # Wyszukiwarka
    # start_urls = ["https://www.amazon.com/s?k=zabawki&page=8"] # i td
    start_urls = ["https://www.amazon.pl/s?i=electronics&bbn=20657432031&rh=n%3A20788267031&s=popularity-rank&fs=true&page=2&ref=lp_20788267031_sar"]

    def parse(self, response):

        if response.status == 403:
            self.log("Access forbidden - 403 error.")
            return
        

        for product in response.css('div.s-main-slot div.s-result-item'):
            yield {
                'title': product.css('span::text').get(),
                'image_url': product.css('img.s-image::attr(src)').get(),  # Extract image URL
                'price': product.css('span.a-price-whole::text').get(),
                'rating': product.css('span.a-icon-alt::text').get(),
                'reviews': product.css('span.a-size-base.s-underline-text::text').get(),
                'url': product.css('a.a-link-normal::attr(href)').get(),
            }