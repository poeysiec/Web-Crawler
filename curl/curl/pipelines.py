# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import os
import requests
import logging


class CurlPipeline:
    latest_filename = 'latest'

    def process_item(self, item, spider):

        print("Processing " + item['filename'])
        filename = item['filename'] + '.json'

        json_content = dict()
        json_content['name'] = item['name']
        json_content['version'] = item['version']
        json_content['name_version'] = item['name_version']
        json_content['release_date'] = item['release_date']
        json_content['download_path'] = item['download_path']
        json_content['filename'] = item['filename']
        json_content['update_details'] = item['content']

        with open(filename, 'w') as file:
            json.dump(json_content, file)       # converts a Python object into a json string
        self.download_package(item['download_path'])
        return item

    @staticmethod
    def download_package(url_input):
        basename = os.path.basename(url_input)

        if os.path.exists(basename) is False:
            with requests.get(url_input, stream=True) as r:
                r.raise_for_status()
                logging.info('Downloading {0}'.format(url_input))
                print('Downloading {0}'.format(url_input))
                with open(basename, 'wb') as f_download:
                    for chunk in r.iter_content(chunk_size=8192):
                        f_download.write(chunk)
        else:
            logging.info("File {0} exists, skip download...".format(basename))
            print("File {0} exists, skip download...".format(basename))
