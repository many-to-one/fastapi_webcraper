import os, requests
import scrapy, time, openpyxl, random
import pandas as pd
from openpyxl import load_workbook



# PROXY_APIS = [
#     "https://www.proxy-list.download/api/v1/get?type=https",
#     "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
# ]

# def fetch_proxies_from_api():
#     # Example free proxy API
#     api_url = random.choice(PROXY_APIS)

#     try:
#         response = requests.get(api_url)
#         proxies = response.text.splitlines()
#         return proxies
#     except Exception as e:
#         print(f"Failed to fetch proxies: {e}")
#         return []
    

class WholeSpider(scrapy.Spider):
    name = "my_spider"

    def __init__(self, start_urls=None, file_path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = start_urls
        self.file_path=file_path
        self.page_counter = 1
        self.max_pages = 10000
        self.df = pd.read_excel(file_path)
        self.df["first_availability_date"] = None


    # def start_request(self):

    #     try:
    #         df = pd.read_excel(self.file_path)
    #     except Exception as e:
    #         self.logger.error(f"Failed to read Excel file: {e}")
    #         return

    #     for url self.start_urls.dropna():
    #         yield scrapy.Request(
    #             url=url,
    #             callback=self.parse_first_date,
    #             meta={'product_url': url}
    #         )


    def parse(self, response):
        # scrape data
        self.page_counter += 1

        # Update progress
        progress = int((self.page_counter / self.max_pages) * 100)
        with open(f"amz/progress_batch_test.txt", "w") as f:
            f.write(str(progress))

        # Stop when enough pages scraped
        if self.page_counter >= self.max_pages:
            return
        

        # Scraping proccess logic
        first_availability_date = response.xpath(
            '//th[contains(text(), "Data pierwszej dostępności")]/following-sibling::td/text()'
        ).get()
        print(' ++++++++++++++++++++++++++++++++++++++ first_availability_date ++++++++++++++++++++++++++++++++++++++ ', first_availability_date)

        # Update the corresponding row in the DataFrame
        self.df.loc[self.df["url"] == response.url, "first_availability_date"] = first_availability_date

        # Stop condition
        if self.page_counter >= self.max_pages or self.page_counter >= len(self.start_urls):
            self.save_to_excel()




    def save_to_excel(self):
        try:
            self.df.to_excel(self.file_path, index=False)
            self.logger.info(f" ++++++++++++++++++++++++++++++++++++++ Updated Excel file saved to: {self.file_path} ++++++++++++++++++++++++++++++++++++++ ")
        except Exception as e:
            self.logger.error(f" ++++++++++++++++++++++++++++++++++++++ Failed to save Excel file: {e} ++++++++++++++++++++++++++++++++++++++ ")
