"""VideoBuilder module"""
import io
import multiprocessing
import os
import uuid

from PIL import Image

from Core.moviepy.Clip import Clip
from Core.moviepy.audio.AudioClip import AudioClip, CompositeAudioClip
from Core.moviepy.audio.io.AudioFileClip import AudioFileClip
from Core.moviepy.video.VideoClip import TextClip, ImageClip, ColorClip
from Core.moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from Core.moviepy.video.compositing.transitions import slide_out
from Core.moviepy.video.fx.fadeout import fadeout
from Core.moviepy.video.fx.resize import resize

from googletrans import Translator, constants

from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation


class VideoBuilder:
    """VideoBuilder class for building a video from image, text, audio and video clips"""
    progressChangeListener = None
    project_id = None

    def __init__(self):
        self.clip = None
        self.fps = 20
        self.format = "mp4"
        self.titles = []
        self.images = []
        self.audio = []
        self.width = 1920
        self.height = 1080
        self.folder = None
        os.environ["IMAGEIO_REQUEST_TIMEOUT"] = "10"
        os.environ["IMAGEMAGICK_BINARY"] = "/usr/bin/convert"
        os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
        os.environ['STABILITY_KEY'] = 'sk-vKMeP8LNyaBQHQzmAVkALkpnwJscBmS5iTWyIJtw03eLQUYO'
        self.stability_api = client.StabilityInference(
            key=os.environ['STABILITY_KEY'],  # API Key reference.
            verbose=True,  # Print debug messages.
            engine="stable-diffusion-xl-1024-v0-9",  # Set the engine to use for generation.
            # Available engines: stable-diffusion-xl-1024-v0-9 stable-diffusion-v1 stable-diffusion-v1-5 stable-diffusion-512-v2-0 stable-diffusion-768-v2-0
            # stable-diffusion-512-v2-1 stable-diffusion-768-v2-1 stable-diffusion-xl-beta-v2-2-2 stable-inpainting-v1-0 stable-inpainting-512-v2-0
        )

    def set_fps(self, fps):
        self.fps = fps

    def set_folder(self, folder):
        self.folder = folder

    def set_format(self, name_of_format):
        self.format = name_of_format

    def set_width(self, width):
        self.width = width

    def set_height(self, height):
        self.height = height

    def resize_image(self, image: Clip):
        """Resize given image to fit master resolution"""
        image = resize(image, (self.width, self.height))
        return image

    # def progressChanged(self, prog: int):
    #     self.progressChangeListener(prog, self.project_id)

    def progressChanged(self, prog: int):
        if self.progressChangeListener is not None:
            self.progressChangeListener(prog, self.project_id)
        else:
            pass

    def add_image_clip(self, image, duration):
        """
            Adding image to list of images with duration
            image - filename of image
            duration - duration in seconds
        """
        img_clip = ImageClip(img=image, duration=duration)
        self.images.append(img_clip)

    def add_image_clip(self, image_clip: Clip, transition=None):
        image_clip = self.resize_image(image_clip)
        if transition is not None:
            if(transition == "fadeout"):
                color = [255, 255, 255]
                edited_clip = fadeout(image_clip, 0.5, color)
                self.images.append(edited_clip)
            elif(transition == "slide_out"):
                edited_clip = slide_out(image_clip, 0.5, "right")
                self.images.append(edited_clip)
            elif(transition == "none"):
                self.images.append(image_clip)

        else:
            self.images.append(image_clip)

    def add_text_clip(self, text, fontsize, color, position, start, duration):
        """
                Adding titles to list of images with duration
                text - content of title
                fontsize - fontsize (for example 40)
                color - color (for example 'black')
                position - position (for example 'center')
                start - time of appear (for example 0)
                duration - duration on screen
        """
        text_clip = TextClip(text, fontsize=fontsize, color=color)
        text_clip = text_clip.set_position(position)
        text_clip = text_clip.set_duration(duration)
        text_clip = text_clip.set_start(start)
        self.titles.append(text_clip)

    def add_text_clip(self, text_clip: Clip):
        self.titles.append(text_clip)

    def add_ai_image(self, promt, start, duration):
        translator = Translator()
        translator.raise_Exception = True
        translated_text = translator.translate(promt).text
        # Set up our initial generation parameters.
        answers = self.stability_api.generate(prompt=translated_text, width=512, height=512, steps=10)

        # Set up our warning to print to the console if the adult content classifier is tripped.
        # If adult content classifier is not tripped, save generated images.
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    print(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please modify the prompt and try again.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    img.save(
                        "temp_content/" + self.folder + "/" + str(
                            artifact.seed) + ".png")  # Save our generated images with their seed number as the filename.
                    image_clip = self.resize_image(
                        ImageClip("temp_content/" + self.folder + "/" + str(artifact.seed) + ".png", duration=duration))
                    image_clip = image_clip.set_start(start)
                    self.images.append(image_clip)

    def compose_clip(self, stable_diffusion):
        """Method to compose titles, images and audio to one clip"""
        if len(self.images) == 0:
            if not stable_diffusion:
                duration = 0
                for i in self.titles:
                    duration = max(duration, i.start + i.duration)
                size = (self.width, self.height)
                self.images.append(ColorClip(size=size, duration=duration, color=[0, 0, 0]))
            else:
                for i in self.titles:
                    try:
                        self.add_ai_image("Background for text: " + i.text, i.start, i.duration)

                    except:
                        size = (self.width, self.height)
                        color_clip = ColorClip(size=size, duration=i.duration, color=[0, 0, 0])
                        color_clip = color_clip.set_start(i.start)
                        self.images.append(color_clip)

        self.clip = CompositeVideoClip(self.images + self.titles)
        self.compose_audio_to_clip()

    def add_audio_clip(self, audio: str):
        """Adding single audio to clip"""
        audio_clip = AudioFileClip(filename=audio)
        if audio_clip.duration > self.clip.duration:
            audio_clip = audio_clip.set_duration(self.clip.duration)
        self.clip = self.clip.set_audio(audio_clip)

    def add_audio_clip(self, audio_clip: AudioClip):
        self.audio.append(audio_clip)

    def compose_audio_to_clip(self):
        if len(self.audio) > 0:
            composed_audio = CompositeAudioClip(self.audio)
            if composed_audio.duration > self.clip.duration:
                composed_audio = composed_audio.set_duration(self.clip.duration)
            self.clip = self.clip.set_audio(composed_audio)

    def export(self, name):
        """Export video to file"""
        self.clip.progressChangeListener = self.progressChanged
        self.clip.write_videofile(filename="preview/" + name + "." + self.format, fps=self.fps,
                                  threads=multiprocessing.cpu_count(), audio_codec='aac',
                                  preset='ultrafast')
        os.rmdir("temp_content/" + name)
        return name + "." + self.format
