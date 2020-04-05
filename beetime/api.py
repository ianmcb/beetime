import json
from urllib.parse import urlencode

import requests
from requests.compat import urljoin


def get_api(user, token, slug):
    """Get and return the datapoints for a given goal from Beeminder."""
    return api_call("GET", user, token, slug, None, None)


def send_api(user, token, slug, data, did=None):
    """Send or update a datapoint to a given Beeminder goal. If a
    datapoint ID (did) is given, the existing datapoint is updated.
    Otherwise a new datapoint is created. Returns the datapoint ID
    for use in caching.
    """
    response = api_call("POST", user, token, slug, data, did)
    return json.loads(response)["id"]


def api_call(method, user, token, slug, data, did):
    """Prepare an API request.

    Based on code by: muflax <mail@muflax.com>, 2012
    """

    cmd = "datapoints"
    base = f"https://www.beeminder.com/api/v1/users/{user}/goals/{slug}/"
    if method == "POST" and did is not None:
        url = urljoin(base, f"{cmd}/{did}.json")
        method = "PUT"
    else:
        url = urljoin(base, f"{cmd}.json")

    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Accept": "text/plain",
    }
    params = urlencode({"auth_token": token} if method == "GET" else data)

    response = requests.request(method, url, headers=headers, data=params)
    response.raise_for_status()
    return response.text
