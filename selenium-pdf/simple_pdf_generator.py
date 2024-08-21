import base64
import io
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver


def send_cmd(driver: WebDriver, cmd: str, params: dict | None = None):
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


webdriver = webdriver.Chrome()
webdriver.get("https://www.google.com")
result = send_cmd(webdriver, "Page.printToPDF")
data = base64.b64decode(
    result["data"]
)  # -> base64.b64decode() decodes the base64 encoded data
binary_file = io.BytesIO(data)  # -> io.BytesIO() creates a binary stream
pdf_file = Path.cwd() / "selenium-pdf/sample.pdf"
pdf_file.write_bytes(binary_file.getvalue())  # 4
