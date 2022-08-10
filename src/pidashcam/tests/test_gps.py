#! /usr/bin/python

from unittest import TestCase

import pidashcam

class TestGPS(TestCase):
    def gpsd_is_object(self):
        g = GPSPoller()
        self.assertTrue(isobject(g))
