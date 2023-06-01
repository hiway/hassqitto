import hassquitto as hq
import logging

# Enable logging
logging.getLogger("hassquitto").setLevel(logging.DEBUG)

# Define message.
MESSAGE = "Hello, World!"


# Define the device.
class Device(hq.Device):
    greet = hq.Button(name="Greet")
    message = hq.Text(name="Message")


# Instantiate the device.
device = Device(name="Example Button Entity")


# Handler for button click event.
@device.greet.on_click
def greet_on_click(_state):
    print("Greet button clicked!")

    # Publish message.
    global MESSAGE
    device.message.publish_state(MESSAGE)

    # Toggle message.
    MESSAGE = "Hello, World!" if MESSAGE == "Goodbye, World!" else "Goodbye, World!"


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
    # Set device as available and online.
    device.set_available()
    device.set_online()

    # Loop forever.
    device.run()

except KeyboardInterrupt:
    # Wait for Ctrl+C.
    pass

finally:
    # Remove example device from Home Assistant.
    device.destroy_discovery()

    # Disconnect from MQTT.
    device.disconnect()
