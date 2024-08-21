import base64
import io
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.print_page_options import PrintOptions
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from jinja2 import Environment, FileSystemLoader, select_autoescape


sample_data = [
    {
        "bank_name": "Bank of Mars",
        "account_holder": "John Doe",
        "account_number": "1234567890",
        "statement_period_start": "01/01/2024",
        "statement_period_end": "31/01/2024",
        "transactions": [
            {
                "date": "01/01/2024",
                "description": "Deposit",
                "amount": "$1,000.00",
                "balance": "$5,000.00",
            },
            {
                "date": "05/01/2024",
                "description": "Grocery Store",
                "amount": "-$150.00",
                "balance": "$4,850.00",
            },
            {
                "date": "10/01/2024",
                "description": "Restaurant",
                "amount": "-$60.00",
                "balance": "$4,790.00",
            },
            # Add more transactions as needed
        ],
        "spending_labels": [
            "Groceries",
            "Dining",
            "Utilities",
            "Entertainment",
            "Others",
        ],
        "spending_data": [150, 60, 200, 100, 90],
        "current_year": "2024",
    },
    # Add more sample data as needed
]  # 1


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
    options.scale = 0.7
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
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "pageready"))  # 2
        )
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


def render_html_from_template(template_path: Path, data: dict[str, Any]):  # 3
    env = Environment(
        loader=FileSystemLoader(template_path.parent),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template(template_path.name)
    return template.render(data)


@contextmanager
def _write_html_and_delete(html_string: str, temporary_path: Path):  # 4
    temp_file = temporary_path / f"{generate_random_name()}.html"
    temp_file.write_text(html_string)
    try:
        yield temp_file
    finally:
        temp_file.unlink()


if __name__ == "__main__":
    cwd = Path.cwd()
    driver_path = cwd / "selenium-pdf/chromedriver"
    pdf_folder = cwd / "selenium-pdf/pdfs"
    pdf_folder.mkdir(exist_ok=True)

    for data in sample_data:
        html_string = render_html_from_template(
            cwd / "selenium-pdf/templates/statement_of_account.jinja", data
        )
        with _write_html_and_delete(html_string, cwd) as html_file:
            write_pdf(html_file.as_uri(), driver_path, pdf_folder)
