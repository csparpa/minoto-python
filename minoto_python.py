# -*- coding: utf-8 -*-
import os
import time
import random
import string
import json
import requests
from requests_toolbelt import MultipartEncoder


class MinotoClient():

    VIDEOS_ENDPOINT = 'https://api.minoto-video.com/publishers/%s/videos'
    VIDEO_URL = VIDEOS_ENDPOINT+'/%s'
    SEARCH_BY_TITLE_URL = VIDEOS_ENDPOINT+'?search=%s&searchfields=title'

    def __init__(self, publisher_id, oauth_params, output_format='json'):
        self.publisher_id = publisher_id
        self.oauth_access_token = oauth_params['oauth_access_token']
        self.oauth_token_secret = oauth_params['oauth_token_secret']
        self.oauth_consumer_key = oauth_params['oauth_consumer_key']
        self.oauth_consumer_secret = oauth_params['oauth_consumer_secret']
        self.oauth_version = '1.0'
        self.output_format = output_format

    @staticmethod
    def _generate_timestamp():
        return int(time.time())

    @staticmethod
    def _generate_nonce(length=9):
        return ''.join(random.choice(string.ascii_uppercase + \
                 string.ascii_lowercase + string.digits) for _ in range(length))

    def _oauth_plain_text_params(self):
        timestamp = MinotoClient._generate_timestamp()
        nonce = MinotoClient._generate_nonce(9)
        oauth_signature_method = 'PLAINTEXT'
        return dict(oauth_consumer_key=self.oauth_consumer_key,
                    oauth_nonce=nonce,
                    oauth_signature_method=oauth_signature_method,
                    oauth_timestamp=timestamp,
                    oauth_token=self.oauth_access_token,
                    oauth_version=self.oauth_version,
                    output_format=self.output_format,
                    oauth_signature=self.oauth_consumer_secret+'&'+ \
                        self.oauth_token_secret)

    def announce_video_resource(self, video_properties):
        announcement_url = self.VIDEOS_ENDPOINT % (self.publisher_id,)
        params = self._oauth_plain_text_params()
        resp = requests.post(announcement_url, params=params,
                             headers={'Content-Type': 'application/json'},
                             data=json.dumps(video_properties))
        video = resp.json()
        if not resp.status_code == 200 or not video['status'] == 'announced':
            raise Exception('Impossible to announce video - Minoto API status code: %s' % (resp.status_code,))
        return dict(minoto_id=video['id'], upload_uri=video['upload_uri'], upload_token=video['upload_token'])

    def upload_clip_to_video_resource(self, upload_uri, upload_token, path_to_video):
        filename = os.path.basename(path_to_video).split('.')[0]
        m = MultipartEncoder(fields={'UPLOAD_IDENTIFIER': upload_token,
                                     'video': (filename, open(path_to_video, 'rb'), 'application/octet-stream')})
        resp = requests.post(upload_uri, data=m, headers={'Content-Type': m.content_type})
        if not resp.status_code == 200:
            raise Exception('Impossible to upload video - Minoto API status code: %s' % (resp.status_code,))

    def read_video_resource(self, minoto_id):
        url = self.VIDEO_URL % (self.publisher_id, minoto_id)
        params = self._oauth_plain_text_params()
        resp = requests.get(url, params=params)
        if resp.status_code == 404:  # not found
            return None
        if resp.status_code != 200:
            raise Exception('Error in reading video %s - Minoto API status code: %s' % (minoto_id, resp.status_code,))
        return resp.json()

    def delete_video_resource(self, minoto_id):
        url = self.VIDEO_URL % (self.publisher_id, minoto_id)
        params = self._oauth_plain_text_params()
        resp = requests.delete(url, params=params)
        if not resp.status_code == 204:
            raise Exception('Impossible to remove video %s - Minoto API status code: %s' % (minoto_id, resp.status_code))

    def search_video_resource_by_title(self, title):
        url = self.SEARCH_BY_TITLE_URL % (self.publisher_id, title)
        params = self._oauth_plain_text_params()
        resp = requests.get(url, params=params)
        if resp.status_code == 404:  # not found
            return None
        if not resp.status_code == 200:
            raise Exception('Error in search - Minoto API status code: %s' % (resp.status_code,))
        return resp.json()