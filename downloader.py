#!/usr/bin/env python3
import argparse
import sys
import requests
from tqdm import tqdm
from playwright.sync_api import sync_playwright

def extract_metadata(page_url):
    """Uses a headless browser to run JavaScript and extract the dynamic video URL."""
    print(f"[*] Loading {page_url} | Please Wait...")
    
    with sync_playwright() as p:
        # Launch headless Chromium
        browser = p.chromium.launch(headless=True)
        
        # Set a standard User-Agent
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            # Go to the URL and wait for the network to quiet down
            page.goto(page_url, wait_until="networkidle", timeout=30000)
            
            # Wait specifically for a <video> tag that HAS a 'src' attribute
            # This ensures the page's JavaScript has finished injecting the link
            video_element = page.wait_for_selector("video[src]", timeout=15000)
            
            if not video_element:
                print(f"[-] Could not find a loaded <video> tag on {page_url}")
                return None, None, None
                
            # Extract the fully populated src and the JavaScript fileName variable
            video_url = video_element.get_attribute("src")
            file_name = page.evaluate("window.fileName")
            
            # Extract cookies so our requests downloader is authenticated
            cookies = {cookie['name']: cookie['value'] for cookie in context.cookies()}
            
            return video_url, file_name, cookies
            
        except Exception as e:
            print(f"[-] Browser extraction failed for {page_url}: {e}")
            return None, None, None
        finally:
            browser.close()

def download_video(video_url, file_name, cookies, current_index, total_files):
    """Downloads the video with a progress bar displaying size and speed."""
    print(f"\nDownloading [{current_index} out of {total_files}]: {file_name}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Referer": "https://filester.me/"
    }
    
    try:
        # Pass the Playwright session cookies to the requests session to bypass 403s
        response = requests.get(video_url, stream=True, headers=headers, cookies=cookies)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        progress_bar = tqdm(
            total=total_size, 
            unit='B', 
            unit_scale=True, 
            unit_divisor=1024,
            desc="Progress",
            ascii=False,
            bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}B out of {total_fmt}B [{rate_fmt}{postfix}]"
        )
        
        with open(file_name, 'wb') as file:
            for data in response.iter_content(chunk_size=1024 * 64):
                if data:
                    size = file.write(data)
                    progress_bar.update(size)
                    
        progress_bar.close()
        print(f"[+] Successfully downloaded: {file_name}")
        
    except Exception as e:
        print(f"[-] Error downloading {file_name}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Download dynamic videos from specific HTML pages.")
    parser.add_argument('-u', '--urls', nargs='+', help="One or more URLs to process separated by space.")
    parser.add_argument('-f', '--file', type=str, help="Text file containing a list of URLs.")
    
    args = parser.parse_args()
    urls_to_process = []

    if args.urls:
        urls_to_process.extend(args.urls)
        
    if args.file:
        try:
            with open(args.file, 'r') as file:
                urls_to_process.extend([line.strip() for line in file if line.strip()])
        except Exception as e:
            print(f"[-] Error reading file {args.file}: {e}")
            sys.exit(1)

    if not urls_to_process:
        print("[-] No URLs provided. Use -u or -f to provide URLs.")
        parser.print_help()
        sys.exit(1)

    urls_to_process = list(dict.fromkeys(urls_to_process))
    total_files = len(urls_to_process)
    
    print(f"Found {total_files} URL(s) to process.\n")
    
    for index, page_url in enumerate(urls_to_process, start=1):
        # Extract data using the headless browser
        video_url, file_name, cookies = extract_metadata(page_url)
        
        if video_url and file_name:
            # Download using requests, passing the browser's cookies
            download_video(video_url, file_name, cookies, index, total_files)

if __name__ == "__main__":
    main()
