#!/usr/bin/python3

import json
import os
import requests

import json_manifest

class Downloader:
    def __init__(self):
        manifest = self.read_manifest('manifests/manifest4.json')
        download_origin = json.loads(manifest.decode('utf-8'))['download_origin']

        self.download_urls = ['{}{}'.format(download_origin,path) \
                for path in self.get_chunk_paths(manifest)]

    def get_chunk_paths(self, manifest):
        mf = json_manifest.JSONManifest.read_all(manifest)
        for element in mf.chunk_data_list.elements:
            yield element.path

    def read_manifest(self, filename):
        if os.path.exists(filename):
            return open(filename, 'rb').read()

if __name__ == '__main__':
    dw = Downloader()
    for url in dw.download_urls:
        print(url)
        
