import os
import tbapy

tba = tbapy.TBA(os.getenv("TBA_KEY"))

for event in tba.events(year=2019):
    if event['event_type'] in range(0, 10):
        for match in tba.event_matches(event['key']):
            if