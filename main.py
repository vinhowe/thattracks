from flask import Flask, send_file, request
from base64 import b64decode
from io import BytesIO
from user_agents import parse
from json import load
from twilio.rest import Client
import geoip2.database
from geoip2.errors import AddressNotFoundError
from time import strftime, tzset
import os
import subprocess

app = Flask(__name__)

# Load Twilio secrets from twilio_secrets.json
twilio_secrets = None

with open('twilio_secrets.json') as twilio_secrets_file:
    twilio_secrets = load(twilio_secrets_file)

# Load config from config.json
config = None

with open('config.json') as config_file:
    config = load(config_file)

# Set timezone
os.environ['TZ'] = config['timezone']
tzset()

# Set transparent pixel information data
# We do this with a base64 string to avoid being dependent on a 1x1 png
base64_pixel = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkqAcAAIUAgUW0RjgAAAAASUVORK5CYII="
pixel_data = b64decode(base64_pixel)

# Set up Twilio
client = Client(twilio_secrets['account_sid'], twilio_secrets['auth_token'])

# Read GeoIP2 database
geoip2_reader = geoip2.database.Reader('geolite2/GeoLite2-City.mmdb')


def ip_location_summary(ip_addr):
    try:
        location_info = geoip2_reader.city(ip_addr)
    except AddressNotFoundError as e:
        return "location unknown"
    country = location_info.country.name
    subdivision = location_info.subdivisions.most_specific.name
    city = location_info.city.name
    return f"{city}, {subdivision}, {country}"


def notify_sms(message_body):
    print(message_body)
    message = client.messages \
        .create(
            body=message_body,
            from_=config['sms_sender'],
            to=config['sms_recipient']
        )


def generate_notification_body(tracking_id, ip_addr, user_agent):
    user_agent_string = str(parse(str(user_agent)))
    coarse_location = ip_location_summary(ip_addr)
    time = strftime("%H:%M")

    return f"Tracking pixel request for '{tracking_id}': {ip_addr} at {time}\n" \
           f"{coarse_location}\n" \
           f"{user_agent_string}"


@app.route('/')
def info_root():
    # FIXME: Make this serve a pretty informative webpage or something
    return "Pixel tracking server."


@app.route('/track/<tracking_id>')
def track(tracking_id):
    print(request.remote_addr)
    print(parse(str(request.user_agent)))

    message = generate_notification_body(
        tracking_id, request.remote_addr, parse(str(request.user_agent)))

    notify_sms(message)
    return send_file(BytesIO(pixel_data), mimetype='image/png')


if __name__ == '__main__':
    app.run(host="0.0.0.0")
