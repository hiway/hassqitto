import time
import hassquitto as hq
import logging

logging.getLogger("hassquitto").setLevel(logging.DEBUG)


class Hello(hq.Device):
    pass


hello = Hello(name="Example Availability")


if __name__ == "__main__":
    # To see the device in Home Assistant, open the following URL:
    # http://homeassistant.local:8123/config/devices/dashboard
    # look for "Example Availability" and click on the name.

    # Connect to MQTT.
    hello.connect(
        host="homeassistant.local",
        port=1883,  # MQTT port.
        username="example",  # MQTT username.
        password="example",  # MQTT password.
    )

    # Wait for yourself to click on the device in Home Assistant.
    time.sleep(10)

    # Device is available.
    hello.set_available()

    for i in range(5):
        # Device is online.
        hello.set_online()
        time.sleep(3)

        # Device is offline.
        hello.set_offline()
        time.sleep(3)

    # Device is not available.
    hello.set_not_available()
    time.sleep(5)

    # Remove the example device from Home Assistant.
    hello.destroy_discovery()

    # Disconnect from MQTT.
    hello.disconnect()
