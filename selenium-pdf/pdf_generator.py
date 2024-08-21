import base64
import io
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.remote.webdriver import WebDriver


def _send_cmd(driver: WebDriver, cmd: str, params: dict | None = None):
    """
    Send a command to the browser
    """
    if not params:
        params = {}
    response = driver.command_executor._request(
        "POST",
        f"{driver.command_executor._url}/session/{driver.session_id}/chromium/send_command_and_get_result",
        json.dumps({"cmd": cmd, "params": params}),
    )
    if response.get("status"):
        raise Exception(response.get("value"))
    return response.get("value")


def _generate_print_options() -> dict:
    """Generate print options"""

    options = PrintOptions()
    options.scale = 1
    print_options_dict = options.to_dict()
    print_options_dict["displayHeaderFooter"] = False
    print_options_dict["printBackground"] = True
    print_options_dict["format"] = "A4"
    # You can add more options
    return print_options_dict


@contextmanager
def _launch_headless_chrome(driver_path: str) -> Generator[WebDriver, None, None]:
    """Launch a headless Chrome browser"""

    chrome_service = webdriver.chrome.service.Service(driver_path)
    webdriver_options = ChromeOptions()
    webdriver_options.add_argument("--headless")
    webdriver_options.add_argument("--disable-gpu")
    webdriver_options.add_argument("--no-sandbox")
    webdriver_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=chrome_service, options=webdriver_options)
    try:
        yield driver
    finally:
        driver.quit()


def generate_pdf(uri: str, driver_path: str):
    """Generate a PDF from a webpage or local HTML file"""
    with _launch_headless_chrome(driver_path) as driver:
        driver.get(uri)
        result = _send_cmd(driver, "Page.printToPDF", _generate_print_options())
        data = base64.b64decode(result["data"])
        return io.BytesIO(data)


def generate_random_name():
    import random
    import string

    return "".join(random.choices(string.ascii_lowercase + string.digits, k=8))


def write_pdf(uri: str, driver_path: str, pdf_folder: Path):
    """Write a PDF file to the filesystem"""
    pdf_file = pdf_folder / f"{generate_random_name()}.pdf"
    pdf_file.write_bytes(generate_pdf(uri, driver_path).getvalue())


if __name__ == "__main__":
    cwd = Path.cwd()
    driver_path = cwd / "selenium-pdf/chromedriver"
    pdf_folder = cwd / "selenium-pdf/pdfs"
    pdf_folder.mkdir(exist_ok=True)
    uris = [
        "https://www.google.com",
        "https://www.python.org",
        "https://www.wikipedia.org",
    ]
    for uri in uris:
        write_pdf(uri, driver_path, pdf_folder)
