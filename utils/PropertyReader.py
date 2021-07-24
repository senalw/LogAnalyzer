#!/usr/bin/python
"""
Created by senalw on 9/15/2018.
"""

from utils.Singleton import Singleton
from settings import ROOT_DIR
import os


class PropertyReader(Singleton):
    keys = {}

    def __init__(self):
        self.readPropertyFile()

    def readPropertyFile(self):
        try:
            separator = "="
            with open(os.path.join(ROOT_DIR,'resources/configs')) as file:
                for line in file:
                    if separator in line:
                        name, value = line.split(separator, 1)
                        self.keys[name.strip()] = value.strip()
        except Exception as e:
            print(e)
            raise Exception(e.message)

    def getProperty(self, propertyName):
        property = self.keys.get(propertyName)
        if property is not None:
            return property
        else:
            raise Exception("Unable to find property value for the property name %s" % (propertyName))
