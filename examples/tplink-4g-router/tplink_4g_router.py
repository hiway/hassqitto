import logging
import platform
import time
import threading
from dataclasses import dataclass
from typing import Iterable
from os import environ

import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import hassquitto as hq


# Enable logging
logger = hq.logging.get_logger(__name__)
logging.getLogger(__name__).setLevel(logging.DEBUG)
logging.getLogger("hassquitto").setLevel(logging.DEBUG)


HEADLESS = environ.get("HEADLESS", "true").lower() == "true"
ROUTER_URL = environ.get("ROUTER_URL", "http://192.168.0.1/")
ROUTER_PASSWORD = environ.get("ROUTER_PASSWORD", "admin")
MQTT_HOST = environ.get("MQTT_HOST", "homeassistant.local")
MQTT_PORT = int(environ.get("MQTT_PORT", 1883))
MQTT_USERNAME = environ.get("MQTT_USERNAME", "example")
MQTT_PASSWORD = environ.get("MQTT_PASSWORD", "example")


def firefox_binary() -> str:
    system = platform.system()
    if system == "FreeBSD":
        return "/usr/local/bin/firefox"
    elif system == "Linux":
        return "/usr/bin/firefox"
    elif system == "Darwin":
        return "/Applications/Firefox.app/Contents/MacOS/firefox-bin"
    else:
        raise NotImplementedError(f"Unsupported system: {system}")


@dataclass
class Message:
    sender: str
    timestamp: str
    text: str


@dataclass
class Status:
    data_used_monthly: str
    signal_strength: int
    internet_status: str
    ipv4_address: str
    ipv6_address: str


class TPLink4GRouterAPI:
    """TP Link 4G + WiFi Router WebUI API"""

    def __init__(
        self,
        router_url: str,
        router_password: str,
        headless=False,
    ) -> None:
        self.router_url = router_url
        self.router_password = router_password
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")
        self.driver = webdriver.Firefox(
            firefox_binary=firefox_binary(),
            # service=FirefoxService(firefox_binary()),
            options=options,
        )
        logger.info("Firefox WebDriver initialized")

    def _wait_until_id(self, value, timeout: int = 10) -> WebElement:
        return WebDriverWait(self.driver, timeout=timeout).until(
            EC.presence_of_element_located((By.ID, value))
        )

    def _click_element(self, by, value, timeout: int = 10) -> None:
        element = (WebDriverWait(self.driver, timeout=timeout)).until(
            EC.presence_of_element_located((by, value))
        )
        element.click()

    def _get_value_of_id(self, element_id):
        element = self._wait_until_id(element_id)
        return element.get_attribute("value")

    def open_browser(self):
        """Open URL in browser"""
        logger.info("Opening browser: %s", self.router_url)
        self.driver.start_client()
        self.driver.get(self.router_url)

    def close_browser(self) -> None:
        """Close browser"""
        logger.info("Closing browser.")
        self.driver.stop_client()
        # self.driver.quit()

    def login(self) -> None:
        """Log in to router web UI"""
        self.driver.find_element(By.ID, "pc-login-password").clear()
        self.driver.find_element(By.ID, "pc-login-password").send_keys(
            self.router_password
        )
        logger.info("Entered password, waiting for admin page to load.")
        self._wait_until_id("pc-login-btn")
        self._click_element(By.ID, "pc-login-btn")
        logger.info("Logged in to admin page, waiting for asynchronous page load.")
        time.sleep(5)
        logger.info("Verifying login was sucessful...")
        try:
            self.driver.find_element(By.ID, "basic")
            logger.info("Login successful")
        except NoSuchElementException:
            logger.warning("Login not successful?")
            try:
                self._click_element(By.ID, "confirm-yes")
                logger.info("Login successful!")
            except NoSuchElementException as exc:
                raise exc
        finally:
            time.sleep(10)  # Home page takes longer to render after login

    def logout(self):
        """Log out from router web UI"""
        logger.info("Logging out.")
        self._click_element(By.ID, "topLogout")
        time.sleep(5)
        self._click_element(
            By.XPATH,
            '//button[contains(@class, "btn-msg-ok") and '
            'contains(@class, "btn-confirm")]',
        )
        time.sleep(5)

    def open_basic_home_page(self) -> None:
        """Open basic home page"""
        logger.info("Navigating to basic home page")
        self._click_element(By.ID, "basic")
        time.sleep(10)

    def open_sms_page(self) -> None:
        """Open SMS page"""
        logger.info("Navigating to SMS page.")
        self._click_element(By.ID, "map_icon_sms")
        time.sleep(5)

    def open_sms_detail_page(self, index=1) -> None:
        """Open SMS detail page"""
        logger.info("Navigating to SMS detail page.")
        self._click_element(By.ID, f"msg_{index}")
        time.sleep(5)

    def open_sms_detail_next_page(self) -> None:
        """Open SMS detail next page"""
        logger.info("Navigating to next SMS detail page.")
        self._click_element(By.ID, "divNextBtn")
        time.sleep(5)

    def get_sms(self) -> Message:
        """Get data from sms detail page"""
        logger.info("Reading SMS details.")

        msg_content = self._wait_until_id("msgContent")
        text = msg_content.get_attribute("innerHTML")
        timestamp = self.driver.find_element(By.ID, "recvTime").get_attribute(
            "innerHTML"
        )
        sender = self.driver.find_element(By.ID, "phoneNumber").get_attribute(
            "innerHTML"
        )
        if not (text or sender or timestamp):
            logger.info("No more messages.")
            raise IndexError("No more messages.")
        return Message(sender=sender, timestamp=timestamp, text=text)

    def unread_messages(self, limit: int = 10) -> list[Message]:
        """Iterate over unread messages"""
        self.open_sms_page()
        messages = []
        try:
            self.open_sms_detail_page()
        except TimeoutException as exc:
            logger.info("No new messages.")
            raise IndexError("No new messages.") from exc
        messages.append(self.get_sms())

        for _ in range(limit - 1):
            self.open_sms_detail_next_page()
            try:
                messages.append(self.get_sms())
            except IndexError:
                break

        return messages

    def get_status(self) -> Status:
        """Get basic status of router"""
        internet_status = self._get_value_of_id("internetStatus")
        ip_addresses = self._get_value_of_id("internetIp")
        if "/" in ip_addresses:
            ipv4_address = ip_addresses.split("/")[0].strip()
            ipv6_address = ip_addresses.split("/")[1].strip()
        else:
            ipv4_address = ip_addresses.strip()
            ipv6_address = ""

        signal_strength = self._get_value_of_id("signalStrength2")
        data_used_monthly = self._get_value_of_id("data2")

        internet_status = internet_status.lower()
        signal_strength = signal_strength.removesuffix("%")
        data_used_monthly = data_used_monthly.removesuffix("GB (Monthly Used)")

        if data_used_monthly == "--":
            time.sleep(5)
            return self.get_status()

        return Status(
            internet_status=internet_status,
            ipv4_address=ipv4_address,
            ipv6_address=ipv6_address,
            signal_strength=int(signal_strength),
            data_used_monthly=data_used_monthly,
        )

    def reboot_router(self):
        """Reboot router"""
        self._click_element(By.XPATH, '//*[@id="topReboot"]')
        self._click_element(
            By.XPATH, "/html/body/div[8]/div/div[4]/div/div[2]/div/div[2]/button"
        )


class TPLink4GRouter(hq.Device):
    data_used_monthly = hq.Sensor(
        name="Data used (monthly)",
        device_class="data_size",
        unit_of_measurement="GB",
    )
    signal_strength = hq.Sensor(
        name="Signal strength",
        unit_of_measurement="%",
    )
    internet_status = hq.Sensor(
        name="Internet status",
    )
    ipv4_address = hq.Sensor(
        name="IPv4 Address",
    )
    ipv6_address = hq.Sensor(
        name="IPv6 Address",
    )
    text_message = hq.Sensor(
        name="Text message",
    )
    reboot_router = hq.Button(name="Reboot Router")
    status = hq.Sensor(name="Script status", entity_category="diagnostic")
    router_url = hq.Sensor(name="Router URL", entity_category="diagnostic")


api = TPLink4GRouterAPI(
    router_url=ROUTER_URL,
    router_password=ROUTER_PASSWORD,
    headless=HEADLESS,
)

device = TPLink4GRouter(name="TPLink 4G Router")
device.model = "Archer MR200 4G + WiFi Modem"
device.manufacturer = "TP-Link"


@device.on_connected
@device.on_interval(minutes=5)
def on_connected():
    try:
        device.status.publish_state("querying")
        api.open_browser()
        api.login()
        status = api.get_status()

        device.data_used_monthly.publish_state(status.data_used_monthly)
        device.signal_strength.publish_state(status.signal_strength)
        device.internet_status.publish_state(status.internet_status)
        device.ipv4_address.publish_state(status.ipv4_address)
        device.ipv6_address.publish_state(status.ipv6_address)
    except Exception as exc:
        logger.error(exc)
        device.status.publish_state("error")

    try:
        for sms in reversed(api.unread_messages(limit=3)):
            device.text_message.publish_state(
                f"{sms.text} [{sms.sender} @{sms.timestamp}]"
            )
            time.sleep(1)

        api.logout()
        device.status.publish_state("idle")
    except Exception as exc:
        logger.error(exc)
        device.status.publish_state("idle")
    finally:
        api.logout()
        api.close_browser()


@device.reboot_router.on_click
def reboot_router_on_click(_state):
    reboot_thread = threading.Thread(target=reboot_router)
    reboot_thread.start()

    device.status.publish_state("rebooting router")
    device.set_not_available()
    device.set_offline()


def reboot_router():
    try:
        api.open_browser()
        api.login()
        api.reboot_router()
        api.close_browser()
    except Exception as exc:
        logger.error(exc)
        device.status.publish_state("error")
    finally:
        try:
            api.close_browser()
        except Exception as exc:
            logger.error(exc)

        logger.info("Checking if router is back online.")
        time.sleep(20)
        while True:
            try:
                _ = requests.get(ROUTER_URL, timeout=10)
                device.set_available()
                device.set_online()
                device.status.publish_state("idle")
                break
            except Exception as exc:
                logger.error(exc)
                time.sleep(10)


try:
    # Connect to MQTT.
    device.connect(
        host=MQTT_HOST,  # MQTT host.
        port=MQTT_PORT,  # MQTT port.
        username=MQTT_USERNAME,  # MQTT username.
        password=MQTT_PASSWORD,  # MQTT password.
    )
    # Set device as available and online.
    device.set_available()
    device.set_online()
    device.status.publish_state("starting")
    device.router_url.publish_state(ROUTER_URL)

    # Loop forever.
    device.run()

except KeyboardInterrupt:
    # Wait for Ctrl+C.
    pass

finally:
    device.status.publish_state("stopped")
    # Remove example device from Home Assistant.
    # device.destroy_discovery()

    # Disconnect from MQTT.
    device.disconnect()
