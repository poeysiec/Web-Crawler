import scrapy
import re
import os
from cmake.items import CmakeItem


class CmakeSpider(scrapy.Spider):
    name = 'cmake'
    allowed_domains = ['cmake.org/download']
    start_urls = ['https://cmake.org/download/']

    def parse(self, response):

        print('Processing Cmake - accessing {0}'.format(response.url))

        target_frame = response.xpath('//*[@id="et-boc"]/div/div/div/div[2]/div/div/div/h3[contains(text(),"Latest Release")]')
        version = target_frame.xpath('.//text()').re(r'Release (.+)')[0].strip('()')
        release_notes = target_frame.xpath('.//following-sibling::p/a/@href').get()
        download_path = target_frame.xpath('.//following-sibling::table[1]/tbody/tr/td/a[contains(text(),".tar.gz")]/@href').get()

        item = CmakeItem()
        item['name'] = 'cmake'
        item['version'] = version
        item['name_version'] = '{0}-{1}'.format('cmake', item['version'])
        item['release_date'] = 'none'
        item['content'] = response.urljoin(release_notes)
        item['download_path'] = download_path
        item['filename'] = os.path.basename(download_path)
        item['bundle_name'] = re.search(r'(.+)-{0}'.format(item['version']), item['filename']).group(1)

        yield item