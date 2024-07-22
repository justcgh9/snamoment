import pyttsx3


class TextToSpeech:
    @staticmethod
    def convert(text, filepath):
        """
        converts the string to text
        :param text: string that will be converted
        :param filepath: path where audio will be saved
        :return:
        """
        string = text
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print(voices)
        engine.setProperty('voice', voices[0].id)
        engine.setProperty('voice', 4)
        engine.save_to_file(string, filepath)
        engine.runAndWait()
        f = open('speech.mp3', 'r')
        return f
