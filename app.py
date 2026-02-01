import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
import threading
import webbrowser
from urllib.parse import urlparse
import json
import time
from datetime import datetime
import ftplib
import os

from src.database import GameCache
from src.scraper import PSScraper
from src.config import cfg
from src.apis import RealDebridAPI
import ttkthemes

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("450x250")
        self.configure(bg='#2b2b2b')

        # Theme
        style = ttkthemes.ThemedStyle(self)
        style.set_theme("equilux")
        font = ("Segoe UI", 10)
        style.configure('TLabel', font=font)
        style.configure('TEntry', font=font)
        style.configure('TButton', font=font)

        # Load current settings
        apis = cfg.apis
        ftp = cfg.ftp

        # Frame
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Real Debrid API Key
        ttk.Label(frame, text="Real Debrid API Key:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.rd_key = ttk.Entry(frame, width=40)
        self.rd_key.insert(0, apis.get("real_debrid_api_key", ""))
        self.rd_key.grid(row=0, column=1, pady=5, padx=5)
        ttk.Button(frame, text="View API", command=lambda: webbrowser.open("https://real-debrid.com/apitoken")).grid(row=0, column=2, padx=5)

        # FTP Settings
        ttk.Label(frame, text="FTP Host:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.ftp_host = ttk.Entry(frame, width=40)
        self.ftp_host.insert(0, ftp.get("host", ""))
        self.ftp_host.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(frame, text="FTP Port:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.ftp_port = ttk.Entry(frame, width=40)
        self.ftp_port.insert(0, str(ftp.get("port", 21)))
        self.ftp_port.grid(row=2, column=1, pady=5, padx=5)

        ttk.Label(frame, text="FTP Username:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.ftp_user = ttk.Entry(frame, width=40)
        self.ftp_user.insert(0, ftp.get("username", ""))
        self.ftp_user.grid(row=3, column=1, pady=5, padx=5)

        ttk.Label(frame, text="FTP Password:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.ftp_pass = ttk.Entry(frame, width=40, show="*")
        self.ftp_pass.insert(0, ftp.get("password", ""))
        self.ftp_pass.grid(row=4, column=1, pady=5, padx=5)

        # Save button
        self.save_btn = ttk.Button(frame, text="Save", command=self.save_settings)
        self.save_btn.grid(row=5, column=0, columnspan=3, pady=20)

        frame.columnconfigure(1, weight=1)

    def save_settings(self):
        settings = cfg.settings
        settings["apis"] = {
            "real_debrid_api_key": self.rd_key.get()
        }
        settings["ftp"] = {
            "host": self.ftp_host.get(),
            "port": int(self.ftp_port.get()) if self.ftp_port.get().isdigit() else 21,
            "username": self.ftp_user.get(),
            "password": self.ftp_pass.get()
        }
        try:
            with open("settings.json", "w") as f:
                import json
                json.dump(settings, f, indent=4)
            messagebox.showinfo("Settings", "Settings saved successfully!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

class PKGScraperGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Debrid PS PKG Scraper")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')

        # DPI scaling
        dpi = self.root.winfo_fpixels('1i')
        scale = dpi / 72.0
        self.root.call('tk', 'scaling', scale)

        # Dark theme
        self.style = ttkthemes.ThemedStyle(self.root)
        self.style.set_theme("equilux")

        # Custom font
        self.font = ("Segoe UI", 10)
        self.title_font = ("Segoe UI", 14, "bold")

        # Configure styles
        self.style.configure('TLabel', font=self.font)
        self.style.configure('TEntry', font=self.font)
        self.style.configure('TButton', font=self.font)
        self.style.configure('TFrame', borderwidth=1, relief='solid')

        self.db = GameCache()
        self.scraper = PSScraper()
        self.db.load()

        self.games = []
        self.selected_game = None
        self.links = []
        self.selected_link = None
        self.history = self.load_history()

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.create_widgets()

    def create_widgets(self):
        # Title
        title_label = ttk.Label(self.root, text="Debrid PS PKG Scraper", font=self.title_font, anchor='center')
        title_label.pack(pady=10, fill=tk.X)

        # Search frame
        search_frame = ttk.Frame(self.root, padding=10)
        search_frame.pack(fill=tk.X, padx=10)

        ttk.Label(search_frame, text="Search Game:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_games())

        self.search_button = ttk.Button(search_frame, text="Search", command=self.search_games)
        self.search_button.grid(row=0, column=2, padx=5)

        self.history_button = ttk.Button(search_frame, text="Download History", command=self.show_history)
        self.history_button.grid(row=0, column=3, padx=5)

        self.settings_button = ttk.Button(search_frame, text="Settings", command=self.open_settings)
        self.settings_button.grid(row=0, column=4, padx=5)

        search_frame.columnconfigure(1, weight=1)

        # Separator
        ttk.Separator(self.root, orient='horizontal').pack(fill=tk.X, padx=10)

        # Main paned window
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Bottom frame for signup buttons
        bottom_frame = ttk.Frame(self.root, padding=10)
        bottom_frame.pack(fill=tk.X, padx=10)
        ttk.Button(bottom_frame, text="Sign up for Real Debrid", command=lambda: webbrowser.open("http://real-debrid.com/?id=2672286")).pack(side=tk.LEFT, padx=5)

        # Left frame: results
        left_frame = ttk.Frame(self.paned, padding=5)
        self.paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="Search Results:", font=self.title_font).pack(anchor=tk.W)
        results_frame = ttk.Frame(left_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.results_listbox = tk.Listbox(results_frame, bg='#2b2b2b', fg='white', selectbackground='#4a4a4a', font=self.font, height=20, selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_listbox.yview)
        self.results_listbox.configure(yscrollcommand=scrollbar.set)
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_listbox.bind('<<ListboxSelect>>', self.on_game_select)

        # Right frame: details
        right_frame = ttk.Frame(self.paned, padding=5)
        self.paned.add(right_frame, weight=2)

        ttk.Label(right_frame, text="Game Details:", font=self.title_font).pack(anchor=tk.W)

        # Details text
        self.details_text = scrolledtext.ScrolledText(right_frame, bg='#2b2b2b', fg='white', font=self.font, wrap=tk.WORD, height=10)
        self.details_text.pack(fill=tk.X, pady=5)

        # Links
        ttk.Label(right_frame, text="Download Links:").pack(anchor=tk.W)
        links_frame = ttk.Frame(right_frame)
        links_frame.pack(fill=tk.BOTH, expand=True)

        self.links_listbox = tk.Listbox(links_frame, bg='#2b2b2b', fg='white', selectbackground='#4a4a4a', font=self.font, selectmode=tk.SINGLE)
        links_scrollbar = ttk.Scrollbar(links_frame, orient=tk.VERTICAL, command=self.links_listbox.yview)
        self.links_listbox.configure(yscrollcommand=links_scrollbar.set)
        self.links_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        links_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.links_listbox.bind('<<ListboxSelect>>', self.on_link_select)

        # Buttons
        button_frame = ttk.Frame(right_frame, padding=5)
        button_frame.pack(fill=tk.X)

        self.open_link_btn = ttk.Button(button_frame, text="Open Link", command=self.open_selected_link, state=tk.DISABLED)
        self.open_link_btn.pack(side=tk.LEFT, padx=5)

        self.rd_btn = tk.Button(button_frame, text="Download with Real-Debrid", command=self.send_to_rd, state=tk.DISABLED, bg='#ff6b6b', fg='white', font=self.font, relief=tk.RAISED, bd=2)
        self.rd_btn.pack(side=tk.LEFT, padx=5)

        self.ftp_btn = tk.Button(button_frame, text="FTP Transfer", command=self.ftp_transfer, state=tk.DISABLED, bg='#6b6bff', fg='white', font=self.font, relief=tk.RAISED, bd=2)
        self.ftp_btn.pack(side=tk.LEFT, padx=5)

        self.paned.sashpos(0, 400)  # Set initial sash position

    def open_settings(self):
        SettingsWindow(self.root)

    def search_games(self):
        query = self.search_entry.get().strip()
        if not query:
            self.status_var.set("Please enter a search query")
            return
        self.results_listbox.delete(0, tk.END)
        self.details_text.delete(1.0, tk.END)
        self.links_listbox.delete(0, tk.END)
        self.status_var.set("Searching...")
        threading.Thread(target=self._search_games, args=(query,)).start()

    def _search_games(self, query):
        games = self.scraper.search_games(query)
        self.games = games
        self.root.after(0, self.update_results_list)

    def update_results_list(self):
        for i, game in enumerate(self.games):
            self.results_listbox.insert(tk.END, f"{i+1}. {game['title']}")
        self.status_var.set(f"Found {len(self.games)} games")

    def on_game_select(self, event):
        selection = self.results_listbox.curselection()
        if selection:
            idx = selection[0]
            if idx < len(self.games):
                self.selected_game = self.games[idx]
                self.display_game_details()
            else:
                self.status_var.set("Invalid selection")

    def display_game_details(self):
        if not self.selected_game:
            self.status_var.set("No game selected")
            return
        try:
            game = self.selected_game
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, f"Title: {game['title']}\n\n")

            cached_data = self.db.get(game["url"])
            if cached_data:
                self.details_text.insert(tk.END, "Loaded from cache\n")
                links = cached_data["links"]
                metadata = cached_data.get("metadata", {"size": cached_data.get("size", "N/A")})
                self.show_metadata_and_links(metadata, links)
            else:
                self.details_text.insert(tk.END, "Scraping live data...\n")
                self.links_listbox.delete(0, tk.END)
                self.links = []
                self.status_var.set("Scraping game details...")
                threading.Thread(target=self._scrape_details, args=(game,), daemon=True).start()
        except Exception as e:
            self.status_var.set(f"Error displaying game details: {e}")
            print(f"Error in display_game_details: {e}")

    def _scrape_details(self, game):
        try:
            links, metadata = self.scraper.get_game_links(game["url"], game["size"])
            if links:
                game["size"] = metadata.get("size", "N/A")
                self.db.save(game, links, metadata)
            self.root.after(0, lambda: self.show_metadata_and_links(metadata, links))
            self.root.after(0, lambda: self.status_var.set("Details loaded"))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error scraping details: {e}"))
            print(f"Error in _scrape_details: {e}")

    def show_metadata_and_links(self, metadata, links):
        try:
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(tk.END, f"Size: {metadata.get('size', 'N/A')}\n")
            self.details_text.insert(tk.END, f"Version: {metadata.get('version', 'N/A')}\n")
            self.details_text.insert(tk.END, f"Region: {metadata.get('region', 'N/A')}\n")
            self.details_text.insert(tk.END, f"CUSA: {metadata.get('cusa', 'N/A')}\n")
            self.details_text.insert(tk.END, f"Firmware: {metadata.get('firmware', 'N/A')}\n")
            self.details_text.insert(tk.END, f"Voice: {metadata.get('voice', 'N/A')}\n")
            self.details_text.insert(tk.END, f"Subtitles: {metadata.get('subtitles', 'N/A')}\n")
            pwd = metadata.get("password")
            if pwd and pwd.lower() != "n/a":
                self.details_text.insert(tk.END, f"Password: {pwd}\n")

            self.links_listbox.delete(0, tk.END)
            self.links = []
            if links:
                if isinstance(links[0], dict):
                    from itertools import groupby
                    links.sort(key=lambda x: x.get("group", "Misc"))
                    for group_name, group_items in groupby(links, key=lambda x: x.get("group", "Misc")):
                        for item in group_items:
                            url = item.get("url", "")
                            label = item.get("label", "Link")
                            host = self.get_host_name(url)
                            display = f"{group_name} - {label} ({host})"
                            self.links_listbox.insert(tk.END, display)
                            self.links.append(url)
                else:
                    for link in links:
                        host = self.get_host_name(link)
                        display = f"{host}: {link}"
                        self.links_listbox.insert(tk.END, display)
                        self.links.append(link)
                self.status_var.set(f"Loaded {len(links)} download links")
            else:
                self.links_listbox.insert(tk.END, "No download links found.")
                self.status_var.set("No download links found")
        except Exception as e:
            self.status_var.set(f"Error showing metadata: {e}")
            print(f"Error in show_metadata_and_links: {e}")

    def on_link_select(self, event):
        selection = self.links_listbox.curselection()
        if selection and self.links:
            idx = selection[0]
            if idx < len(self.links):
                self.selected_link = self.links[idx]
                self.open_link_btn.config(state=tk.NORMAL)
                self.rd_btn.config(state=tk.NORMAL)
                self.ftp_btn.config(state=tk.NORMAL)
            else:
                self.selected_link = None
                self.open_link_btn.config(state=tk.DISABLED)
                self.rd_btn.config(state=tk.DISABLED)
                self.ftp_btn.config(state=tk.DISABLED)
        else:
            self.selected_link = None
            self.open_link_btn.config(state=tk.DISABLED)
            self.rd_btn.config(state=tk.DISABLED)
            self.ftp_btn.config(state=tk.DISABLED)

    def open_selected_link(self):
        if self.selected_link:
            webbrowser.open(self.selected_link)

    def send_to_rd(self):
        if not self.selected_link:
            return
        apis = cfg.apis
        api_key = apis.get("real_debrid_api_key", "")
        if not api_key:
            messagebox.showerror("Error", "Real Debrid API key not set. Please configure in settings.")
            return
        rd = RealDebridAPI(api_key)
        try:
            result = rd.unrestrict_link(self.selected_link)
            if "download" in result:
                webbrowser.open(result["download"])
                # Add to history
                self.add_to_history(self.selected_game['title'], self.selected_link, result["download"])
            else:
                messagebox.showerror("Error", f"Failed to unrestrict link: {result}")
        except Exception as e:
            messagebox.showerror("Error", f"Exception: {e}")

    def ftp_transfer(self):
        ftp_config = cfg.ftp
        if not ftp_config.get("host"):
            messagebox.showerror("Error", "FTP host not configured. Please set it in settings.")
            return

        # Select local file
        local_file = filedialog.askopenfilename(title="Select file to upload")
        if not local_file:
            return

        # Ask for remote directory
        remote_dir = simpledialog.askstring("FTP Directory", "Enter remote directory path:", initialvalue="/")
        if remote_dir is None:
            return

        # Upload in thread
        threading.Thread(target=self._ftp_upload, args=(local_file, remote_dir, ftp_config), daemon=True).start()

    def _ftp_upload(self, local_file, remote_dir, ftp_config):
        try:
            with ftplib.FTP() as ftp:
                ftp.connect(ftp_config["host"], ftp_config["port"])
                ftp.login(ftp_config["username"], ftp_config["password"])

                # Change to remote directory
                if remote_dir and remote_dir != "/":
                    try:
                        ftp.cwd(remote_dir)
                    except ftplib.error_perm:
                        self.root.after(0, lambda: messagebox.showerror("FTP Error", f"Cannot access directory: {remote_dir}"))
                        return

                # Upload file
                filename = os.path.basename(local_file)
                with open(local_file, 'rb') as f:
                    ftp.storbinary(f'STOR {filename}', f)

                self.root.after(0, lambda: messagebox.showinfo("Success", f"Uploaded {filename} to FTP"))

        except Exception as e:
            self.root.after(0, lambda: self.root.after(0, lambda: messagebox.showerror("FTP Error", f"Upload failed: {e}")))

    def get_host_name(self, url):
        try:
            domain = urlparse(url).netloc
            parts = domain.replace("www.", "").split(".")
            return parts[0].capitalize() if parts else "Link"
        except:
            return "Link"

    def run(self):
        self.root.mainloop()

    def load_history(self):
        try:
            with open("download_history.json", "r") as f:
                return json.load(f)
        except:
            return []

    def save_history(self):
        try:
            with open("download_history.json", "w") as f:
                json.dump(self.history, f, indent=4)
        except:
            pass

    def add_to_history(self, game_title, original_link, download_link):
        entry = {
            "timestamp": time.time(),
            "game_title": game_title,
            "original_link": original_link,
            "download_link": download_link
        }
        self.history.append(entry)
        self.save_history()

    def show_history(self):
        history_window = tk.Toplevel(self.root)
        history_window.title("Download History")
        history_window.geometry("800x600")
        history_window.configure(bg='#2b2b2b')

        # Theme
        style = ttkthemes.ThemedStyle(history_window)
        style.set_theme("equilux")

        # Scrolled text
        text = scrolledtext.ScrolledText(history_window, bg='#2b2b2b', fg='white', font=self.font, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for entry in reversed(self.history[-50:]):  # Show last 50
            dt = datetime.fromtimestamp(entry["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            text.insert(tk.END, f"{dt} - {entry['game_title']}\n")
            text.insert(tk.END, f"Original: {entry['original_link']}\n")
            text.insert(tk.END, f"Download: {entry['download_link']}\n\n")

        text.config(state=tk.DISABLED)

if __name__ == "__main__":
    app = PKGScraperGUI()
    app.run()