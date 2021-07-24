#!/usr/bin/python
"""
Created by senalw on 9/15/2018.
"""

import re
import datetime
import os
from os import walk
from datetime import timedelta
from utils.PropertyReader import PropertyReader
from enums.FILE_TYPE_ENUM import FileTypeEnum
from enums.STAT_TYPE_ENUM import StatTypeEnum
from enums.OUTPUT_TYPE_ENUM import OutputTypeEnum
from utils.Stat import Stat
from utils.Logger import Logger
from utils import CommonUtils
from utils.OutputHandler import OutputHandler
from model.ResourceUsage import ResourceUsage


class LogReader:

    def __init__(self, extractor, outputType):
        self.propertyReader = PropertyReader()
        self.logPath = self.propertyReader.getProperty("LOG_FILE_LOC")
        self.timeSeriesFormat = self.propertyReader.getProperty("TIME_SERIES_FORMAT")
        statTimeDeltaOffset = str(self.propertyReader.getProperty("STAT_INSERT_TIME_DELTA_OFFSET")).split(":")
        self.hours = statTimeDeltaOffset[0]
        self.minutes = statTimeDeltaOffset[1]
        self.seconds = statTimeDeltaOffset[2]
        self.extractor = extractor
        self.outputType = outputType
        self.fileRegex = None
        self.stat = Stat()
        self.machineName = None
        self.logger = Logger()
        self.key = None
        self.freeMem = 0
        self.totalMem = 0
        self.isFoundLine = False

        if self.extractor.getFileType() == FileTypeEnum.GSD:
            self.fileRegex = self.propertyReader.getProperty("GSD_FILE_REGEX")
        elif self.extractor.getFileType() == FileTypeEnum.SSM_STAT:
            self.fileRegex = self.propertyReader.getProperty("SSM_STAT_FILE_REGEX")
        elif self.extractor.getFileType() == FileTypeEnum.SSM_INST_RES:
            self.fileRegex = self.propertyReader.getProperty("SSM_INST_RES_FILE_REGEX")
        else:
            raise Exception("File type[%s] is not supported!" % (str(self.extractor.getFileType())))
        self.files = self.getLogs()
        self.readFiles()
        if len(self.stat) > 0:
            self.writeOuput()
        else:
            self.logger.log_errors("No extracted data points, check the regex inputs!")
            raise Exception("No extracted data points, check the regex inputs!")

    def getLogs(self):
        fileList = []
        for (dirPath, directories, files) in walk(self.logPath):
            for file in files:
                if re.match(self.fileRegex, file, re.M | re.I) and file not in fileList:
                    fileList.append(os.path.join(dirPath, file))
        fileList.sort()
        return fileList

    def readFiles(self):
        try:
            if len(self.files) == 0:
                raise Exception("No files were loaded, please check the path!")
            for file in self.files:
                self.logger.log_info("Start analyzing %s" % (file))
                if self.extractor.getFileType() == FileTypeEnum.GSD:
                    self.machineName = file.split("\\")[-1].split("/")[-1].split(".")[1]
                openfile = open(file, "r")
                for line in openfile:
                    self.processLog(line)
                openfile.close()
        except Exception as e:
            self.logger.log_errors("Unable to analyze log file due to %s" % (e.message))
            raise Exception(e)

    def processLog(self, line):
        if (self.extractor.getFileType() == FileTypeEnum.GSD):
            self.processGSD(line)
        elif (self.extractor.getFileType() == FileTypeEnum.SSM_STAT):
            self.processSSM_STAT(line)
        elif (self.extractor.getFileType() == FileTypeEnum.SSM_INST_RES):
            print("SSM_INST_RES")

    def processGSD(self, line):
        value = None
        if (self.extractor.getStatType() == StatTypeEnum.MACHINE_MEM_STAT):
            if re.match(".*System Memory Information.*", line,
                        re.I | re.M):  # time stamp can be found with this regex line
                self.key = line.split("|")[0]
            elif re.match(".*MemTotal:.*", line, re.I | re.M):
                self.totalMem = int(str(re.findall(r'\b\d+\b', line.split(":")[1].strip()).pop()))
            elif re.match(".*MemFree:.*", line, re.I | re.M):
                self.freeMem = int(str(re.findall(r'\b\d+\b', line.split(":")[1].strip()).pop()))
            if self.totalMem != 0:
                value = str(CommonUtils._getCommonMemModel(str(self.totalMem - self.freeMem) + "K")) + (
                        (",%s") % (self.machineName))

        elif self.extractor.getStatType() == StatTypeEnum.MACHINE_CPU_STAT:
            if re.match(".*Collecting stats...", line, re.I | re.M):  # time stamp can be found with this regex line
                self.key = line.split("|")[0]
            elif re.match(".*MACHINE USAGE.*", line, re.I | re.M):
                result = CommonUtils._extractByRegex("CPU\s+=\s+(\d*.?\d+)", line)
                if result is not None:
                    value = result.split("=")[1].strip() + ((",%s") % (self.machineName))

        elif self.extractor.getStatType() == StatTypeEnum.PROCESS_MEM_STAT or \
                self.extractor.getStatType() == StatTypeEnum.PROCESS_CPU_STAT or self.extractor.getStatType() == \
                StatTypeEnum.PROCESS_RESOURCE_USAGE_STAT:
            if re.match(".*Collecting stats...", line, re.I | re.M):  # time stamp can be found with this regex line
                self.key = line.split("|")[0]
            else:
                resourceUsage = self.getProcessResourceUsage(line)
                if self.extractor.getStatType() == StatTypeEnum.PROCESS_CPU_STAT and resourceUsage is not None:
                    value = ("%s,%s,%s") % (round(sum(resourceUsage.CPU) / len(resourceUsage.CPU), 2),
                                            self.extractor.getComponentName(), self.machineName)
                elif self.extractor.getStatType() == StatTypeEnum.PROCESS_MEM_STAT and resourceUsage is not None:
                    if self.extractor.getStatName() == "1":
                        value = CommonUtils._getCommonMemModel(resourceUsage.totalMemory) + (
                                (",%s,%s") % (self.extractor.getComponentName(), self.machineName))
                    elif self.extractor.getStatName() == "2":
                        value = CommonUtils._getCommonMemModel(resourceUsage.residentMemory) + (
                                (",%s,%s") % (self.extractor.getComponentName(), self.machineName))
                elif self.extractor.getStatType() == StatTypeEnum.PROCESS_RESOURCE_USAGE_STAT and resourceUsage is not None:
                    cpu = resourceUsage.CPU
                    value = (("%s,%s,%s,%s,%s") % (
                        resourceUsage.fileDescriptor, CommonUtils._getCommonMemModel(resourceUsage.totalMemory),
                        CommonUtils._getCommonMemModel(resourceUsage.residentMemory), round(sum(cpu) / len(cpu), 2),
                        self.extractor.getComponentName()))

        elif self.extractor.getStatType() == StatTypeEnum.MACHINE_IO_STAT:
            value = self.processIOstat(value, line)
        self._addtoMap(value)  # create time series

    def processIOstat(self, value, line):
        if re.match(".*Collecting stats...", line, re.I | re.M):  # time stamp can be found with this regex line
            self.key = line.split("|")[0]
        else:
            if "Disk I/O statistics" in line:
                self.isFoundLine = True
            if self.isFoundLine == True:
                line = re.sub(r'[(\[\]{)}]', ' ', re.sub(" +", " ", line))  # remove the unwanted characters
                arr = filter(None, line.split(" "))
                if len(arr) == 8:
                    try:
                        val = ("%s,%s,%s,%s,%s,%s,%s,%s,%s") % (
                            arr[0].split("|")[1], arr[1], CommonUtils._extractNumberInString(arr[2]), arr[3],
                            CommonUtils._extractNumberInString(arr[4]), arr[5],
                            CommonUtils._extractNumberInString(arr[6]),
                            CommonUtils._extractNumberInString(arr[7]), self.machineName)
                        if "None" not in val:
                            value = val
                    except Exception as e:
                        value = None
        return value

    def getProcessResourceUsage(self, line):
        line = re.sub(' +', ' ', line)  # remove the duplicated space
        arr = line.split(" ")
        if len(arr) >= 7:
            binaryName = CommonUtils._extractByRegex(self.extractor.getComponentName(), arr[2].strip())
            if binaryName is None:
                return
            return ResourceUsage(arr[0].split("|")[1], arr[1], arr[2], arr[3], arr[4],
                                 CommonUtils._extractByRegex("\\d*.?\\d+\\w+", arr[5]), arr[6])
        return None

    def processSSM_STAT(self, line):
        if self.extractor.getStatType() == StatTypeEnum.PROCESS_STAT:
            arr = line.split("|")
            if (len(arr) > 3):
                self.key = arr[0].strip()
                processName = CommonUtils._extractByRegex(self.extractor.getComponentName(), arr[1].strip())
                if processName is None:
                    return
                statName = CommonUtils._extractByRegex(self.extractor.getStatName(), arr[2].strip())
                if statName is None:
                    return
                if self.extractor.getOption() != "-PSS":
                    description = CommonUtils._extractNumberInString(
                        CommonUtils._extractByRegex(self.extractor.getDescription(), arr[3].strip()))
                else:
                    description = CommonUtils._extractByRegex(self.extractor.getDescription(), arr[3].strip())
                if description is None:
                    return
                self._addtoMap((("%s,%s,%s,%s") % (
                    description, self.extractor.getComponentName(), statName,
                    self.extractor.getDescription())))

    def _addtoMap(self, value):
        if value is not None:
            shiftedTime = str(CommonUtils.getDateTimeObj(CommonUtils._logTimeConverter(self.key, self.timeSeriesFormat),
                                                         self.timeSeriesFormat) + timedelta(hours=float(self.hours),
                                                                                            minutes=float(self.minutes),
                                                                                            seconds=float(
                                                                                                self.seconds)))
            if "." in shiftedTime:
                timeFormat = '%Y-%m-%d %H:%M:%S.%f'
            else:
                timeFormat = '%Y-%m-%d %H:%M:%S'

            formattedTime = str(CommonUtils.timeFormatter(shiftedTime, timeFormat, self.timeSeriesFormat))
            if self.extractor.isMultipleStat() == False:
                self.stat.update({CommonUtils.to_epoch(formattedTime): value})
            elif self.extractor.isMultipleStat() == True:
                self.stat.setdefault(value.split(",")[0], {}). \
                    update({CommonUtils.to_epoch(formattedTime): value})

    def _createCSVFileName(self):
        if self.extractor.getDescription() is None:
            return ("%s_%s_%s") % (
                self.extractor.getFileType(), self.extractor.getStatName(),
                datetime.datetime.now().strftime("%Y%m%d%H%M%S"))
        else:
            return ("%s_%s_%s_%s" % (
                self.extractor.getFileType(), self.extractor.getComponentName().replace(":", ""),
                self.extractor.getDescription().replace("\\", ""),
                datetime.datetime.now().strftime("%Y%m%d%H%M%S"))).replace(" ", "").replace("\\", "")

    def writeOuput(self):
        self.stat.keys().sort()  # sort from time
        self.logger.log_info(
            "Extracted stats from the %s file and stat count is %s" % (
                str(self.extractor.getFileType()), str(len(self.stat))))
        outputHandler = OutputHandler(self.stat)
        if self.outputType == OutputTypeEnum.CSV:
            outputHandler.writeOutput(self._createCSVFileName())
        elif self.outputType == OutputTypeEnum.DB:
            outputHandler.commitDb(self.extractor.getTableName(), self.extractor.getColumns(), self.stat)
