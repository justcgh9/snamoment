import httplib2
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
import urllib.request
import json


class YoutubeUploader:
    def __init__(self, client_secrets):
        """
        initialisation of YouTube Uploader
        :param client_secrets: file with client secret and client id
        """
        self.client_secrets = client_secrets
        self.credentials = 'credentials.json'
        client_secrets = json.load(open(client_secrets, 'r'))
        self.client_id = client_secrets.get('web').get('client_id')
        self.client_secret = client_secrets.get('web').get('client_secret')
        self.flow = None
        self.youtube = None

    def get_access(self, refresh_token):
        """
        Function that request access token for JSON2VIDEO project
        :return: access token
        """
        oauth_url = 'https://accounts.google.com/o/oauth2/token'
        data = dict(
            refresh_token=refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret,
            grant_type='refresh_token',
        )
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        request = urllib.request.Request(oauth_url, data=urllib.parse.urlencode(data).encode('utf-8'), headers=headers)
        response = json.loads(urllib.request.urlopen(request).read().decode('utf-8'))
        return response['access_token']

    def authenticate(
            self,
            refresh_token):
        """
        Function that authenticates user
        :param refresh_token: refresh token
        """
        access_token = self.get_access(refresh_token)
        cred_str = {
            "refresh_token": "{}".format(refresh_token),
            "access_token": "{}".format(access_token),
            "client_id": "{}".format(self.client_id),
            "client_secret": "{}".format(self.client_secret),
            "token_expiry": "2020-10-27T18:03:48Z",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
            "user_agent": "null",
            "revoke_uri": "https://oauth2.googleapis.com/revoke",
            "id_token": "null",
            "id_token_jwt": "null",
            "token_response": {
                "access_token": "{}".format(refresh_token),
                "expires_in": 3599,
                "scope": "https://www.googleapis.com/auth/youtube.upload",
                "token_type": "Bearer"
            },
            "scopes": [
                "https://www.googleapis.com/auth/youtube.upload"
            ],
            "token_info_uri": "https://oauth2.googleapis.com/tokeninfo",
            "invalid": "false",
            "_class": "OAuth2Credentials",
            "_module": "oauth2client.client"
        }
        with open(self.credentials, 'w') as f:
            json.dump(cred_str, f)
        self.flow = flow_from_clientsecrets(
            self.client_secrets,
            scope="https://www.googleapis.com/auth/youtube.upload",
            message='No clients secret found')
        self.credentials = Storage(self.credentials).get()
        self.youtube = build("youtube", "v3", http=self.credentials.authorize(httplib2.Http()))

    def upload(self, data, chunksize=(-1)):
        """
        Function that uploads video
        :param data: data of the video
        :param chunksize: chunksize
        :return: link to YouTube video
        """
        body = {
            'snippet': {
                'title': data.get('title', 'Test Title'),
                'description': data.get('description', 'Test Description'),
                'tags': data.get('tags', []),
            },
            'status': {
                'privacyStatus': data.get('privacyStatus', 'public'),
                'selfDeclaredMadeForKids': data.get('kids', False)
            }
        }
        insert_request = self.youtube.videos().insert(
            part=",".join(
                list(body.keys())), body=body, media_body=MediaFileUpload(data.get('filepath'),
                                                                          chunksize=chunksize, resumable=True))
        response = None
        video_id = ''
        while response is None:
            try:
                response = insert_request.next_chunk()[1]
                if 'id' in response:
                    video_id = response.get('id')
                    response = True
                else:
                    raise Exception(f'Unexpected response: {response}')
            except Exception as e:
                return e
        return 'https://www.youtube.com/watch?v=' + video_id
