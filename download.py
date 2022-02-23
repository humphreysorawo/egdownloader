#!/usr/bin/python3

import json
import os
import requests
import sys

import json_manifest

from chunk import Chunk

class Downloader:
    def __init__(self, path_to_manifest):
        manifest = Downloader.read_manifest(path_to_manifest)
        self.mf = None

        download_origin = json.loads(manifest.decode('utf-8'))['download_origin']

        self.download_urls = ['{}{}'.format(download_origin,path) \
                for path in self.get_chunk_paths(manifest)]

    def get_chunk_paths(self, manifest):
        self.mf = json_manifest.JSONManifest.read_all(manifest)
        for element in self.mf.chunk_data_list.elements:
            yield element.path

    @classmethod
    def read_manifest(cls, filename):
        if os.path.exists(filename):
            return open(filename, 'rb').read()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('python3 ./download.py manifest_file')
        sys.exit(1)

    manifest_ = sys.argv[1]
    if not os.path.exists(manifest_):
        print('[ERROR] Manifest file not found !')
        sys.exit(1)

    dw = Downloader(manifest_)
    chunks = dict()
    for i,url in enumerate(dw.download_urls):
        res = requests.get(url)
        if res.ok:
            print('[INFO] Downloaded chunk from {}'.format(url))
            c = Chunk.read_buffer(res.content)

            chunks[c.guid_num] = c.data

    if not chunks:
        print('[ERROR] No chunks were read from {}'.format(manifest_))
        sys.exit(1)

    save_dir = 'saves'
    for fm in dw.mf.file_manifest_list.elements:
        dirs, fname = os.path.split(fm.filename)
        fdir = os.path.join(save_dir, dirs)
        fpath = os.path.join(fdir, fname)

        if not os.path.exists(fdir):
            os.makedirs(fdir)

        print('[INFO] Writing {}'.format(fpath))
        with open(fpath, 'wb') as fh:
            for cp in fm.chunk_parts:
                if cp.guid_num not in chunks:
                    print('[ERROR] Chunk part is missing for {}'.format(fname))
                else:
                    fh.write(chunks[cp.guid_num][cp.offset:cp.offset + cp.size])
                    print('[INFO] Written content to {}'.format(fname))

    print('\n[INFO] Done !')
