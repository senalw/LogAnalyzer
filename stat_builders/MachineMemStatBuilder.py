#!/usr/bin/python
"""
Created by senalw on 9/14/2018.
"""
from stat_builders.Extractor import Builder
from enums.FILE_TYPE_ENUM import FileTypeEnum
from enums.STAT_TYPE_ENUM import StatTypeEnum


class MachineMemStatBuilder(Builder):

    def __init__(self, machineName, memStatName, option):
        self.memStatName = memStatName
        self.machine = machineName
        self.option = option

    def getMachineName(self):
        return self.machine

    def getStatType(self):
        return StatTypeEnum.MACHINE_MEM_STAT

    def getFileType(self):
        return FileTypeEnum.GSD

    def getComponentName(self):
        pass

    def getStatName(self):
        return self.memStatName

    def getDescription(self):
        pass

    def getColumns(self):
        return "Time,MachineMemory,Machine"

    def getTableName(self):
        return "MachineMemory"

    def isMultipleStat(self):
        return False

    def getOption(self):
        return self.option
