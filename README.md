# 🎧 BBC Podcast Downloader

A user-friendly Python application for extracting and downloading **audio** and **PDF transcripts** from BBC Learning English podcasts, including:

- **The English We Speak**
- **6 Minute English**

Built with a clean GUI using Tkinter, it allows you to browse, filter, and save podcast media links with ease.

---

## ✅ Features

- 🎙️ **Select Podcast Type** – Choose between podcast categories.
- 🗂️ **Episode Filtering** – Manually remove unwanted episodes before scraping.
- 🔊 **Download Audio & PDF** – Extract direct links for each episode.
- 💾 **Save & Copy Links** – Save results as a text file or copy them to clipboard.
- ⚠️ **Failed Media Tab** – View episodes missing audio or PDF files.
- 🔁 **Update Button** – Re-extract media only from selected (remaining) episode links.
- 📁 **Custom Save Location** – Choose where to save the output file.

---

## 🛠️ Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/bbc-podcast-downloader.git
   cd bbc-podcast-downloader


2. **Install Dependencies**
   Make sure you have Python 3.7 or higher installed, then run


3. **Run the Application**

   ```bash
   python BBC Podcast Downloader.py
   ```

---

## 📝 Requirements:

* `requests`
* `beautifulsoup4`
* `tk`
* `ttkthemes`
* `pillow`

---

## 🚀 Usage

1. Launch the app.
2. Select the podcast type.
3. Click the **"Scrape Episodes"** button.
4. Review the list of episodes, and remove any unwanted links.
5. Click **"Download Media"** to extract available audio and PDF files.
6. Use **"Save"** or **Ctrl + V** to copy or store your results.
7. Use **"Update"** to reprocess only the current links in the episode tab.

---

## 📂 Output Example

Saved link text file format:

```
https://.../episode1.mp3
https://.../episode1.pdf

https://.../episode2.mp3
https://.../episode2.pdf
```

Failed episodes will be listed under the **Failed** tab and saved separately (if desired).
