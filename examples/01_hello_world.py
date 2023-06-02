import hassquitto as hq

# Create a new device with the name "Example Device"
device = hq.Device(name="Example Device")

# To see the device, open the following URL in browser:
#   homeassistant.local:8123/config/devices/dashboard


# Function to run when the device connects to the MQTT broker
@device.on_connect
async def device_connected(device):
    # Update device status
    await device.status("Hello, World!")


try:
    # Run the device with MQTT username and password "example"
    # Default MQTT broker: homeassistant.local:1883
    device.run(
        username="example",
        password="example",
    )
except KeyboardInterrupt:
    # Stop the device when user presses Ctrl+C
    device.stop()
finally:
    # Remove the device from Home Assistant
    device.destroy()