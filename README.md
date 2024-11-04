# Microsoft Stream Downloader (macOS)

## Prerequisites

### ffmpg

`brew install ffmpeg`

### GUI only: tkinter

`pip install tk`

## Download from Microsoft Stream

### Single Input

`python download_single.py video.mp4 "https://..."`

### Input List

With `input.csv` ready:

`python download_from_input_file.py`

### GUI

`python download_gui.py`
