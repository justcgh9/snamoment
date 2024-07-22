"""JSON parser unit test module"""
import unittest
from Core.json_parser import JsonParser
from Core.moviepy.video.VideoClip import TextClip


class TestParser(unittest.TestCase):
    """JSON parser unit test class"""

    def test_text(self):
        """Testing parsing from string"""
        input_string = """
        {
          "title": "SecondVideo",
          "resolution": "full-hd",
          "width": 1920,
          "height": 1080,
          "transition": "fadeout",
          "fps": 20,
          "elements": [
            {
              "type": "text",
              "text": "Hello world!",
              "start": 0,
              "end": 10,
              "fontSize":100,
              "position": "center",
              "color":"white"
            }
          ]
        }
        """
        parser = JsonParser()
        parser.read_from_raw_json(input_string)
        element: TextClip = parser.parse_elements(parser.raw_parsed_dict['elements'], 123)[0][0]

        correct_result: TextClip = TextClip("Hello world!", fontsize=100, color="white")
        correct_result = correct_result.set_start(0)
        correct_result = correct_result.set_end(10)
        correct_result = correct_result.set_position("center")

        self.assertEqual(element.duration, correct_result.duration)
        self.assertEqual(element.color, correct_result.color)
