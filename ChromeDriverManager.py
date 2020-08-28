import platform
import os
import requests
import zipfile
import re
from bs4 import BeautifulSoup
from typing import Optional

driver_dir = 'browser_drivers'
os_name_mapping = {'Darwin': 'mac64', 'Windows': 'win32', 'Linux': 'linux64'}
chrome_version = None
os_name = platform.system()
chrome_driver_center_url = "https://chromedriver.chromium.org/downloads"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36",
}

if not os.path.exists(driver_dir):
    os.mkdir(driver_dir)

if os_name == 'Darwin':
    installpath = "/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome"
    chrome_version = os.popen(f"{installpath} --version").read().strip('Google Chrome ').strip()
elif os_name == 'Windows':
    cmd = 'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version '
    chrome_version = os.popen(cmd).read().split()[-1]
elif os_name == 'Linux':
    installpath = "/usr/bin/google-chrome"
    chrome_version = os.popen(f"{installpath} --version").read().strip('Google Chrome ').strip()
else:
    raise NotImplemented(f"Unknown OS '{os_name}'")


def unzip_file(compressed_file: str, target_dir: str) -> None:
    with zipfile.ZipFile(compressed_file, "r") as zip_ref:
        zip_ref.extractall(target_dir)


def download_driver() -> str:
    # find the most relevant driver for current chrome browser
    r = requests.get(chrome_driver_center_url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    chrome_version_series_level3 = chrome_version[:chrome_version.rfind(".")]
    span = soup.find("span", text=re.compile(f"ChromeDriver {chrome_version_series_level3}\.\d+"))
    driver_version_link = span.find("a")["href"]
    most_relevant_driver_series = driver_version_link[driver_version_link.rfind(chrome_version_series_level3):-1]

    # download the most relevant driver
    url = f"https://chromedriver.storage.googleapis.com/{most_relevant_driver_series}/chromedriver_{os_name_mapping[os_name]}.zip"
    print(url)
    r = requests.get(url, headers=headers)
    file_path = os.path.join(driver_dir, f"chromedriver_{os_name_mapping[os_name]}.zip")
    with open(file_path, "wb") as f:
        f.write(r.content)
    return file_path


def find_driver() -> Optional[str]:
    for file_name in os.listdir(driver_dir):
        if file_name.startswith("chromedriver") and not file_name.endswith(".zip"):
            return os.path.join(driver_dir, file_name)
    return None


def get_driver() -> str:
    driver = find_driver()
    if not driver:
        print(f"Did not find driver in {driver_dir}, downloading from Chrome driver website")
        driver_zip = download_driver()
        unzip_file(driver_zip, driver_dir)
    return find_driver()


if __name__ == '__main__':
    driver = get_driver()
    # unzip_file(os.path.join(driver_dir,"chromedriver_linux64.zip"), driver_dir)
