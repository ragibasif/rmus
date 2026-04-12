import configparser
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from rich import print

CONFIG_PATH = Path(__file__).with_name("setup.cfg")


def load_music_dir() -> str:
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config["rmus"]["music_dir"]


def get_music_files() -> list[Path]:
    """Get all music files in the music directory."""
    music_dir = load_music_dir()
    music_files: list[Path] = []
    for file in Path(music_dir).glob("*.mp3"):
        if file.is_file():
            music_files.append(file)
    return music_files


def read_file_tags(file_path: Path):
    if file_path.exists() and file_path.suffix.lower() == ".mp3":
        audio = MP3(str(file_path),ID3=EasyID3)
        duration: str = f"{audio.info.length:.2f}s"
        print(duration)
        tags = ID3(str(file_path))
        print(list(tags.keys()))


def main():
    music_files = get_music_files()
    print(music_files)
    for f in music_files:
        read_file_tags(f)


if __name__ == "__main__":
    main()
