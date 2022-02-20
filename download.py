#!/usr/bin/python3

import json
import os

import json_manifest

class Downloader:
    def __init__(self):
        manifest = self.read_manifest('manifests/manifest4.json')
        self.paths = self.get_chunk_paths(manifest)

    def get_chunk_paths(self, manifest):
        mf = json_manifest.JSONManifest.read_all(manifest)
        for element in mf.chunk_data_list.elements:
            yield element.path

    def read_manifest(self, filename):
        if os.path.exists(filename):
            return open(filename, 'rb').read()

if __name__ == '__main__':
    dw = Downloader()
    for path in dw.paths:
        print(path)
