import sys
from cx_Freeze import setup, Executable

# cx_Freeze automatically detects most dependencies, but we can explicitly include important ones
build_exe_options = {
    "packages": ["os", "customtkinter", "yt_dlp"],
    "excludes": [],
}

# Use "Win32GUI" for a GUI application on Windows so it doesn't open a console window
base = "gui" if sys.platform == "win32" else None

setup(
    name="YouTube Media Downloader",
    version="1.0",
    description="A sleek app to download videos and audio from YouTube",
    author="Burhan",
    options={"build_exe": build_exe_options},
    executables=[Executable("downloader_app.py", base=base, target_name="MediaDownloader.exe")]
)
