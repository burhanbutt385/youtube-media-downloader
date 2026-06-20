import customtkinter as ctk
import yt_dlp
import threading
import os
import time

# Apply a global sleek dark theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Define global fonts for a professional look
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SUBTITLE = ("Segoe UI", 14, "bold")
FONT_DEFAULT = ("Segoe UI", 13)
FONT_SMALL = ("Segoe UI", 11)

class PlaylistDialog(ctk.CTkToplevel):
    def __init__(self, master, playlist_info, on_confirm_callback):
        super().__init__(master)
        self.title("Playlist Detected")
        self.geometry("550x650")
        self.attributes('-topmost', True)
        self.configure(fg_color="#1a1a1a")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header Area
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        title_text = "Playlist Detected"
        ctk.CTkLabel(header, text=title_text, font=FONT_TITLE, text_color="#5fa5f9").pack(anchor="w")
        
        subtitle_text = f"{playlist_info.get('title', 'Unknown')} • {len(playlist_info.get('entries', []))} videos"
        ctk.CTkLabel(header, text=subtitle_text, font=FONT_DEFAULT, text_color="gray").pack(anchor="w", pady=(2, 0))

        # Scrollable list of videos (sleek card)
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#242424", corner_radius=10)
        self.scroll_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        entries = playlist_info.get('entries', [])
        for i, entry in enumerate(entries):
            video_title = entry.get('title', 'Private/Deleted Video')
            lbl = ctk.CTkLabel(self.scroll_frame, text=f"{i+1}. {video_title}", anchor="w", justify="left", font=FONT_DEFAULT)
            lbl.grid(row=i, column=0, sticky="w", pady=4, padx=5)

        # Buttons
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=2, column=0, pady=20, padx=20, sticky="ew")
        
        self.confirm_btn = ctk.CTkButton(self.btn_frame, text="Add All to Queue", font=FONT_DEFAULT, fg_color="#2563eb", hover_color="#1d4ed8",
                                         command=lambda: self.confirm(on_confirm_callback), height=40, corner_radius=8)
        self.confirm_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))

        self.cancel_btn = ctk.CTkButton(self.btn_frame, text="Cancel", font=FONT_DEFAULT, fg_color="#3f3f46", hover_color="#27272a",
                                        command=self.destroy, height=40, corner_radius=8)
        self.cancel_btn.pack(side="right", expand=True, fill="x", padx=(10, 0))

    def confirm(self, callback):
        self.destroy()
        callback()

class DownloadItem(ctk.CTkFrame):
    def __init__(self, master, url, app_instance, auto_start=False, pre_fetched_info=None):
        # Card style background
        super().__init__(master, corner_radius=12, fg_color="#262626")
        self.url = url
        self.app = app_instance
        self.video_info = pre_fetched_info
        self.available_formats = []
        
        # State machine
        self.status = "Idle"
        self.cancel_requested = False

        self.grid_columnconfigure(1, weight=1)

        # Title Label with subtle loading text initially
        self.title_label = ctk.CTkLabel(self, text="Fetching details...", font=FONT_SUBTITLE, anchor="w", text_color="#a1a1aa")
        self.title_label.grid(row=0, column=0, columnspan=3, padx=15, pady=(15, 10), sticky="ew")

        # Options Frame
        self.options_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.options_frame.grid(row=1, column=0, columnspan=2, padx=15, sticky="w")

        # Type Selection
        self.type_var = ctk.StringVar(value="Video (mp4)")
        self.type_menu = ctk.CTkOptionMenu(self.options_frame, variable=self.type_var, values=["Video (mp4)", "Audio (mp3)"], command=self.update_resolutions, width=130, height=32, corner_radius=6, font=FONT_DEFAULT)
        self.type_menu.pack(side="left", padx=(0, 10))

        # Resolution Selection
        self.res_var = ctk.StringVar(value="Loading...")
        self.res_menu = ctk.CTkOptionMenu(self.options_frame, variable=self.res_var, values=["Loading..."], width=130, height=32, corner_radius=6, font=FONT_DEFAULT)
        self.res_menu.pack(side="left")

        # Action Button (Start/Cancel/Done)
        self.action_button = ctk.CTkButton(self, text="Start", font=FONT_DEFAULT, command=self.handle_action, width=100, height=32, corner_radius=6, fg_color="#10b981", hover_color="#059669", state="disabled")
        self.action_button.grid(row=1, column=2, padx=15, sticky="e")

        # Progress Area
        self.progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.progress_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=15, pady=(15, 15))
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, height=8, corner_radius=4, progress_color="#3b82f6")
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 15))

        self.status_label = ctk.CTkLabel(self.progress_frame, text="0%", width=45, anchor="e", font=FONT_DEFAULT, text_color="#a1a1aa")
        self.status_label.grid(row=0, column=1)

        # Loading animation thread control
        self.is_fetching = True
        self.loading_thread = threading.Thread(target=self.animate_loading_text)
        self.loading_thread.start()

        # Fetch info
        if self.video_info:
            self.process_video_info(self.video_info, auto_start)
        else:
            threading.Thread(target=self.fetch_video_info, args=(url, auto_start)).start()

    def animate_loading_text(self):
        dots = 0
        while self.is_fetching:
            if self.status == "Error":
                break
            dots = (dots + 1) % 4
            try:
                self.title_label.configure(text="Fetching details" + "." * dots)
            except:
                break
            time.sleep(0.4)

    def fetch_video_info(self, url, auto_start):
        ydl_opts = {'extract_flat': 'in_playlist', 'quiet': True, 'no_warnings': True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            self.after(0, self.process_video_info, info, auto_start)
        except Exception as e:
            self.is_fetching = False
            self.after(0, self.show_error, str(e))

    def process_video_info(self, info, auto_start):
        self.is_fetching = False
        self.video_info = info
        title = info.get('title', 'Unknown Title')
        
        if 'entries' in info and len(info['entries']) > 0:
            title = f"[Playlist] {title} ({len(info['entries'])} videos)"
            first_url = info['entries'][0].get('url') or info['entries'][0].get('webpage_url')
            if first_url:
                try:
                    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                        single_info = ydl.extract_info(first_url, download=False)
                        self.available_formats = single_info.get('formats', [])
                except:
                    pass
        else:
            self.available_formats = info.get('formats', [])

        self.title_label.configure(text=title, text_color="#f4f4f5") # Bright text
        self.update_resolutions(self.type_var.get())
        self.action_button.configure(state="normal")

        if auto_start:
            self.queue_download()

    def update_resolutions(self, type_choice):
        if not self.available_formats:
            self.res_menu.configure(values=["Default/Best"])
            self.res_var.set("Default/Best")
            return

        if "Audio" in type_choice:
            self.res_menu.configure(values=["Best Audio"])
            self.res_var.set("Best Audio")
        else:
            resolutions = set()
            for f in self.available_formats:
                if f.get('vcodec') != 'none' and f.get('height'):
                    resolutions.add(f"{f.get('height')}p")
            
            res_list = sorted(list(resolutions), key=lambda x: int(x.replace('p', '')), reverse=True)
            if not res_list:
                res_list = ["Best Video"]
            
            self.res_menu.configure(values=res_list)
            self.res_var.set(res_list[0])

    def show_error(self, error_msg):
        self.is_fetching = False
        self.title_label.configure(text="Error Fetching Metadata", text_color="#ef4444")
        self.status_label.configure(text="Error", text_color="#ef4444")
        self.progress_bar.configure(progress_color="#ef4444")

    def handle_action(self):
        if self.status in ["Idle", "Cancelled"]:
            self.queue_download()
        elif self.status in ["Queued", "Downloading"]:
            self.cancel_download()

    def cancel_download(self):
        if self.status == "Queued":
            self.status = "Cancelled"
            self.action_button.configure(text="Start", state="normal", fg_color="#10b981", hover_color="#059669")
            self.type_menu.configure(state="normal")
            self.res_menu.configure(state="normal")
            self.configure(border_color="transparent", border_width=0)
        elif self.status == "Downloading":
            self.cancel_requested = True
            self.action_button.configure(text="Cancelling...", state="disabled", fg_color="#f59e0b")

    def mark_cancelled(self):
        self.status = "Cancelled"
        self.cancel_requested = False
        self.action_button.configure(text="Start", state="normal", fg_color="#10b981", hover_color="#059669")
        self.type_menu.configure(state="normal")
        self.res_menu.configure(state="normal")
        self.configure(border_color="transparent", border_width=0)
        self.status_label.configure(text="0%", text_color="#a1a1aa")
        self.progress_bar.set(0)
        self.progress_bar.configure(progress_color="#3b82f6")

    def progress_hook(self, d):
        if getattr(self, 'cancel_requested', False):
            raise Exception("Download cancelled by user")
            
        if d['status'] == 'downloading':
            try:
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded_bytes = d.get('downloaded_bytes', 0)
                if total_bytes > 0:
                    percent = downloaded_bytes / total_bytes
                    self.after(0, self.update_progress, percent)
            except:
                pass
        elif d['status'] == 'finished':
            self.after(0, self.update_progress, 1.0)
            self.after(0, self.mark_done)

    def mark_done(self):
        self.status = "Done"
        self.action_button.configure(text="Done", state="disabled", fg_color="#3f3f46")
        self.progress_bar.configure(progress_color="#10b981") # Green
        self.status_label.configure(text="Done!", text_color="#10b981")
        self.configure(border_width=1, border_color="#10b981")
        
    def update_progress(self, percent):
        self.progress_bar.set(percent)
        self.status_label.configure(text=f"{int(percent * 100)}%")

    def queue_download(self):
        if self.status not in ["Idle", "Cancelled"]:
            return
            
        self.cancel_requested = False
        self.status = "Queued"
        self.configure(border_width=1, border_color="#3b82f6") # Blue border for queued
        self.progress_bar.configure(progress_color="#3b82f6")
        self.action_button.configure(text="Cancel", state="normal", fg_color="#f59e0b", hover_color="#d97706")
        self.type_menu.configure(state="disabled")
        self.res_menu.configure(state="disabled")
        
        self.app.check_queue()

    def begin_download(self):
        self.status = "Downloading"
        self.action_button.configure(text="Stop", fg_color="#ef4444", hover_color="#b91c1c")
        self.progress_bar.configure(progress_color="#6366f1") # Indigo for active download
        thread = threading.Thread(target=self.download_video)
        thread.start()

    def download_video(self):
        download_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
        file_type = self.type_var.get()
        resolution = self.res_var.get()

        format_str = 'best'
        if "Audio" in file_type:
            format_str = 'bestaudio/best'
        else:
            if resolution != "Default/Best" and resolution != "Best Video":
                height = resolution.replace('p', '')
                format_str = f'bestvideo[height<={height}]+bestaudio/best'

        ydl_opts = {
            'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
            'format': format_str,
            'progress_hooks': [self.progress_hook],
            'quiet': True,
            'no_warnings': True,
            'concurrent_fragment_downloads': 10,
        }

        if "Audio" in file_type:
            ydl_opts['postprocessors'] = [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
                {'key': 'EmbedThumbnail'},
                {'key': 'FFmpegMetadata', 'add_metadata': True}
            ]
            ydl_opts['writethumbnail'] = True

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
        except Exception as e:
            if getattr(self, 'cancel_requested', False):
                self.after(0, self.mark_cancelled)
            else:
                self.after(0, self.show_error, str(e))
                self.after(0, self.action_button.configure, {"text": "Error", "fg_color": "#ef4444"})
                self.after(0, self.configure, {"border_width": 1, "border_color": "#ef4444"})
                self.status = "Error"
        finally:
            self.app.active_downloads -= 1
            self.app.check_queue()


class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Media Downloader")
        self.geometry("900x700")
        self.configure(fg_color="#121212")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.active_downloads = 0

        # Header Frame (Glassy/Sleek look)
        self.header_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1e1e1e")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        self.header_frame.grid_columnconfigure(0, weight=1)

        # Title Label
        self.app_title = ctk.CTkLabel(self.header_frame, text="Media Downloader", font=("Segoe UI", 24, "bold"), text_color="#ffffff")
        self.app_title.grid(row=0, column=0, columnspan=4, sticky="w", padx=20, pady=(20, 5))

        # Subtitle Label
        self.app_subtitle = ctk.CTkLabel(self.header_frame, text="Download videos and audio in high quality", font=FONT_DEFAULT, text_color="#a1a1aa")
        self.app_subtitle.grid(row=1, column=0, columnspan=4, sticky="w", padx=20, pady=(0, 15))

        # Controls Container
        self.controls = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.controls.grid(row=2, column=0, columnspan=4, sticky="ew", padx=20, pady=(0, 20))
        self.controls.grid_columnconfigure(0, weight=1)

        # URL Input
        self.url_var = ctk.StringVar()
        self.url_entry = ctk.CTkEntry(self.controls, textvariable=self.url_var, placeholder_text="Paste YouTube URL here...", font=FONT_DEFAULT, height=45, corner_radius=8, border_width=1, border_color="#3f3f46", fg_color="#27272a")
        self.url_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        # Add Button
        self.add_button = ctk.CTkButton(self.controls, text="Add to Queue", font=FONT_SUBTITLE, command=self.check_url_thread, width=140, height=45, corner_radius=8, fg_color="#2563eb", hover_color="#1d4ed8")
        self.add_button.grid(row=0, column=1, padx=(0, 10))

        # Start All Button
        self.start_all_btn = ctk.CTkButton(self.controls, text="Start All", font=FONT_SUBTITLE, command=self.start_all_queued, width=120, height=45, corner_radius=8, fg_color="#10b981", hover_color="#059669")
        self.start_all_btn.grid(row=0, column=2, padx=(0, 15))

        # Auto-Download Switch
        self.auto_download_var = ctk.BooleanVar(value=False)
        self.auto_download_switch = ctk.CTkSwitch(self.controls, text="Auto-Start", font=FONT_DEFAULT, variable=self.auto_download_var, progress_color="#2563eb")
        self.auto_download_switch.grid(row=0, column=3)

        # Loading Indeterminate Bar (Hidden by default)
        self.loading_bar = ctk.CTkProgressBar(self.header_frame, mode="indeterminate", height=3, corner_radius=0, progress_color="#3b82f6", fg_color="#1e1e1e")
        self.loading_bar.grid(row=3, column=0, columnspan=4, sticky="ew", padx=20, pady=(0, 0))
        self.loading_bar.set(0)
        self.loading_bar.grid_remove()

        # Queue Frame (Scrollable)
        self.queue_frame = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        self.queue_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.queue_frame.grid_columnconfigure(0, weight=1)
        
        self.items = []

    def check_url_thread(self):
        url = self.url_var.get().strip()
        if not url:
            return
            
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://www.youtube.com/watch?v={url}"

        self.url_var.set("")
        self.add_button.configure(state="disabled", text="Checking...")
        
        # Show and start loading bar
        self.loading_bar.grid()
        self.loading_bar.start()

        threading.Thread(target=self.fetch_initial_info, args=(url,)).start()

    def fetch_initial_info(self, url):
        ydl_opts = {'extract_flat': 'in_playlist', 'quiet': True, 'no_warnings': True}
        
        if "list=RD" in url:
            ydl_opts['playlistend'] = 50

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            self.after(0, self.handle_fetched_info, info, url)
        except Exception as e:
            self.after(0, self.reset_add_button)
            print(f"Error fetching info: {e}")

    def reset_add_button(self):
        self.add_button.configure(state="normal", text="Add to Queue")
        self.loading_bar.stop()
        self.loading_bar.grid_remove()

    def handle_fetched_info(self, info, url):
        self.reset_add_button()
        
        if 'entries' in info and len(info['entries']) > 0:
            PlaylistDialog(self, info, on_confirm_callback=lambda: self.add_playlist_items(info))
        else:
            self.add_item_to_queue(url, info)

    def add_playlist_items(self, playlist_info):
        for entry in playlist_info.get('entries', []):
            vid_url = entry.get('url') or entry.get('webpage_url')
            if not vid_url and entry.get('id'):
                vid_url = f"https://www.youtube.com/watch?v={entry.get('id')}"
                
            if vid_url:
                self.add_item_to_queue(vid_url, entry)

    def add_item_to_queue(self, url, info):
        auto_start = self.auto_download_var.get()
        item = DownloadItem(self.queue_frame, url, self, auto_start=auto_start, pre_fetched_info=info)
        item.grid(row=len(self.items), column=0, sticky="ew", padx=10, pady=(0, 15))
        self.items.append(item)
        
    def start_all_queued(self):
        for item in self.items:
            if item.status in ["Idle", "Cancelled"]:
                item.queue_download()

    def check_queue(self):
        if self.active_downloads >= 2:
            return
            
        for item in self.items:
            if item.status == "Queued":
                self.active_downloads += 1
                item.begin_download()
                if self.active_downloads >= 2:
                    break

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
