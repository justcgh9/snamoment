"""YouTube uploader unit test module"""
import unittest
from Core.youtube import Uploader


def upload(path, title, description, tags):
    uploader = Uploader('Core/client_secrets.json', 'Core/credentials.storage')
    video = uploader.upload(path, title, description, tags)
    return video


class UploadTester(unittest.TestCase):
    """YouTube uploader unit test class"""
    def test_generated(self):
        self.assertTrue(upload('Core/video.mp4', 'title1', 'description1',
                               []).startswith('https://www.youtube.com/watch?v='))

    def test_local(self):
        self.assertTrue(upload('Core/video_2023-06-23_13-04-57.mp4', 'title1', 'description1', [])
                        .startswith('https://www.youtube.com/watch?v='))
