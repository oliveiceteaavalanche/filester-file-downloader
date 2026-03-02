# 📂 Filester Video Downloader – Dynamic‑URL Extractor

Automate media file downloads from Filester.me using Python. Handles single, bulk, and file-list URL inputs in one script.

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or newer
- Internet connection (Playwright will download Chromium on first run)

### Installation

```bash
# Clone the repo
git clone https://github.com/oliveiceteaavalanche/filester-file-downloader.git
cd filester-file-downloader
```

It is recommended to create a python virtual environment. Refer to [python docs to create an environment](https://docs.python.org/3/library/venv.html).

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install the Chromium binary used by Playwright
playwright install chromium
```

---

## 📖 Usage

```bash
python downloader.py -u https://example.com/page1 https://example.com/page2
```

or with a file containing one URL per line:

```bash
python downloader.py -f urls.txt
```

**Options**

| Flag | Meaning |
|---|---|
| `-u`, `--urls` | Space‑separated list of URLs to process. |
| `-f`, `--file` | Path to a text file with URLs (one per line). |
| `-h`, `--help` | Show help message. |

The script prints status messages, extracts the video URL, and saves the file.

---

## 🛠️ How It Works

1. **Playwright launch** – Starts a headless Chromium instance with a custom User‑Agent.  
2. **Page navigation** – Waits for `networkidle` then looks for a `<video src="…">` element.  
3. **Metadata extraction** – Retrieves the video URL, the `window.fileName` variable, and all cookies from the browser context.  
4. **Download** – Sends a `requests.get` call with the same cookies and a matching User‑Agent, streaming the content while `tqdm` displays progress.

---

## 🤝 Contributing

1. Fork the repository.  
2. Create a feature branch (`git checkout -b feature-name`).  
3. Commit your changes and push (`git push origin feature-name`).  
4. Open a Pull Request describing the improvement.

Please keep the code style consistent (PEP 8) and update this README if you add new options.

---

## 📄 License

This project is licensed under the **MIT License** 
