import scrapy
import re
import os
from sqlite.items import SqliteItem


class SqliteSpider(scrapy.Spider):
    name = 'sqlite'
    allowed_domains = ['www.sqlite.org/index.html']
    start_urls = ['http://www.sqlite.org/index.html']

    def parse(self, response):

        print('Processing SQLite - accessing {0}'.format(response.url))

        version = response.xpath("//a[contains(text(),'Version')]/text()").get()
        version = version.split(' ')[1]
        release_date = response.xpath("/html/body/text()").re(r' \((.+)\).')  # to get the date without bracket
        release_date = release_date[0]

        site_base = 'http://www.sqlite.org'
        releaselog_url = response.xpath("//a[contains(text(),'Version')]/@href").get()
        full_releaselog_url = f'{site_base}/{releaselog_url}'

        yield scrapy.Request(url=full_releaselog_url, callback=self.parse_releaselog_page, meta={
            'version': version,
            'release_date': release_date
        }, dont_filter=True)

    def parse_releaselog_page(self, response):
        version = response.meta['version']
        release_date = response.meta['release_date']
        releaselog_title = response.xpath("//h2").getall()
        releaselog_title = ''.join([str(title) for title in releaselog_title])
        releaselog_content = response.xpath("//ol").getall()
        releaselog_content = ''.join([str(content) for content in releaselog_content])

        download_url = 'https://www.sqlite.org/download.html'
        yield scrapy.Request(url=download_url, callback=self.parse_download_page, meta={
            'version': version,
            'release_date': release_date,
            'content': releaselog_title + releaselog_content
        }, dont_filter=True)

    def parse_download_page(self, response):
        site_base = 'http://www.sqlite.org'
        release_date = response.meta['release_date']
        year = release_date.split('-')[0]

        filename = response.xpath('//*[@id="a2"]/text()').get()
        download_path = f'{site_base}/{year}/{filename}'

        item = SqliteItem()
        item['name'] = 'sqlite'
        item['version'] = response.meta['version']
        item['download_path'] = download_path  # get https://..
        item['filename'] = filename  # get tar.gz file
        item['version'] = response.meta['version']
        item['name_version'] = '{0}-{1}'.format(item['name'], item['version'])  # get name-version
        item['release_date'] = release_date
        item['content'] = response.meta['content']
        item['bundle_name'] = 'sqlite'
        yield item