import scrapy
import re
import os
from krb5.items import Krb5Item


class Krb5Spider(scrapy.Spider):
    name = 'krb5'
    # allowed_domains = ['web.mit.edu/kerberos/']
    start_urls = ['https://kerberos.org/dist/index.html']

    def parse(self, response):

        print('Processing Kerberos - accessing {0}'.format(response.url))

        version = response.xpath("//ul[2]/li/a[contains(text(),'current release') and (not(contains(text(),'Windows')))]").re(r'Release (.+) -')
        name = response.xpath('//ul/li[1]/a[contains(@href,"krb5")]/text()').re(r'(.+)-')
        release_date = response.xpath('//h2/a[contains(text(),"current")]').re(r'\((.+)\)')
        content_url = response.xpath('//ul/li[1]/a[contains(@href,"krb5")]/@href').getall()

        yield scrapy.Request(response.url, callback=self.parse_version_page, meta={
            'name': name,
            'version': version,
            'release_date': release_date,
            'content_url': content_url
        }, dont_filter=True)

    def parse_version_page(self, response):
        name = response.meta['name'][0]
        version = response.meta['version'][0]
        version_base = version[0:4]
        content_url = response.meta['content_url']
        release_date = response.meta['release_date']

        content_base = 'https://web.mit.edu/kerberos/'
        changes_content_url = '{0}{1}-{2}/{3}-{4}.html'.format(content_base, name, version_base, name, version)

        yield scrapy.Request(url=changes_content_url, callback=self.parse_release_page, meta={
            'version': version,
            'content_url': content_url,
            'release_date': release_date
        }, dont_filter=True)

    def parse_release_page(self, response):
        version = response.meta['version']
        site_base = 'https://kerberos.org/dist/'

        release_date = response.xpath(f"//h2[contains(text(),'Major') and (contains(text(),'{version}'))]").re(
            r'\((.+)\)')
        changes_title = response.xpath(f"//h2[contains(text(),'Major') and (contains(text(),'{version}'))]").getall()
        changes_title = ''.join([str(title) for title in changes_title])
        change_content = response.xpath(
            f"//h2[contains(text(),'Major') and (contains(text(),'{version}'))]/following-sibling::ul").getall()
        change_content = ''.join([str(content) for content in change_content])

        content_url = response.meta['content_url'][0]

        item = Krb5Item()
        item['name'] = 'krb5'
        item['version'] = version
        item['name_version'] = '{0}-{1}'.format(item['name'], item['version'])  # get name-version
        item['release_date'] = release_date[0]
        item['content'] = changes_title + change_content
        item['download_path'] = '{0}{1}'.format(site_base, content_url)  # get https://..
        item['filename'] = os.path.basename(content_url)  # get tar.gz file
        item['bundle_name'] = re.search(r'(.+)-{0}'.format(item['version']), item['filename']).group(1)
        yield item


