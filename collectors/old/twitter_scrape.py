#!/usr/bin/python

from doppelserver.models import *
from time import sleep
from dateutil import tz
import tweepy

def status_to_dict(status):
    return {"screen_name": status.user.screen_name,
            "text": status.text,
            "geo": status.geo}

def make_person(username, realname, location=None):
    user = api.get_user(username)
    group = SensorGroup()
    group.name = realname
    group.type = "person"
    if location:
        (group.building, group.floor, group.room) = parse_location(location[0:3], location[4], location[5:])
    else:
        (group.building, group.floor, group.room) = (None, None, None)
    person = Person()
    person.name = realname
    person.sensor_group = group
    person.twitter_id = user.id
    sensor = Sensor()
    sensor.type = "twitter"
    sensor.group = group
    return person

# this stuff is secret! if we publish the source, we'll need to move this
# into a separate file that doesn't get published
auth = tweepy.OAuthHandler("7k8MLYWH0mFb8TYHlvnlTw", "1No0QY677rtFILj3UUYTNJQTpfUM8VxIby987OM")
auth.set_access_token("335478396-aXGWBh2TX9PjpC1BiiGlK95xTpJVjFRTtaxowhKJ", "8HGeq2s3bk3fM2uUFtAw6fLanRipbzNydLXLR3Hvf0")
api = tweepy.API(auth)
if __name__ == "__main__":
    s = load_session()
    last_id = api.home_timeline(count=1)[0].id

    while True:
        new_tweets = api.home_timeline(since_id=last_id, count=100)
        for tweet in new_tweets:
            user_id = tweet.user.id
            sensor = s.query(Sensor).filter_by(type="twitter").join(SensorGroup, Person) \
                .filter_by(twitter_id=user_id).first()
            creation = tweet.created_at.replace(tzinfo=tz.gettz('UTC'))
            creation = creation.astimezone(tz.gettz('America/New_York'))
            event = Event(sensor=sensor, time=creation, json=status_to_dict(tweet))
            s.add(event)
            last_id = max(last_id, tweet.id)
        s.commit()
        sleep(60)
