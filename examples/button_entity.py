import time
import hassquitto as hq
import logging

logging.getLogger("hassquitto").setLevel(logging.DEBUG)


class Device(hq.Device):
    greet = hq.Button(name="Greet")
    message = hq.Text(name="Message")


device = Device(name="Example Button Entity")
MESSAGE = "Hello, World!"


@device.greet.on_click
def greet_on_click(_state):
    global MESSAGE

    print("Greet button clicked!")

    device.message.publish_state(MESSAGE)

    # Toggle the message.
    MESSAGE = "Hello, World!" if MESSAGE == "Goodbye, World!" else "Goodbye, World!"


if __name__ == "__main__":
    # To see the device in Home Assistant, open the following URL:
    # http://homeassistant.local:8123/config/devices/dashboard
    # look for "Example Button Entity" and click on the name.

    # Refresh the Device page if all entities don't show up.

    try:
        # Connect to MQTT.
        device.connect(
            host="homeassistant.local",
            port=1883,  # MQTT port.
            username="example",  # MQTT username.
            password="example",  # MQTT password.
        )
        device.set_available()
        device.set_online()

        device.run()
    except KeyboardInterrupt:
        pass
    finally:
        device.destroy_discovery()
        device.disconnect()
