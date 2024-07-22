"""Module for reading JSON and converting it to video"""
import json
import shutil
import os

from arabic_reshaper import arabic_reshaper
from bidi.algorithm import get_display

from Core.moviepy.Clip import Clip
from Core.moviepy.audio.io.AudioFileClip import AudioFileClip

from Core.video_builder import VideoBuilder
from Core.moviepy.video.VideoClip import VideoClip, ImageClip, TextClip
import requests
import uuid

DEFAULT_FONT_SIZE = 50
DEFAULT_TEXT_COLOR = "white"
DEFAULT_TEXT_POSITION = "center"
DEFAULT_TRANSITION = "none"
DEFAULT_FPS = 1
DEFAULT_STABLE_DIFFUSION = False


class JsonParser:
    """JSON to video converter class"""
    raw_parsed_dict = {}
    raw_json_string = ""
    progressChangeListener = None

    def read_from_raw_json(self, raw_json_string: str):
        """Reads JSON from string"""
        self.raw_json_string = raw_json_string
        self.raw_parsed_dict = json.loads(raw_json_string)

    def read_from_file(self, file_name: str):
        """Reads JSON from file"""
        with open(file_name, mode="r") as file:
            self.raw_parsed_dict = json.load(file)

    def parse_video(self, video_id, quality="720p", video_format="mp4"):
        """Parses JSON and builds video using VideoBuilder"""
        video_builder: VideoBuilder = VideoBuilder()
        video_builder.project_id = video_id
        video_builder.progressChangeListener = self.progressChangeListener
        video_builder.set_format(video_format)
        video_builder.set_width(self.raw_parsed_dict['width'])
        video_builder.set_height(self.raw_parsed_dict['height'])
        video_builder.set_fps(DEFAULT_FPS if 'fps' not in self.raw_parsed_dict else
                              self.raw_parsed_dict['fps'])
        video_builder.set_folder(str(video_id))
        if not os.path.exists("temp_content/"):
            os.mkdir("temp_content/")

        if os.path.exists("temp_content/" + str(video_id)):
            shutil.rmtree("temp_content/" + str(video_id))

        os.mkdir("temp_content/" + str(video_id))
        elements, transitions = self.parse_elements(self.raw_parsed_dict['elements'], video_id)
        index_of_image = 0
        for element in elements:
            if element is VideoClip:
                pass
            elif type(element) is ImageClip:
                video_builder.add_image_clip(element, transitions[index_of_image])
                index_of_image += 1
            elif type(element) is TextClip:
                video_builder.add_text_clip(element)
            elif type(element) is AudioFileClip:
                video_builder.add_audio_clip(element)

        stable_diffusion = DEFAULT_STABLE_DIFFUSION if 'ai' not in self.raw_parsed_dict else self.raw_parsed_dict[
            'ai']
        video_builder.compose_clip(stable_diffusion=stable_diffusion)
        return video_builder.export(video_id)

    def parse_elements(self, elements: list, video_id) -> list:
        """Parses JSON video elements"""
        res_elements = []
        transitions = []
        for element in elements:
            new_element: Clip
            type_ = element['type']
            start = element['start']
            end = element['end']

            color = DEFAULT_TEXT_COLOR if 'color' not in element else element['color']
            position = DEFAULT_TEXT_POSITION if 'position' not in element else element['position']

            if type_ == "video":
                pass
            elif type_ == "text":
                parsed_text = element['text']
                font_size = DEFAULT_FONT_SIZE if 'fontSize' not in element else element['fontSize']
                count_of_symbols = 0
                for i in range(len(parsed_text)):
                    if parsed_text[i] != ' ':
                        count_of_symbols += 1
                    else:
                        count_of_symbols = 0
                    if count_of_symbols > 20:
                        parsed_text = parsed_text[:i] + "- " + parsed_text[i:]
                        count_of_symbols = 0
                reshaped_text = arabic_reshaper.reshape(parsed_text)  # correct its shape
                bidi_text = get_display(reshaped_text)
                if len(bidi_text) > 80:
                    new_element = TextClip(bidi_text, fontsize=font_size,
                                           color=color, font="Arial", method="caption")
                else:
                    new_element = TextClip(bidi_text, fontsize=font_size,
                                           color=color, font="Arial")
                new_element = new_element.set_start(start)
                new_element = new_element.set_end(end)
                new_element = new_element.set_position(position)
            elif type_ == "image":
                new_element = ImageClip(element['src'], duration=end - start)
                new_element = new_element.set_start(start)
                new_element = new_element.set_position(position)
                if 'transition' in element:
                    transitions.append(element['transition'])
                else:
                    transitions.append(DEFAULT_TRANSITION)
            elif type_ == "audio":
                try:
                    new_element = AudioFileClip(filename=element["src"])
                except:
                    response = requests.get(element['src'])
                    filename = "temp_content/" + str(video_id) + "/" + uuid.uuid4().hex + ".mp3"
                    file = open(filename, "wb")
                    file.write(response.content)
                    new_element = AudioFileClip(filename=filename)
                    file.close()
                    os.remove(file.name)

                new_element = new_element.set_start(start)
                new_element = new_element.set_end(end)
                new_element = new_element.set_duration(end - start)
            res_elements.append(new_element)
        return res_elements, transitions
