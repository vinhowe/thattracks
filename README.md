# thattracks
Basic tracking pixel server that sends me Twilio text whenever it's accessed.

## Setup
Install dependencies with `pip install -r requirements.txt`. You may want to do this in a virtual environment.

Rename `example_twilio_secrets.json` to `twilio_secrets.json`, and `example_config.json` to `config.json`.

Sign up for an account on Twilio, and copy the account SID and auth token into `twilio_secrets.json`. Then copy your SMS sender number and personal number into `config.json`.

Because the notifications are generated server-side, you'll also probably want to set `timezone` in `config.json` to your timezone. If you're not sure what your timezone is, check out [heyalexej's list of pytz timezones](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568).

## Usage
In the page (or email) where you want notifications, embed an HTML `img` element pointing to `https://{yourhostname}/track/{unique tracking id}`
