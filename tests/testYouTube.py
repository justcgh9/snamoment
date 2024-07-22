"""YouTube uploader unit test module"""
import unittest
from Core.youtube import YoutubeUploader


class UploadTester(unittest.TestCase):
    """YouTube uploader unit test class"""
    pass
    # def testGenerated(self):
    #     uploader = Uploader('Core/client_secrets.json', 'Core/credentials.storage')
    #     video = uploader.upload('tests/video.mp4', 'title1', 'description1', [])
    #
    #     self.assertTrue(video.startswith('https://www.youtube.com/watch?v=') or
    #                     video.startswith('The quota'))
    #
    # def testLocal(self):
    #     uploader = Uploader('Core/client_secrets.json', 'Core/credentials.storage')
    #     video = uploader.upload('tests/video_2023-06-23_13-04-57.mp4',
    #                             'title1', 'description1', [])
    #
    #     self.assertTrue(video.startswith('https://www.youtube.com/watch?v=') or
    #                     video.startswith('The quota'))

    # def testLocal(self):
    #     uploader = Uploader('Core/credentials.storage', 'Core/client_secrets.json')
    #     video = uploader.upload('tests/video_2023-06-23_13-04-57.mp4',
    #                             'title1', 'description1', [])
    #     vid = upload('tests/video_2023-06-23_13-04-57.mp4', 'title1', 'description1', [])
    #     self.assertTrue(vid.startswith('https://www.youtube.com/watch?v=') or
    #                     vid.startswith('The quota'))
