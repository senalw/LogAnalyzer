#!/usr/bin/python
"""
Created by senalw on 9/14/2018.
"""
from stat_builders.Extractor import Builder
from enums.FILE_TYPE_ENUM import FileTypeEnum
from enums.STAT_TYPE_ENUM import StatTypeEnum


class MachineCPUStatBuilder(Builder):

    def __init__(self, machineName, cpuStatName, option):
        self.cpuStatName = cpuStatName
        self.machine = machineName
        self.option = option

    def getMachineName(self):
        return self.machine

    def getStatType(self):
        return StatTypeEnum.MACHINE_CPU_STAT

    def getFileType(self):
        return FileTypeEnum.GSD

    def getComponentName(self):
        pass

    def getStatName(self):
        return self.cpuStatName

    def getDescription(self):
        pass

    def getColumns(self):
        return "Time,CPU_percentage,Machine"

    def getTableName(self):
        return "MachineCPU"

    def isMultipleStat(self):
        return False

    def getOption(self):
        return self.option
