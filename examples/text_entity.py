import time
import hassquitto as hq
import logging

logging.getLogger("hassquitto").setLevel(logging.DEBUG)


class Device(hq.Device):
    greeting = hq.Text(name="Greeting", entity_category="diagnostic")


device = Device(name="Example Text Entity")


if __name__ == "__main__":
    # To see the device in Home Assistant, open the following URL:
    # http://homeassistant.local:8123/config/devices/dashboard
    # look for "Example Text Entity" and click on the name.

    # Refresh the Device page if all entities don't show up.

    # Connect to MQTT.
    device.connect(
        host="homeassistant.local",
        port=1883,  # MQTT port.
        username="example",  # MQTT username.
        password="example",  # MQTT password.
    )
    device.set_available()
    device.set_online()

    # Wait for yourself to click on the device in Home Assistant.
    time.sleep(10)

    # Set the text entity.
    device.greeting.publish_state("Hello, World!")
    time.sleep(10)
    device.greeting.publish_state("Goodbye, World!")

    # Device is offline.
    device.set_offline()
    device.set_not_available()
    time.sleep(1)

    # Remove the example device from Home Assistant.
    device.destroy_discovery()

    # Disconnect from MQTT.
    device.disconnect()
