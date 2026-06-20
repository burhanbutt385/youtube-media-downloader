# YouTube Media Downloader

![Media Downloader UI](https://img.shields.io/badge/UI-CustomTkinter-blue?style=for-the-badge)
![Built with Python](https://img.shields.io/badge/Built_with-Python_3-gold?style=for-the-badge&logo=python)
![Powered by yt-dlp](https://img.shields.io/badge/Powered_by-yt--dlp-red?style=for-the-badge)

A sleek, fast, and highly customizable desktop application for downloading videos and audio directly from YouTube. Designed with a modern, glass-like aesthetic and intuitive user experience in mind, Media Downloader takes the hassle out of securing high-quality media locally.

## ✨ Features

- **Modern & Professional UI**: Built with `customtkinter`, featuring a beautiful dark mode, subtle card animations, and a cohesive design system.
- **Smart Formatting**: Automatically detects and offers the highest available video resolutions (up to 4K/8K) or extracts crisp MP3 audio.
- **Playlist Support**: Intelligently detects playlist URLs and provides a scrollable dialog to batch-add videos to your download queue.
- **Asynchronous Downloading**: Seamlessly fetches metadata and downloads files in the background without freezing the UI.
- **Standalone Distribution**: Available as a completely portable `.exe` or an installable `.msi` Windows installer, requiring **zero dependencies** on the target machine.

## 🚀 Installation & Usage

You do not need to install Python or use the command line if you just want to run the application!

### Option 1: Portable Executable (Recommended)
1. Head over to the `dist` folder.
2. Download `downloader_app.exe`.
3. Double-click the file to run the app immediately. No installation required!

### Option 2: Windows Installer
1. Head over to the `dist` folder.
2. Download and run `YouTube Media Downloader-1.0-win64.msi`.
3. Follow the standard Windows setup wizard to install the application to your PC.

### Option 3: Run from Source
If you are a developer and wish to run or modify the application locally:
```bash
# Clone the repository
git clone https://github.com/yourusername/youtube-media-downloader.git
cd youtube-media-downloader

# Install the required dependencies
pip install -r requirements.txt

# Run the application
python downloader_app.py
```

## 🛠️ Building the Executables

This project uses `PyInstaller` for the portable executable and `cx_Freeze` for the Windows Installer.

**To build the portable `.exe`:**
```bash
pip install pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed downloader_app.py
```

**To build the Windows Installer (`.msi`):**
```bash
pip install cx_Freeze
python setup.py bdist_msi
```

## 📜 Libraries Used
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - For the stunning, modern GUI components.
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - The powerhouse library handling the robust downloading and formatting.
