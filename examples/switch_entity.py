import hassquitto as hq
import logging

# Enable logging
logging.getLogger("hassquitto").setLevel(logging.DEBUG)


# Define the device.
class Device(hq.Device):
    shout = hq.Switch(name="Shout")  # , initial_state="ON")


# Instantiate the device.
device = Device(name="Example Switch Entity")


# Handler for switch state change event.
@device.shout.on_change
def shout_on_change(state):
    print("Shout switch changed to:", state)


# To see the device in Home Assistant, open the following URL:
# http://homeassistant.local:8123/config/devices/dashboard
# look for "Example Switch Entity" and click on the name.

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
