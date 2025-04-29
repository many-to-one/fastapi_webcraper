# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
import json


import os


class AmzSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class AmzDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


# DOWNLOADER_MIDDLEWARES = { 
#     'scraper.middlewares.RotateUserAgentMiddleware': 400, 
#     'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750, 
#     }

# USER_AGENTS = [ "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", 
#                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36", ]
# PROXIES = [ "http://user:pass@proxy1.com:8000", "http://user:pass@proxy2.com:8080", ]



# import random 

# class RotateUserAgentMiddleware: 
#     def process_request(self, request, spider): 
#         request.headers['User-Agent'] = random.choice(USER_AGENTS) 
#         request.meta['proxy'] = random.choice(PROXIES)


from rotating_proxies.middlewares import RotatingProxyMiddleware
from rotating_proxies.middlewares import BanDetectionMiddleware
import random

class CustomRotatingProxyMiddleware(RotatingProxyMiddleware):

    def load_proxies(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        proxy_file = os.path.join(base_dir, 'proxies.txt')
        with open(proxy_file) as f:
            return [line.strip() for line in f if line.strip()]
    
    def process_response(self, request, response, spider):
        # Call parent RotatingProxyMiddleware
        result = super().process_response(request, response, spider)

        # Custom logic: If banned a lot, reload proxies
        if self.stats.get_value('rotating_proxies/proxies_left', 0) < 3:
            spider.logger.warning("⚠️ Too few proxies left, reloading proxy list...")

            # (Re)load proxy list (you can read from file, or API)
            self.proxies = self.load_proxies()
            self.stats.set_value('rotating_proxies/proxies_left', len(self.proxies))
        
        return result
    


class DynamicAutoThrottleMiddleware:

    def __init__(self):
        self.delay = 0.5  # start small
        self.success_counter = 0
        self.ban_counter = 0

    @classmethod
    def from_crawler(cls, crawler):
        mw = cls()
        crawler.signals.connect(mw.response_received, signal=signals.response_received)
        return mw

    def response_received(self, response, request, spider):
        if response.status in [403, 429]:
            self.ban_counter += 1
        else:
            self.success_counter += 1

        total = self.success_counter + self.ban_counter
        if total >= 20:  # check every 20 requests
            success_rate = self.success_counter / total
            if success_rate < 0.7:
                self.delay = min(self.delay + 0.2, 10)  # slower if bad
            else:
                self.delay = max(self.delay - 0.1, 0.5)  # faster if good
            
            spider.crawler.settings.set('DOWNLOAD_DELAY', self.delay, priority='spider')
            spider.logger.info(f"Dynamic delay adjusted to {self.delay:.2f}s (success rate {success_rate:.2%})")

            # reset
            self.success_counter = 0
            self.ban_counter = 0



class ProxyStatsMiddleware:

    def __init__(self):
        self.proxy_usage = {}  # {proxy: {"ok": int, "ban": int}}

    @classmethod
    def from_crawler(cls, crawler):
        mw = cls()
        crawler.signals.connect(mw.response_received, signal=signals.response_received)
        crawler.signals.connect(mw.spider_closed, signal=signals.spider_closed)
        crawler.settings = crawler.settings
        return mw

    def response_received(self, response, request, spider):
        proxy = request.meta.get('proxy')
        if not proxy:
            return

        if proxy not in self.proxy_usage:
            self.proxy_usage[proxy] = {"ok": 0, "ban": 0}

        if response.status in [403, 429]:  # Ban detection
            self.proxy_usage[proxy]["ban"] += 1
        else:
            self.proxy_usage[proxy]["ok"] += 1

    def spider_closed(self, spider):       
        with open('proxy_stats.json', 'w') as f:
            json.dump(self.proxy_usage, f)
