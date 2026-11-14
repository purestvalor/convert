"""
yt to mp3/mp4 converter
takes a yt link nd downloads the audio (mp3) or video (mp4).
"""

import os
import shutil
import subprocess
from pathlib import Path

# CHANGE DEFAULT MP3 FOLDER HERE
DEFAULT_MP3_DIR = str(Path.home() / "Downloads")

# CHANGE DEFAULT MP4 FOLDER HERE
DEFAULT_MP4_DIR = str(Path.home() / "Downloads")


def sanitize(name: str) -> str:
    return "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in name[:50])


def find_ffmpeg():
    """local ./bin first, then PATH, then pip bundled (imageio-ffmpeg)"""
    for name in ("ffmpeg.exe", "ffmpeg"):
        local = Path("./bin") / name
        if local.exists():
            return str(local)
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return None


def download_youtube_audio(
    url: str,
    output_dir: str = "./downloads",
    custom_name: str = "",
    is_mp4: bool = False,
):
    """
    makes yt link into mp3 or mp4

    Args:
        url (str): the yt url
        output_dir (str): dir to save file
        custom_name (str): custom filename if provided
        is_mp4 (bool): True = MP4 (video+audio), False = MP3

    Returns:
        str: path to file, or None if failed
    """

    try:
        import yt_dlp
    except ImportError:
        print("u dont got yt-dlp")
        print("open terminal nd run this  pip install yt-dlp")
        return None

    os.makedirs(output_dir, exist_ok=True)
    ext = "mp4" if is_mp4 else "mp3"

    base_opts = {"quiet": False, "no_warnings": True}
    ffmpeg = find_ffmpeg()
    if ffmpeg:
        base_opts["ffmpeg_location"] = ffmpeg

    try:
        print(f"here comes the {ext}..!: {url}")

        # get title first
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as probe:
            info = probe.extract_info(url, download=False)
        title = info.get("title", "untitled")

        safe_title = sanitize(custom_name or title)
        output_path = Path(output_dir) / f"{safe_title}.{ext}"
        outtmpl = str(Path(output_dir) / f"{safe_title}.%(ext)s")

        if is_mp4:
            ydl_opts = {
                **base_opts,
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "outtmpl": outtmpl,
                "merge_output_format": "mp4",
            }
        else:
            ydl_opts = {
                **base_opts,
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        print(f"ur {ext} is saved here: {output_path}")
        return str(output_path)
    except Exception as e:
        print(f"error downloading from yt, srrry..: {e}")
        return None


AUDIO_VIDEO_EXTS = {
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".wmv", ".m4v",
    ".wav", ".flac", ".m4a", ".aac", ".ogg", ".opus", ".wma", ".mp3",
}


def convert_to_mp3(src: str, output_dir: str, custom_name: str = ""):
    """
    converts a local audio/video file to mp3

    Returns:
        str: path to mp3, or None if failed
    """
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        print("ffmpeg not found. run: pip install imageio-ffmpeg")
        return None

    src_path = Path(src)
    if not src_path.is_file():
        print(f"file not found: {src}")
        return None

    os.makedirs(output_dir, exist_ok=True)
    out_path = Path(output_dir) / f"{sanitize(custom_name or src_path.stem)}.mp3"

    cmd = [
        ffmpeg, "-y", "-i", str(src_path),
        "-vn", "-codec:a", "libmp3lame", "-b:a", "192k",
        str(out_path),
    ]

    try:
        print(f"converting: {src_path.name}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ffmpeg failed: {result.stderr[-500:]}")
            return None
        print(f"ur mp3 is saved here: {out_path}")
        return str(out_path)
    except Exception as e:
        print(f"error converting file, srrry..: {e}")
        return None


def clean_path(raw: str) -> str:
    """drag-drop into terminal adds quotes"""
    return raw.strip().strip('"').strip("'")


def local_mode():
    """convert a file or a whole folder to mp3"""
    raw = input("\ndrag a file or folder here (or paste the path)\n> ")
    path = Path(clean_path(raw))

    if not path.exists():
        print("that path doesnt exist")
        return

    default_dir = DEFAULT_MP3_DIR
    user_dir = input(f"\nwhere do u wanna dump the mp3? (default: {default_dir})\n> ").strip() or default_dir
    print()

    if path.is_file():
        custom_name = input("what do u wanna name the file? (blank - default same name)\n> ").strip()
        print()
        convert_to_mp3(str(path), user_dir, custom_name)
        return

    files = sorted(
        f for f in path.iterdir()
        if f.is_file() and f.suffix.lower() in AUDIO_VIDEO_EXTS
    )
    if not files:
        print("no audio/video files in that folder")
        return

    done = 0
    for f in files:
        if convert_to_mp3(str(f), user_dir):
            done += 1
    print(f"\ndone: {done}/{len(files)} converted")


def link_mode():
    """download from yt/tiktok link"""
    url = input("put the url here\n> ").strip()

    if not url:
        print("u typed nothing. try again")
        return

    custom_name = input("what do u wanna name the file? (blank - default yt title)\n> ").strip()

    supported_patterns = ["youtube.com", "youtu.be", "tiktok.com"]
    is_supported_url = any(pattern in url for pattern in supported_patterns)

    if not is_supported_url:
        print("this isnt a yt/tiktok url, try one of these :")
        print("  https://www.youtube.com/watch?v=VIDEO_ID")
        print("  https://youtu.be/VIDEO_ID")
        print("  https://www.tiktok.com/@user/video/VIDEO_ID")
        print()

        confirm = input("do u still wanna try (y/n): ").strip().lower()
        if confirm != "y":
            return

    print("\nChoose output format:")
    print("  1) MP3 (audio only) - default")
    print("  2) MP4 (video + audio)")

    while True:
        format_choice = input("\nSelect (default: mp3)\n> ").strip().lower()

        if format_choice in ("", "1", "mp3"):
            is_mp4 = False
            break
        elif format_choice in ("2", "mp4"):
            is_mp4 = True
            break
        else:
            print("type 1, 2, mp3 or mp4")

    ext = "mp4" if is_mp4 else "mp3"
    default_dir = DEFAULT_MP4_DIR if is_mp4 else DEFAULT_MP3_DIR
    user_dir = input(f"\nwhere do u wanna dump the {ext}? (default: {default_dir})\n> ").strip() or default_dir

    print()
    download_youtube_audio(url, user_dir, custom_name, is_mp4)


def main():
    """user input thingy"""

    W = 40
    line = "─" * 17 + " ⚔  " + "─" * 18
    print(line)
    print("valors yt/tiktok to mp3/mp4".center(W))
    print(line)
    print()
    print("  1) link (yt/tiktok)")
    print("  2) file from pc to mp3")

    while True:
        mode = input("\nSelect\n(default = 1) \n>").strip()
        if mode in ("", "1"):
            link_mode()
            break
        elif mode == "2":
            local_mode()
            break
        else:
            print("type 1 or 2")


if __name__ == "__main__":
    main()