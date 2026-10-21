"""Evaluate any student-collected 0/1 event stream stored in a CSV.

Expected columns: t,event,label (integer t = 0,1,2,...; event,label = 0/1)
Label 1 means the time step belongs to a known positive episode.
Students must label their episodes INDEPENDENTLY of detector predictions.
This is deliberately simple; real sensor data needs preprocessing first.

Example: python -m dionaea.field_data my_observations.csv
"""
import csv
import json
import sys
from pathlib import Path
from .detectors import METHODS, Settings, detect
from .evaluate import evaluate


def read_csv(path: Path):
    events, labels = [], []
    with path.open(newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not {'t','event','label'} <= set(reader.fieldnames):
            raise ValueError('CSV must have columns t,event,label')
        for index, row in enumerate(reader):
            if int(row['t']) != index:
                raise ValueError('t must start at 0 and increment by 1 for every row')
            event, label = int(row['event']), int(row['label'])
            if event not in (0,1) or label not in (0,1):
                raise ValueError('event and label must be 0 or 1')
            events.append(event)
            labels.append(label)
    if not events:
        raise ValueError('CSV has no observations')
    episodes = []
    start = None
    for t, label in enumerate(labels+[0]):
        if label and start is None:
            start=t
        elif not label and start is not None:
            episodes.append({'start':start,'end':t})
            start=None
    if not episodes:
        raise ValueError('Label at least one genuine episode before evaluating')
    return events, episodes


def score_file(path: Path, settings: Settings=Settings()):
    events, episodes = read_csv(path)
    return {'file':str(path), 'length':len(events), 'episodes':episodes,
            'detectors':{name:evaluate(detect(events,name,settings)['alarms'], episodes,len(events))
                         for name in METHODS}}


def main():
    if len(sys.argv)!=2:
        raise SystemExit('Usage: python -m dionaea.field_data observations.csv')
    print(json.dumps(score_file(Path(sys.argv[1])),indent=2))

if __name__=='__main__':
    main()
