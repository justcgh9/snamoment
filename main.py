import shutil

from Core.json_parser import JsonParser

if __name__ == "__main__":
    parser = JsonParser()
    parser.read_from_file("second.json")
    parser.parse_video("name")

