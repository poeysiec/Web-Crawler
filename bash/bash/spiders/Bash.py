import scrapy
import re
import os
from bash.items import BashItem


class BashSpider(scrapy.Spider):
    name = 'bash'
    # allowed_domains = ['ftp.gnu.org/gnu/bash']
    start_urls = ['http://ftp.gnu.org/gnu/bash/']

    def parse(self, response):

        print('Processing Bash - accessing {0}'.format(response.url))

        site_base = 'https://ftp.gnu.org/gnu/bash'

        filename = response.xpath("//tr/td/a[contains(@href,'tar.gz') and not (contains(@href,'sig')) and not (contains(@href,'beta')) and not (contains(@href,'alpha')) and not (contains(@href,'rc')) and not (contains(@href,'doc')) and not (contains(@href,'readline'))]/@href").getall()[-1]
        version = response.xpath("//tr/td/a[contains(@href,'tar.gz') and not (contains(@href,'sig')) and not (contains(@href,'beta')) and not (contains(@href,'alpha')) and not (contains(@href,'rc')) and not (contains(@href,'doc')) and not (contains(@href,'readline'))]/@href").re(r'bash-(.+).tar.gz')[-1]
        release_date = response.xpath("//tr/td/a[contains(@href,'tar.gz') and not (contains(@href,'sig')) and not (contains(@href,'beta')) and not (contains(@href,'alpha')) and not (contains(@href,'rc')) and not (contains(@href,'doc')) and not (contains(@href,'readline'))]/parent::td/parent::tr/td[3]/text()").getall()[-1]
        release_date = release_date.split(' ')[0]
        download_path = f'{site_base}/{filename}'

        item = BashItem()
        item['name'] = 'bash'
        item['version'] = version
        item['download_path'] = download_path
        item['filename'] = filename
        item['name_version'] = '{0}-{1}'.format(item['name'], item['version'])
        item['release_date'] = release_date
        item['content'] = 'none'
        item['bundle_name'] = re.search(r'(.+)-{0}'.format(item['version']), item['filename']).group(1)
        yield item
