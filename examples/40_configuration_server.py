import asyncio
import logging
import hassquitto as hq
from quart import Quart, request, render_template_string, redirect, url_for

logging.getLogger("hassquitto").setLevel(logging.DEBUG)

# Create a new device with the name "Example Device"
device = hq.Device(name="Example Device")

# To see the device, open the following URL in browser:
#   http://homeassistant.local:8123/config/devices/dashboard

# Configuration dictionary
config = {"status": ""}

# Quart app URL
device.configuration_url = "http://localhost:8789/config"

# Quart app
app = Quart(__name__)


@app.before_serving
async def on_startup():
    # Defaults: host=homeassistant.local, port=1883
    await device.connect(username="example", password="example")
    await device.status("See Device Configuration URL", retain=True)

    # Start scheduler
    await device.start()


@app.after_serving
async def on_shutdown():
    # Reset status
    await device.status("", retain=True)

    # Remove the device from Home Assistant
    await device.destroy()
    await device.disconnect()
    await device.stop()


# Route to update the configuration
@app.route("/config", methods=["POST"])
async def update_config():
    # Update the configuration dictionary with the new values
    form = await request.form
    for key in form:
        config[key] = form[key]
        if key == "status":
            await device.status(form[key])
            await device.status_set_confirm()

    # Redirect back to the configuration page
    return redirect(url_for("config_page"))


# Route to display the configuration page
@app.route("/config", methods=["GET"])
async def config_page():
    status = await device.status()
    if status is not None:
        config["status"] = status

    return await render_template_string(
        """<!DOCTYPE html>
<html>
<head>
    <title>Device Configuration</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f2f2f2;
        }
        h1 {
            text-align: center;
            margin-top: 50px;
        }
        form {
            margin: 0 auto;
            width: 50%;
            background-color: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 0px 10px #ccc;
        }
        label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
        }
        input[type=text] {
            width: 100%;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            margin-bottom: 20px;
            box-sizing: border-box;
        }
        input[type=submit] {
            background-color: #4CAF50;
            color: #fff;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        input[type=submit]:hover {
            background-color: #3e8e41;
        }
    </style>
</head>
<body>
    <h1>Device Configuration</h1>
    <form method="POST" action="{{ url_for('update_config') }}">
        {% for key, value in config.items() %}
            <label for="{{ key }}">{{ key }}</label>
            <input type="text" id="{{ key }}" name="{{ key }}" value="{{ value }}" {% if loop.first %}autofocus{% endif %}><br>
        {% endfor %}
        <input type="submit" value="Save">
    </form>
</body>
</html>
""",
        config=config,
    )


if __name__ == "__main__":
    app.run(port=8789)
