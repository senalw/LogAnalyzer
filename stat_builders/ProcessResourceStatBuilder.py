#!/usr/bin/python
"""
Created by senalw on 9/18/2018.
"""
from stat_builders.Extractor import Builder
from enums.FILE_TYPE_ENUM import FileTypeEnum
from enums.STAT_TYPE_ENUM import StatTypeEnum


class ProcessResoureStatBuilder(Builder):

    def __init__(self, processName, StatName, option):
        self.StatName = StatName
        self.componentName = processName
        self.option = option

    def getStatName(self):
        return self.StatName

    def getStatType(self):
        return StatTypeEnum.PROCESS_RESOURCE_USAGE_STAT

    def getFileType(self):
        return FileTypeEnum.GSD

    def getComponentName(self):
        return self.componentName

    def getDescription(self):
        pass

    def getMachineName(self):
        pass

    def getColumns(self):
        return "Time,FileDescriptor,TotalMemory,ResidentMemory,AverageCPU,Component"

    def getTableName(self):
        return "ProcessResourceUsage"

    def isMultipleStat(self):
        return False

    def getOption(self):
        return self.option
