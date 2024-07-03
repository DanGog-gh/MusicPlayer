from mutagen.mp3 import MP3


def get_mp3_metadata(mp3_file):
    """
    Метод возвращает из трека название альбома, имя атриста и название
    трека
    """

    metadata = {
        "title": "Unknown",  # название трека
        "artist": "Unknown",  # название группы/исполнителя
        "album": "Unknown",  # название альбома
        "track": "Unknown",
    }

    try:
        audio = MP3(mp3_file)
        if "TIT2" in audio:
            metadata["title"] = audio["TIT2"].text[0]
        if "TPE1" in audio:
            metadata["artist"] = audio["TPE1"].text[0]
        if "TALB" in audio:
            metadata["album"] = audio["TALB"].text[0]
        if "TRCK" in audio:
            metadata["track"] = audio["TRCK"].text[0]

        return metadata
    except Exception as e:
        return metadata
