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

    def __init__(self, start_urls=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = start_urls
        self.max_pages = 400
        self.page_counter = 0
        self.current_page = 1
        self.scraped_urls = set()
        self.asins = set()
        self.data = []


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
        products = response.css('div.s-main-slot div.s-result-item')
        new_products_found = False

        import re, urllib.parse

        def extract_asin(url):
            match = re.search(r'/dp/([A-Z0-9]+)|/gp/product/([A-Z0-9]+)', url)
            if match:
                return match.group(1) or match.group(2)  # Return the ASIN
            return ''


        count = 0
        asin = None

        for product in products:
            product_url = product.css('a.a-link-normal::attr(href)').get()

            if product_url: # and asin not in self.asins
                if product_url[:5] == "/sspa":
                    parsed_url = urllib.parse.parse_qs(urllib.parse.urlparse(product_url).query)
                    row_product_url = parsed_url.get("url", [""])[0]
                    product_url = urllib.parse.unquote(row_product_url)

                    asin = extract_asin(product_url)
                    if asin:
                        print(' ############################### asin ############################### ', asin)
                        # self.asins.add(asin)

                else:
                    asin = extract_asin(product_url)
                    
                self.asins.add(asin)
                new_products_found = True

                product_title = product.css('span::text').get()  # First attempt (may return 'Sponsorowane')
                # print(' ############################### product_title CLEAN ############################### ', product_title)

                is_sponsored = ''

                if product_title == "Sponsorowane":  
                    print(' ############################### Sponsorowane ? ############################### ', 'YES')
                    product_title = product.css('h2 span::text').get()  # Extract actual title only if 'Sponsorowane' a-size-base-plus
                    print(' ############################### Sponsorowane product_title ############################### ', product_title)
                    is_sponsored = "Sponsorowane"

                product_data = {
                    'date': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'is_sponsored': is_sponsored,
                    "asin": asin, 
                    'title': product_title,
                    'image_url': product.css('img.s-image::attr(src)').get(),
                    'price': product.css('span.a-price-whole::text').get(),
                    'rating': product.css('span.a-icon-alt::text').get(),
                    'reviews': product.css('span.a-size-base::text').get(),  
                    'url': product_url,
                }

                count += 1
                print(" ############################### COUNT ############################### ", count, 'test_category_name')

                if product_data['title'] == "Sponsorowane" and count == 3:
                    self.logger.info(" ############################### THE END ############################### ")
                    self.save_to_excel()
                    raise scrapy.exceptions.CloseSpider("Skipping sponsored product.")

                # if product_data['price'] is not None:
                self.data.append(product_data)  # Add product to list
                self.save_to_excel()
                yield product_data
        
        # if new_products_found:
        #     self.current_page += 1
        #     next_page_url = f"{self.base_url}&page={self.current_page}&ref=sr_nr_p_n_condition-type_1&s=popularity-rank"
        #     random_delay = random.uniform(3, 4) #random.uniform(3, 12) 
        #     yield scrapy.Request(url=next_page_url, callback=self.parse)

        #     if self.current_page % 10 == 0:
        #     # # if self.current_page == 2:
        #         self.save_to_excel()
        #         long_random_delay = random.uniform(4, 5) # random.uniform(60, 120)
        #         time.sleep(long_random_delay)  # Longer delay every 20 pages
        #         self.logger.info(f" ************* LONG DELAY {long_random_delay} seconds at {self.current_page} page ************* ")

        #         yield scrapy.Request(url=next_page_url, callback=self.parse)
            
        #     else:
        #         time.sleep(random_delay)  # Sleep for a random time to avoid being blocked
        #         self.logger.info(f" ************* Scraping page {self.current_page}... ****** DELAY {random_delay} seconds ************* ")

        #         yield scrapy.Request(url=next_page_url, callback=self.parse)
        # else:
        #     self.logger.info("No new products found. Saving to Excel.")
        #     self.save_to_excel()  # Call the save function when scraping stops




    def save_to_excel(self):

        DATA_DIR = f"amz/products/test_category_name/{time.strftime('%Y-%m-%d')}/"
        os.makedirs(DATA_DIR, exist_ok=True)

        filename = f"{'test_category_name'}.xlsx"

        file_path = os.path.join(DATA_DIR, filename)

        # Convert data to a Pandas DataFrame
        df = pd.DataFrame(self.data)

        # Clean data
        df["price"] = pd.to_numeric(df["price"].str.replace("\xa0", "", regex=False), errors="coerce")
        df["rating"] = pd.to_numeric(df["rating"].str.extract(r'(\d+)')[0], errors="coerce")

        # Remove duplicate ASINs (keeping first occurrence)
        df = df.drop_duplicates(subset=["asin"], keep="first")

        sorted_df = df.sort_values(by="price", ascending=False)

        try:
            # Load existing workbook
            workbook = load_workbook(file_path)
            sheet = workbook.active

            # Read existing ASINs to avoid duplicates
            existing_asins = set()
            for row in sheet.iter_rows(min_row=2, values_only=True):  # Assuming headers exist
                existing_asins.add(row[0])  # Assuming 'asin' is the first column

            # Filter out ASINs that are already in the file
            sorted_df = sorted_df[~sorted_df["asin"].isin(existing_asins)]

            # Append only new unique rows
            for _, row in sorted_df.iterrows():
                sheet.append(row.tolist())

            # Save changes
            workbook.save(file_path)

            self.logger.info(f"Data saved to '{file_path}', only unique ASINs recorded.")
            self.data = []  # Clear the data list after saving

        except FileNotFoundError:
            # If file doesn't exist, create a new one with unique ASINs
            sorted_df.to_excel(file_path, index=False, engine="openpyxl")