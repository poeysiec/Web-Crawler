import scrapy
import re
import os
from curl.items import CurlItem


class CurlSpider(scrapy.Spider):
    name = 'curl'
    # allowed_domains = ['curl.se/download.html']
    start_urls = ['http://curl.se/download.html']

    def parse(self, response):

        print('Processing Curl - accessing {0}'.format(response.url))

        site_base = 'https://curl.se'

        download_link = response.xpath("//table[@class='download']//td/a[contains(text(),'tar.gz')]/@href").getall()
        download_path = '{0}{1}'.format(site_base, download_link[0])
        filename = os.path.basename(download_path)
        version = (filename.split('-')[1])[0:6]

        changelog = response.xpath("//div[@class='relatedbox']//a[1]/@href").getall()
        changelog_path = '{0}{1}'.format(site_base, changelog[0])

        yield scrapy.Request(url=changelog_path, callback=self.parse_changelog, meta={
            'download_path': download_path,
            'filename': filename,
            'version': version,
            'changelog_path': changelog_path
        }, dont_filter=True)

    def parse_changelog(self, response):
        version = response.meta['version']
        changelog_title = response.xpath(f"//h2[contains(text(),'{version}')]").getall()
        changelog_title = ''.join([str(title) for title in changelog_title])
        release_date = changelog_title.split('-')[1]
        changelog_content = response.xpath(
            f"//h2[contains(text(),'{version}')]//following-sibling::ul[@class='changes'][1]/li").getall()
        changelog_content = ''.join([str(content) for content in changelog_content])

        print(changelog_title + '\n' + release_date)

        item = CurlItem()
        item['name'] = 'curl'
        item['download_path'] = response.meta['download_path']  # get https://..
        item['filename'] = response.meta['filename']  # get tar.gz file
        item['version'] = response.meta['version']
        item['name_version'] = '{0}-{1}'.format(item['name'], item['version'])  # get name-version
        item['release_date'] = release_date
        item['content'] = changelog_title + changelog_content
        item['bundle_name'] = re.search(r'(.+)-{0}'.format(item['version']), item['filename']).group(1)
        yield item

