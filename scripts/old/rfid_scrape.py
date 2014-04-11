#!/usr/bin/python

from doppelserver.models import Event, load_session
from datetime import datetime
import json, urllib, time
import doppelserver.utils as utils
rooms = [274,333,348,445,474,514,548,674]

if __name__ == "__main__":
    s = load_session()
    sensors = {}
    for room in rooms:
        sensors[room] = utils.lookup_sensor(s, "rfid_%d" % room, "rfid")

    while True:
        now = datetime.now()
        for room in rooms:
            url = "http://tagnet.media.mit.edu/getRfidUserProfiles?readerid=e14-%d-1" % room
            tags = json.load(urllib.urlopen(url))["tags"]
            event_json = {"tags": []}
            for tag in tags:
                tag_json = {}
                for k in "first_name", "last_name", "id", "picture_url", "user_name":
                    if k in tag:
                        tag_json[k] = tag[k]
                if tag_json:
                    event_json["tags"].append(tag_json)
            
            # in order to save on row space, we deduplicate empty entries
            last_entry = s.query(Event).filter_by(sensor=sensors[room]).order_by(Event.time.desc()).first()
            if last_entry.json["tags"] == [] and tags == []:
                continue
            
            s.add(Event(sensor=sensors[room], time=datetime.now(), json=event_json))
            s.commit()
        time.sleep(4)
