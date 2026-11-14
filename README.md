# YouTube to MP3/MP4

Download audio (mp3) or video (mp4) from YouTube/TikTok links, or convert files on your PC to mp3.

## Setup (Windows)

1. Install Python. Open terminal, run:
   ```
   winget install Python.Python.3.12
   ```
   Close terminal & open a new one.

2. Install the requirements (includes yt-dlp & ffmpeg):
   ```
   pip install -r requirements.txt
   ```

3. Run it:
   ```
   python youtube_mp3_converter.py
   ```

## Save paths

Files save to your Downloads folder by default. To change it, open `youtube_mp3_converter.py` & look for the lines marked:

```
# CHANGE DEFAULT MP3 FOLDER HERE
# CHANGE DEFAULT MP4 FOLDER HERE
```

Or just type your own folder when it asks where to save.

## Troubleshooting

- **`winget` not found:** install Python from [python.org](https://python.org) (tick "Add to PATH").
- **Got a .webm instead of mp3:** ffmpeg wasn't found. Run `winget install ffmpeg`, then close terminal & open a new one. Or download it from [ffmpeg.org](https://ffmpeg.org).