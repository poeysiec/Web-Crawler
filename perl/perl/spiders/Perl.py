import scrapy
import re
import os
from perl.items import PerlItem


class PerlSpider(scrapy.Spider):
    name = 'perl'
    # allowed_domains = ['www.cpan.org/src']
    start_urls = ['http://www.cpan.org/src/']

    def parse(self, response):

        print('Processing Perl - accessing {0}'.format(response.url))

        target_frame = response.xpath('//*[@id="content"]/table[1]//tr[@class="latest"]')

        target_version = target_frame.xpath('.//td[2]/text()').getall()
        release_type = target_frame.xpath('.//td[3]/text()').getall()
        release_date = target_frame.xpath('.//td[4]/text()').getall()
        download_url = target_frame.xpath('.//td[5]/a/@href').getall()

        content = zip(target_version, release_type, release_date, download_url)

        for target_version_input, release_type_input, release_date_input, download_url_input in content:
            content_base = 'https://metacpan.org/pod/perldelta'
            yield scrapy.Request(content_base, callback=self.parse_content_page, meta={
                'target_version': target_version_input,
                'release_type': release_type_input,
                'release_date': release_date_input,
                'download_url': download_url_input
            })

    def parse_content_page(self, response):

        new_title = response.xpath('//*[@id="New-Modules-and-Pragmata"]').get()
        new_frame_content = response.xpath('//div[1]/div[2]/div/div[3]/div/ul[3]')
        new_content = new_frame_content.xpath('.//following-sibling::li/p').getall()
        updated_title = response.xpath('//*[@id="Updated-Modules-and-Pragmata"]').get()
        updated_frame_content = response.xpath('//div[1]/div[2]/div/div[3]/div/ul[4]')
        updated_content = updated_frame_content.xpath('.//following-sibling::li/p').getall()

        new_content = '\n'.join([str(content) for content in new_content])
        updated_content = '\n'.join([str(content) for content in updated_content])

        item = PerlItem()
        item['name'] = 'perl'
        item['version'] = response.meta['target_version'].split('\n')[0]
        item['name_version'] = '{0}-{1}'.format(item['name'],item['version'])    # get name-version
        item['release_date'] = response.meta['release_date']
        item['download_path'] = response.meta['download_url']                              # get https://..
        item['filename'] = os.path.basename(response.meta['download_url'])                 # get tar.gz file
        item['content'] = '\n' + new_title + new_content + '\n' + updated_title + updated_content
        item['bundle_name'] = re.search(r'(.+)-{0}'.format(item['version']), item['filename']).group(1)
        yield item

