#!/usr/bin/python
from doppelserver.models import StaticSample, load_session, HourSample
from sqlalchemy import func
import datetime

session = load_session()

def data_for_hour(start):
    end = start + datetime.timedelta(hours=1)
    # return the average of all data for an hour, starting from start
    # note the parentheses around the comparisons in the filter; this is
    # required because & binds tighter than comparison!
    return session.query(StaticSample.sensor_id, func.avg(StaticSample.data)) \
        .filter((StaticSample.time >= start) & (StaticSample.time < end)) \
        .group_by(StaticSample.sensor_id).all()

if __name__ == "__main__":
    now = datetime.datetime.now()
    last_hour = datetime.datetime.now() - datetime.timedelta(hours=1,
                                                             minutes=now.minute,
                                                             seconds=now.second,
                                                             microseconds=now.microsecond)
    try:
        for (id, datum) in data_for_hour(last_hour):
            session.add(HourSample(sensor_id=id, time=last_hour, data=datum))
    except IntegrityError:
        session.rollback()
