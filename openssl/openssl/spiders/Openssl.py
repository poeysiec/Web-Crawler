import scrapy
import re
import os
from openssl.items import OpensslItem


class OpensslSpider(scrapy.Spider):
    name = 'openssl'
    allowed_domains = ['www.openssl.org/source']
    start_urls = ['http://www.openssl.org/source']

    def parse(self, response):
        print('Processing Openssl - accessing {0}'.format(response.url))

        content_nameversion = response.xpath('//*[@id="content"]/div/article/div/table//tr[3]/td[3]/a[1]/text()')
        name = response.xpath('//*[@id="content"]/div/article/div/table//tr[3]/td[3]/a[1]/text()').re(r'(.+)-')
        version = response.xpath('//*[@id="content"]/div/article/div/table//tr[3]/td[3]/a[1]/text()').re(
            r'-(.+).tar.gz')

        content_date_raw = response.xpath('//*[@id="content"]/div/article/div/table//tr[3]/td[2]/text()').getall()
        content_date = content_date_raw
        # print(content_date_raw)
        # print(content_date)

        content_url = response.xpath('//*[@id="content"]/div/article/div/table//tr[3]/td[3]/a[1]/@href').getall()

        content = zip(name, content_nameversion, version, content_date, content_url)

        for name_input, nameversion_input, version_input, content_date_input, content_url_input in content:
            site_base = 'https://www.openssl.org/source/'
            release_base = 'https://www.openssl.org'
            release_strategy = response.xpath('//*[@id="content"]/div/article/div/p[2]/a[1]/@href').get()

            item = OpensslItem()
            item['name'] = name_input
            item['version'] = version_input
            item['name_version'] = '{0}-{1}'.format(item['name'], item['version'])  # get name-version
            item['download_path'] = '{0}{1}'.format(site_base, content_url_input)  # get https://..
            item['filename'] = os.path.basename(content_url_input)  # get tar.gz file
            item['content'] = '{0}{1}'.format(release_base, release_strategy)
            item['release_date'] = content_date_input
            item['bundle_name'] = re.search(r'(.+)-{0}'.format(item['version']), item['filename']).group(1)
            yield item

