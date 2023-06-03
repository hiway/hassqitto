import logging
import hassquitto as hq

logging.getLogger("hassquitto").setLevel(logging.DEBUG)

# Create a new device with the name "Example Device"
device = hq.Device(name="Example Device")

# To see the device, open the following URL in browser:
#   http://homeassistant.local:8123/config/devices/dashboard

counter = 0


# Function to run when the device connects to the MQTT broker
@device.on_interval(seconds=2)
def tick():
    global counter
    print(f"Tick {counter}")

    # Update device status
    device.status(f"Tick {counter}")
    counter += 1


try:
    # Run the device with MQTT username and password "example"
    # Default MQTT broker: homeassistant.local:1883
    device.run(
        username="example",
        password="example",
    )
except KeyboardInterrupt:
    pass
finally:
    # Remove the device from Home Assistant
    device.destroy()
    device.stop()
