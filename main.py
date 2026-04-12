import configparser
import io
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from PIL import Image
from rich import print
import json

CONFIG_PATH = Path(__file__).with_name("setup.cfg")


def load_dir() -> str:
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config["rmus"]["root"]


def get_json_files() -> list[Path]:
    """Get all json files in the directory."""
    data_dir = Path.home() / load_dir()
    print(data_dir)
    json_files: list[Path] = []
    for file in Path(data_dir).rglob("*.json"):
        if file.is_file():
            json_files.append(file)
    return json_files


def get_mp3_files() -> list[Path]:
    """Get all mp3 files in the directory."""
    data_dir = Path.home() / load_dir()
    print(data_dir)
    mp3_files: list[Path] = []
    for file in Path(data_dir).rglob("*.mp3"):
        if file.is_file():
            mp3_files.append(file)
    return mp3_files


def extract_and_save_image(pic):
    cover = pic[0]

    # cover.data contains the raw bytes
    # cover.mime tells you if it's 'image/jpeg' or 'image/png'
    ext = "jpg" if "jpeg" in cover.mime else "png"

    with open(f"extracted_cover.{ext}", "wb") as f:
        f.write(cover.data)

    print(f"Success! Saved cover as extracted_cover.{ext}")
    print(f"Description: {cover.desc}")


def show_image(pic):
    img_data = io.BytesIO(pic.data)
    img = Image.open(img_data)
    img.show()


def read_mp3(file_path: Path):
    tag_lookup = {
        'TIT2': 'title',
        'TPE1': 'artist',
        'TALB': 'album',
        'TRCK': 'track_number',
        'TPOS': 'disc_number',
        'TBPM': 'bpm',
        'TDRC': 'date',
        'TSSE': 'encoding',
        'USLT': 'lyrics',
        'APIC:': 'album_art'
    }

    audio = MP3(str(file_path), ID3=EasyID3)
    duration: str = f"{audio.info.length:.2f}s"
    print(duration)
    tags = ID3(str(file_path))
    for key, value in tags.items():
        if key == 'APIC:':
            print(key, tag_lookup[key])
        elif key.startswith('USLT'):
            print(tag_lookup['USLT'], value)
        elif key in tag_lookup:
            print(tag_lookup[key], value)
        else:
            print(key, value)

    pic = tags.get("APIC:")
    if not pic:
        print("No album art found in this file.")
    # else:
        # extract_and_save_image(pic)
        # show_image(pic)


def read_json(file_path: Path):
    data = json.loads(file_path.read_text(encoding="utf-8"))
    print(data)


def main():
    mp3_fp = get_mp3_files()
    mp3_fp_len = len(mp3_fp)
    print(mp3_fp_len)

    json_fp = get_json_files()
    json_fp_len = len(json_fp)
    print(json_fp_len)

    for fp in mp3_fp[:1]:
        if fp.exists():
            if fp.suffix.lower() == ".mp3":
                read_mp3(fp)
    for fp in json_fp[:1]:
        if fp.exists():
            if fp.suffix.lower() == ".json":
                read_json(fp)

if __name__ == "__main__":
    main()
