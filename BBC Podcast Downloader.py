import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from threading import Thread
import re
from urllib.parse import urljoin
import pyperclip 

class PodcastScraper:
    def __init__(self, root):
        self.root = root
        self.root.title("BBC Podcast Scraper")
        self.episode_links = []
        self.failed_links = [] 
        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Dropdown for podcast selection
        ttk.Label(main_frame, text="Select Podcast:").pack(pady=5)
        self.podcast_choice = ttk.Combobox(main_frame, values=["The English We Speak", "6 Minute English"])
        self.podcast_choice.pack(pady=5)
        self.podcast_choice.set("The English We Speak")  # Default selection

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=5)

        self.scrape_btn = ttk.Button(
            btn_frame, 
            text="1. Scrape Episodes", 
            command=self.start_scraping_thread
        )
        self.scrape_btn.pack(side=tk.LEFT, padx=5)

        self.update_btn = ttk.Button(
            btn_frame, 
            text="2. Update Media Links", 
            state=tk.DISABLED,
            command=self.update_media_links
        )
        self.update_btn.pack(side=tk.LEFT, padx=5)

        self.save_btn = ttk.Button(
            btn_frame, 
            text="3. Save Links to File", 
            state=tk.DISABLED, 
            command=self.save_links_to_file
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)

        # Tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.episode_tab = scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD)
        self.notebook.add(self.episode_tab, text="Episodes")

        self.media_tab = scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD)
        self.notebook.add(self.media_tab, text="Media Links")

        self.failed_tab = scrolledtext.ScrolledText(self.notebook, wrap=tk.WORD)  # Tab for failed links
        self.notebook.add(self.failed_tab, text="Failed Links")

        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.pack()

        # Bind Ctrl + V to paste clipboard content into the appropriate tab
        self.episode_tab.bind("<Control-v>", self.paste_clipboard)  # For episodes tab
        self.media_tab.bind("<Control-v>", self.paste_clipboard)  # For media tab
        self.failed_tab.bind("<Control-v>", self.paste_clipboard)  # For failed links tab

        # Bind to delete selected episode link from the list
        self.episode_tab.bind("<Delete>", self.delete_selected_link)

    def start_scraping_thread(self):
        Thread(target=self.scrape_episodes, daemon=True).start()

    def update_media_links(self):
        Thread(target=self.extract_media_from_tabs, daemon=True).start()

    def scrape_episodes(self):
        self.toggle_ui(state=tk.DISABLED)
        self.clear_tabs()  # Clear the content of tabs

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            base_url = self.get_base_url()

            self.episode_links = self.get_sorted_episodes(base_url, headers)

            if not self.episode_links:
                messagebox.showwarning("Warning", "No episodes found!")
                return

            self.episode_tab.insert(tk.END, "\n".join(self.episode_links))
            self.update_btn['state'] = tk.NORMAL  # Enable the update button
            self.save_btn['state'] = tk.NORMAL
            self.update_status(f"Found {len(self.episode_links)} episodes")

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.toggle_ui(state=tk.NORMAL)

    def get_base_url(self):
        podcast_type = self.podcast_choice.get()
        if podcast_type == "The English We Speak":
            return "https://www.bbc.co.uk/learningenglish/english/features/the-english-we-speak"
        elif podcast_type == "6 Minute English":
            return "https://www.bbc.co.uk/learningenglish/english/features/6-minute-english"
        else:
            raise ValueError("Unknown podcast type")

    def get_sorted_episodes(self, base_url, headers):
        episodes = []
        page = 1

        while page <= 10:
            try:
                url = f"{base_url}?page={page}" if page > 1 else base_url
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code != 200:
                    break

                soup = BeautifulSoup(response.text, 'html.parser')
                # Adjust regex to match all episode links
                pattern = re.compile(
                    r'/(the-english-we-speak[-_/]20\d{2}[-_/]ep-\d+|'
                    r'features/the-english-we-speak/ep-\d+|'
                    r'features/the-english-we-speak_\d{4}/ep-\d+|'
                    r'6-minute-english_\d{4}/ep-\d+|features/6-minute-english/ep-\d+)', re.IGNORECASE
                )

                links = soup.find_all('a', href=pattern)
                for link in links:
                    href = link.get('href')
                    full_url = urljoin(base_url, href)
                    if full_url not in episodes:
                        episodes.append(full_url)

                if not links:
                    break

                page += 1

            except Exception as e:
                messagebox.showwarning("Error", f"Page {page} error: {str(e)}")
                break

        return sorted(
            episodes,
            key=lambda x: re.search(r'ep-(\d{6})', x).group(1),
            reverse=False
        )

    def extract_media_from_tabs(self):
        self.toggle_ui(state=tk.DISABLED)
        self.media_tab.delete(1.0, tk.END)
        self.failed_tab.delete(1.0, tk.END)

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}

            # Use only episode links from the episode tab (ones the user added)
            current_links = self.episode_tab.get(1.0, tk.END).strip().split('\n')
            
            for idx, url in enumerate(current_links, 1):
                if url:
                    self.update_status(f"Processing {idx}/{len(current_links)}")
                    pdf, audio = self.get_media_links(url, headers)

                    # Add only the media links, without labels, to the media tab
                    if pdf != "N/A" or audio != "N/A":
                        if pdf != "N/A":
                            self.media_tab.insert(tk.END, f"{pdf}\n")
                        else:
                            self.failed_tab.insert(tk.END, f"Failed to find PDF for {url}\n")
                        
                        if audio != "N/A":
                            self.media_tab.insert(tk.END, f"{audio}\n")
                        else:
                            self.failed_tab.insert(tk.END, f"Failed to find Audio for {url}\n")
                    else:
                        self.failed_tab.insert(tk.END, f"Both PDF and Audio missing for {url}\n")

            self.update_status("Media extraction completed!")

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.toggle_ui(state=tk.NORMAL)

    def get_media_links(self, url, headers):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            pdf_link = soup.find('a', href=re.compile(r'\.pdf$', re.I))
            pdf = urljoin(url, pdf_link['href']) if pdf_link else "N/A"

            audio_link = soup.find('a', href=re.compile(r'\.mp3$', re.I))
            audio = urljoin(url, audio_link['href']) if audio_link else "N/A"

            return pdf, audio

        except Exception as e:
            return "N/A", "N/A"

    def save_links_to_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as f:
                f.write(self.media_tab.get(1.0, tk.END))
            messagebox.showinfo("Success", f"Links saved to {file_path}")

    def paste_clipboard(self, event):
        clipboard_content = pyperclip.paste()
        current_tab = self.notebook.index(self.notebook.select())  # Get the current selected tab
        if current_tab == 0:  # Episode tab
            self.episode_tab.insert(tk.END, clipboard_content + "\n")
        elif current_tab == 1:  # Media tab
            self.media_tab.insert(tk.END, clipboard_content + "\n")
        elif current_tab == 2:  # Failed tab
            self.failed_tab.insert(tk.END, clipboard_content + "\n")

    def delete_selected_link(self, event):
        try:
            selected_text = self.episode_tab.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.episode_links = [link for link in self.episode_links if link not in selected_text]
            self.episode_tab.delete(tk.SEL_FIRST, tk.SEL_LAST)
            messagebox.showinfo("Success", "Link(s) deleted")
        except tk.TclError:
            pass

    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def toggle_ui(self, state):
        self.scrape_btn['state'] = state
        self.update_btn['state'] = state
        self.save_btn['state'] = state

    def clear_tabs(self):
        self.episode_tab.delete(1.0, tk.END)
        self.media_tab.delete(1.0, tk.END)
        self.failed_tab.delete(1.0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = PodcastScraper(root)
    root.mainloop()
