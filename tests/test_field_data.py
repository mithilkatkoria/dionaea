from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from dionaea.field_data import read_csv, score_file

class FieldDataTests(unittest.TestCase):
    def test_csv_episodes(self):
        with TemporaryDirectory() as temp:
            path=Path(temp)/'observations.csv'
            path.write_text('t,event,label\n0,0,0\n1,1,1\n2,1,1\n3,0,0\n4,1,0\n5,1,1\n6,1,1\n')
            events,eps=read_csv(path)
            self.assertEqual(eps,[{'start':1,'end':3},{'start':5,'end':7}])
            self.assertEqual(len(score_file(path)['detectors']),4)

    def test_bad_clock(self):
        with TemporaryDirectory() as temp:
            path=Path(temp)/'bad.csv'
            path.write_text('t,event,label\n0,0,0\n2,1,1\n')
            with self.assertRaises(ValueError):
                read_csv(path)
