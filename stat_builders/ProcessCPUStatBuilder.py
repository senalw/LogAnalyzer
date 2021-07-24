#!/usr/bin/python
"""
Created by senalw on 9/14/2018.
"""
from stat_builders.Extractor import Builder
from enums.FILE_TYPE_ENUM import FileTypeEnum
from enums.STAT_TYPE_ENUM import StatTypeEnum


class ProcessCPUStatBuilder(Builder):

    def __init__(self, processName, cpuStatName, option):
        self.cpuStatName = cpuStatName
        self.componentName = processName
        self.option = option

    def getStatName(self):
        return self.cpuStatName

    def getComponentName(self):
        return self.componentName

    def getStatType(self):
        return StatTypeEnum.PROCESS_CPU_STAT

    def getFileType(self):
        return FileTypeEnum.GSD

    def getDescription(self):
        pass

    def getMachineName(self):
        pass

    def getColumns(self):
        return "Time,ProcessCPU,Component,Machine"

    def getTableName(self):
        return "ProcessCPU"

    def isMultipleStat(self):
        return False

    def getOption(self):
        return self.option
