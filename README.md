# minoto-python
A super-minimal Python client for [Minoto](http://minotovideo.com/) API

It should basically allow to:

  * announce a new Minoto video resource
  * upload video data (eg: MP4) to a Minoto video resource
  * get info about a Minoto video resource
  * delete a Minoto video resource

Please refer to the Minoto documentation for API details and resources model.

## Installation ##
1. Download/clone source
2. Install dependencies with `pip install -r requirements.txt`

## Usage ##
```
from minoto-python import MinotoClient

publisher_id = 'my-pub-id'
oauth_params = dict(oauth_access_token='xxx', oauth_token_secret='yyy',
                    oauth_consumer_key='zzz', oauth_consumer_secret='www')

client = MinotoClient(publisher-id, oauth_params, output_format='json')

# announce a video resource
video_properties = dict(title='title', description='description', thumbnail_uri='thumb_url',
                        tags='tag1;tag2;tag3')
resp = client.announce_video_resource(video_properties)
minoto_id = resp['minoto_id']       # ID of created video resource
upload_uri = resp['upload_uri']     # URI which you need to upload the clip to
upload_token = resp['upload_token'] # token to be attached to the clip upload

# upload a video to a video resource
client.upload_clip_to_video_resource(upload_uri, upload_token, '/path/to/video/file.mp4'):

# get info about a video resource
json_blob = client.read_video_resource(minoto_id)

# delete a video resource
client.delete_video_resource(minoto_id):
```