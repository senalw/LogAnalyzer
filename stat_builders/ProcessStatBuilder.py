#!/usr/bin/python
"""
Created by senalw on 9/14/2018.
"""

from stat_builders.Extractor import Builder
from enums.FILE_TYPE_ENUM import FileTypeEnum
from enums.STAT_TYPE_ENUM import StatTypeEnum


class ProcessStatBuilder(Builder):

    def __init__(self, componentName, statName, description, option):
        self.componentName = componentName
        self.statName = statName
        self.description = description
        self.option = option

    def getComponentName(self):
        return self.componentName

    def getStatName(self):
        return self.statName

    def getDescription(self):
        return self.description

    def getStatType(self):
        return StatTypeEnum.PROCESS_STAT

    def getFileType(self):
        return FileTypeEnum.SSM_STAT

    def getMachineName(self):
        pass

    def getColumns(self):
        return "Time,ProcessStat,Component,StatName,Description"

    def getTableName(self):
        return "ProcessSSMStat"

    def isMultipleStat(self):
        return False

    def getOption(self):
        return self.option
