#!/usr/bin/python
"""
Created by senalw on 10/1/2018.
"""

from stat_builders.Extractor import Builder
from enums.FILE_TYPE_ENUM import FileTypeEnum
from enums.STAT_TYPE_ENUM import StatTypeEnum


class MachineIOStatBuilder(Builder):

    def __init__(self, machineName, statName,option):
        self.machineName = machineName
        self.statName = statName
        self.option = option

    def getComponentName(self):
        pass

    def getStatType(self):
        return StatTypeEnum.MACHINE_IO_STAT

    def getStatName(self):
        return self.statName

    def getDescription(self):
        pass

    def getFileType(self):
        return FileTypeEnum.GSD

    def getMachineName(self):
        return self.machineName

    def getColumns(self):
        return "Time,Disk,Reads,ReadRate,Writes,WriteRate,AvgQSize,AvgWaite,AvgSrvceTime,Machine"

    def getTableName(self):
        return "MachineIO"

    def isMultipleStat(self):
        return True

    def getOption(self):
        return self.option


