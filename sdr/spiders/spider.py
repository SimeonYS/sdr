import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import SdrItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class SdrSpider(scrapy.Spider):
	name = 'sdr'
	start_urls = ['https://sdrhaa.dk/nyheder']

	def parse(self, response):
		articles = response.xpath('//div[@class="text-content"]/div[@class="row"]/div[@class="col-sm-12"]')
		for article in articles:
			date = article.xpath('.//p/text()').get()
			title = article.xpath('.//h2/text()').get()
			post_links = article.xpath('.//a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date, title=title))

	def parse_post(self, response, date, title):
		content = response.xpath('//div[@class="text-content"]//text()[not (ancestor::h4)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=SdrItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
