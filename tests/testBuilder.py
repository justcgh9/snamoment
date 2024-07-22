"""VideoBuilder unit test module"""
import os.path
# import parser
import unittest
# from Core.video_builder import VideoBuilder
from Core.json_parser import JsonParser


class UploadTester(unittest.TestCase):
    """VideoBuilder unit test class"""
    def test_generation(self):
        """Testing building video from file"""
        parser1 = JsonParser()
        parser1.read_from_file("tests/test.json")
        video = parser1.parse_video('name1')
        self.assertTrue(os.path.exists('preview/' + video))

    def test_second_generation(self):
        """Testing building video from string with images and audio"""
        test = """
               {
      "title": "Test",
      "resolution": "full-hd",
      "width": 1080,
      "height": 1920,
      "transition": "slide_out",
      "fps" : 1,
      "elements":[
      {
      "type": "image",
      "src": "https://cdn.vox-cdn.com/thumbor/Ns5q9fIkrUYuauPpp3kyoY0S-Po=/0x0:4244x2824/1200x800/filters:focal(1783x1073:2461x1751)/cdn.vox-cdn.com/uploads/chorus_image/image/72031570/1246039762.0.jpg",
      "start": 0,
      "end": 5
    },
    {
      "type": "audio",
      "src": "https://od.lk/s/MTdfMzEyNDU1MDZf/afterParty.mp3",
      "start": 0,
      "end": 20
    }
  ]
    }
                    """
        parser1 = JsonParser()
        parser1.read_from_raw_json(test)
        video = parser1.parse_video('name2')
        self.assertTrue(os.path.exists('preview/' + video))

    # def test_third_generation(self):
    #     """Testing video building from string with image and text"""
    #     test = """
    #                   {
    #          "title": "Test",
    #          "resolution": "full-hd",
    #          "width": 1080,
    #          "height": 1920,
    #          "fps" : 1,
    #          "elements":[
    #           {
    #   "type": "image",
    #   "src": "https://cdn.vox-cdn.com/thumbor/Ns5q9fIkrUYuauPpp3kyoY0S-Po=/0x0:4244x2824/1200x800/filters:focal(1783x1073:2461x1751)/cdn.vox-cdn.com/uploads/chorus_image/image/72031570/1246039762.0.jpg",
    #   "start": 0,
    #   "end": 5
    # },
    #           {
    #           "type": "text",
    #           "text": "Hello world!",
    #           "start": 0,
    #           "end": 10,
    #           "fontSize":100,
    #           "position": "center",
    #           "color":"white"
    #         }
           
    #      ]
    #        }
    #                        """
    #     parser1 = JsonParser()
    #     parser1.read_from_raw_json(test)
    #     video = parser1.parse_video('name3')
    #     self.assertTrue(os.path.exists('preview/' + video))
