#!/usr/bin/python3

import requests
from requests.auth import HTTPBasicAuth
import json
import os
import argparse

class EpicGamesLauncher:
    def __init__(self, user_basic, pass_basic):
        # Set the Launcher User Agent
        self.user_agent = 'UELauncher/10.13.1-11497744+++Portal+Release-Live Windows/10.0.18363.1.256.64bit'
        self.oauth_host = 'account-public-service-prod03.ol.epicgames.com'
        self.launcher_host = 'launcher-public-service-prod06.ol.epicgames.com'

        self.session = requests.Session()
        self.session.headers['User-Agent'] = self.user_agent
        self.oauth_basic = HTTPBasicAuth(user_basic, pass_basic)

        self.user = None
        self.items = []

    def start_session(self, refresh_token):
        body = {
            'grant_type':'refresh_token',
            'refresh_token': refresh_token,
            'token_type': 'eg1'
        }

        res = self.session.post('https://' + self.oauth_host + \
                '/account/api/oauth/token',data=body, auth=self.oauth_basic)
        if res.ok:
           print('[INFO] Retrieved access token')
           self.user = json.loads(res.text)

           self.session.headers['Authorization'] = 'Bearer {}'.format(self.user['access_token'])
        else:
            print('[ERROR] Could not retrieve access token')
            exit(1)

    def fetch_library_items(self):
        res = self.session.get('https://' + self.launcher_host + '/launcher/api/public/assets/Windows')
        if res.ok:
            print('[INFO] Retrieved items in UnrealEngine library')
            self.items = json.loads(res.text)
        else:
            print(res.text)
    def fetch_item_manifest(self, catalog_id, namespace, appname):
        res = self.session.get('https://{}/launcher/api/public/assets/v2/platform/Windows/namespace/{}/catalogItem/' \
                '{}/app/{}/label/Live'.format(self.launcher_host, namespace, catalog_id, appname))

        return json.loads(res.text)

    def fetch_download_metadata(self, manifest):
        manifest_data = manifest['elements']
        for element in manifest_data:
            for manifest in element['manifests']:
                if 'queryParams' in manifest:
                    params = '&'.join('{}={}'.format(p['name'], p['value']) \
                            for p in manifest['queryParams'])
                    manifest['uri'] = '?'.join((manifest['uri'], params))
                res = self.session.get(manifest['uri'])
                if res.ok:
                    # print('[INFO] Failed for {} .....'.format(manifest['uri']))
                    continue

        return manifest_data

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True)

    args = parser.parse_args()
    if os.path.exists(args.config):
        config = json.load(open(args.config, 'r'))
        if config.get('refresh_token') and config.get('username') and config.get('password'):
            print('[INFO] Loaded user credentials correctly')
        else:
            print('[ERROR] Missing (refresh_token, username, password)')
            exit(1)

        eg = EpicGamesLauncher(config['username'], config['password'])
        eg.start_session(config['refresh_token'])

        # update refresh token
        config['refresh_token'] = eg.user['refresh_token']
        json.dump(config, open(args.config, 'w'), indent=6)

        eg.fetch_library_items()
        eg.items = [item for item in eg.items if item['assetId'] != 'UE']

        print('[INFO] Apps in Library\n')

        for item in eg.items:
            manifest = eg.fetch_item_manifest(item['catalogItemId'], item['namespace'], item['appName'])

            data = eg.fetch_download_metadata(manifest)
            res = requests.get(data[0]['manifests'][0]['uri'])

            if res.ok:
                mfile = json.loads(res.text)
                print('App Name: ', mfile['AppNameString'])
                print('Manifest Version: ', mfile['ManifestFileVersion'])
                print('--------')
