#!/usr/bin/python
"""
Created by senalw on 9/14/2018.
"""
from stat_builders.Extractor import Builder
from enums.FILE_TYPE_ENUM import FileTypeEnum
from enums.STAT_TYPE_ENUM import StatTypeEnum

class ProcessMemStatBuilder(Builder):

    def __init__(self, processName, memStatName,option):
        self.memStatName = memStatName
        self.componentName = processName
        self.option = option

    def getStatName(self):
        return self.memStatName

    def getStatType(self):
        return StatTypeEnum.PROCESS_MEM_STAT

    def getFileType(self):
        return FileTypeEnum.GSD

    def getComponentName(self):
        return self.componentName

    def getDescription(self):
        pass

    def getMachineName(self):
        pass

    def getColumns(self):
        return "Time,ProcessMemory,Component,MachineName"

    def getTableName(self):
        return "ProcessMemory"

    def isMultipleStat(self):
        return False

    def getOption(self):
        return self.option