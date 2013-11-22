import requests
import logging
import random
import json
import datetime

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_API_URL = 'http://localhost:8000/api/'


def extract_urls(data):
    '''Takes data from a response or part of a response and returns a list of
    all URLs in the response, including any URLs in nested data structures.
    data could be a dictionary or list of dictionaries'''
    urls = []
    if isinstance(data, dict):
        for k, v in data.items():
            if k == "_href":
                logger.debug("found url: %s" % v)
                urls.append(v)
            else:
                urls.extend(extract_urls(v))
        return urls
    elif isinstance(data, list):
        for v in data:
            urls.extend(extract_urls(v))
        return urls

    return urls


def post_site(collection_url):
    new_site = {
        'name': 'Test Site %d' % random.randint(0, 1000000)
    }
    response = requests.post(collection_url, data=json.dumps(new_site)).json()
    logger.info('posted new device to %s' % response['_href'])


def post_device(collection_url):
    new_device = {
        'name': 'Test Device %d' % random.randint(0, 1000000000)
    }
    created_device = requests.post(
        collection_url, data=json.dumps(new_device)).json()
    sensor_collection_url = created_device['sensors']['_href']
    logger.info('posted new device to %s' % created_device['_href'])
    for metric, unit in [('temperature', 'celsius'),
                         ('pressure', 'kPa'),
                         ('setpoint', 'celsius'),
                         ('ambient light', 'lux')]:
        new_sensor = {'metric': metric, 'unit': unit}
        requests.post(sensor_collection_url,
                      data=json.dumps(new_sensor))


def post_sensor_data(collection_url):
    new_data = {
        'timestamp': datetime.datetime.now().isoformat(),
        'value': random.random() * 100
    }
    response = requests.post(collection_url, data=json.dumps(new_data)).json()
    logger.info('posted new sensor data to %s' % response['_href'])


def maybe_post_data(collection_url):
    # this is using specifics of the URL, which is bad news. maybe we should
    # specify the resource type in the _type field?
    for resource_name, probability, post_func in [
            ('sites', 0.1, post_site),
            ('devices', 0.3, post_device),
            ('sensordata', 0.8, post_sensor_data)]:
        if resource_name in collection_url and random.random() < probability:
            post_func(collection_url)


def random_crawl(starting_url):
    url = starting_url
    while True:
        logger.info('GET: %s' % url)
        response = requests.get(url).json()
        if response['_type'] == 'resource-list':
            maybe_post_data(url)
        urls = extract_urls(response)
        url = random.choice(urls)


if __name__ == '__main__':
    random_crawl(BASE_API_URL + 'sites/2')
