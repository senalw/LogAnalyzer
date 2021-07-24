#!/usr/bin/python
"""
Created by senalw on 9/12/2018.
"""
import os
import time
import sys
import platform
import subprocess
from subprocess import PIPE, Popen, check_call

from settings import ROOT_DIR
from utils.LogReader import LogReader
from utils.PropertyReader import PropertyReader
from enums.OUTPUT_TYPE_ENUM import OutputTypeEnum
from stat_builders.Extractor import Director
from stat_builders.MachineCPUStatBuilder import MachineCPUStatBuilder
from stat_builders.MachineMemStatBuilder import MachineMemStatBuilder
from stat_builders.ProcessStatBuilder import ProcessStatBuilder
from stat_builders.ProcessMemStatBuilder import ProcessMemStatBuilder
from stat_builders.ProcessCPUStatBuilder import ProcessCPUStatBuilder
from stat_builders.ProcessResourceStatBuilder import ProcessResoureStatBuilder
from stat_builders.MachineIOStatBuilder import MachineIOStatBuilder
from utils.OutputHandler import OutputHandler
from utils.Logger import Logger


class StatAnalyzer():

    def __init__(self):
        self.propertyReader = PropertyReader()
        self.director = Director()
        self.logger = Logger()

    def extractStats(self, builder, outputType):
        output = OutputTypeEnum.CSV if outputType == "1" else OutputTypeEnum.DB
        self.director.setBuilder(builder)
        self.extractor = self.director.getExtractor()
        self.read_Log(self.extractor, output)

    def read_Log(self, extractor, outputType):
        reader = LogReader(extractor, outputType)


if __name__ == '__main__':
    logger = Logger()
    try:

        machineName = platform.node()
        statAnalyzer = StatAnalyzer()
        director = Director()
        outputHandler = OutputHandler(None)
        commandType = sys.argv[1]

        logger.log_info(
            "==================================== START ANALYZING ==========================================")
        if (commandType == "-MM"):
            outputType = sys.argv[2]
            statAnalyzer.extractStats(MachineMemStatBuilder(machineName, "MachineMEM", commandType), outputType)
        elif (commandType == '-MC'):
            outputType = sys.argv[2]
            statAnalyzer.extractStats(MachineCPUStatBuilder(machineName, "MachineCPU", commandType), outputType)
        elif (commandType == '-PS'):
            process = sys.argv[2]
            statName = sys.argv[3]
            description = sys.argv[4]
            outputType = sys.argv[5]
            statAnalyzer.extractStats(ProcessStatBuilder(process, statName, description, commandType), outputType)
        elif (commandType == '-PSS'):
            process = sys.argv[2]
            statName = sys.argv[3]
            description = sys.argv[4]
            outputType = sys.argv[5]
            statAnalyzer.extractStats(ProcessStatBuilder(process, statName, description, commandType), outputType)
        elif commandType == '-PM':
            binaryName = sys.argv[2]
            memoryType = sys.argv[3]
            outputType = sys.argv[4]
            statAnalyzer.extractStats(ProcessMemStatBuilder(binaryName, memoryType, commandType), outputType)
        elif commandType == '-PC':
            binaryName = sys.argv[2]
            outputType = sys.argv[3]
            statAnalyzer.extractStats(ProcessCPUStatBuilder(binaryName, "ProcessCPU", commandType), outputType)
        elif commandType == '-PR':
            binaryName = sys.argv[2]
            outputType = sys.argv[3]
            statAnalyzer.extractStats(ProcessResoureStatBuilder(binaryName, "ProcessResources", commandType),
                                      outputType)
        elif commandType == '-IO':
            outputType = sys.argv[2]
            statAnalyzer.extractStats(MachineIOStatBuilder(machineName, "MachineIO", commandType), outputType)
        elif commandType == "-UD":
            filePath = sys.argv[2]
            builder = ProcessStatBuilder(None, None, None, None)
            director.setBuilder(builder)
            extractor = director.getExtractor()
            outputHandler.insertFromCSV(filePath, extractor)
        elif commandType == '-UCD':
            filePath = sys.argv[2]
            tableName = sys.argv[3]
            columns = sys.argv[4]
            timeFormat = None
            try:
                timeFormat = sys.argv[5]
            except Exception as e:
                print("")
            stats = outputHandler._loadFileToList(filePath, columns, timeFormat)
            outputHandler.commitDb(tableName, columns, stats)
        elif commandType == '-RD':
            sql = sys.argv[2]
            resultset = outputHandler._retrieveData(sql)
            for item in resultset:
                print(' | '.join(str(e) for e in item))
        elif commandType == '-RF':
            filepath = sys.argv[2]
            openfile = open(os.path.join(filepath), "r").read().splitlines()
            procs = []
            command = None
            for line in openfile:
                if line != "" and ('#' != line[0].strip()):  # check for comments and empty lines
                    args = filter(None, line.split(" "))
                    proc = subprocess.Popen([sys.executable or 'python', os.path.join(ROOT_DIR, 'StatAnalyzer.py')] + args,
                                            stdout=PIPE)
                    logger.log_info("%s command started to run on process with pid[%d] " % (line, proc.pid))
                    time.sleep(1)  # sleep to reduce db file lock impact
                    procs.append(proc)
            for proc in procs:
                proc.wait()
                output, err = proc.communicate()
                if "No extracted data points".upper() in str(output).upper() or proc.returncode != 0:
                    logger.log_errors(
                        "command was unssuccessful which runs on PID[%s] due to %s" % (proc.pid, output))
                else:
                    logger.log_info(
                        "Successfully completed task with command  which runs on PID[%s]" % (proc.pid))


    except Exception as e:
        logger.log_errors(str(e))
        print("\n")
        print(
            "StatAnalyzer.py -MM <1-csv, 2-sqlite db> : Extract machine's used memory")
        print(
            "StatAnalyzer.py -MC <1-csv, 2-sqlite db> : Extract machine's CPU usage in percentage")
        print(
            "StatAnalyzer.py -PS <Full Qualified Process Name> <StatName Regex> <Description Regex> <1-csv, 2-sqlite db>"
            " : Extract stats from process instances")
        print(
            "StatAnalyzer.py -PSS <Full Qualified Process Name> <StatName Regex> <Description Regex> <1-csv, 2-sqlite db>"
            " : Extract stats from process instances with String values")
        print(
            "StatAnalyzer.py -PM <Binary Name> <1-Total Memory, 2-Resident Memory> <1-csv, 2-sqlite db>"
            " : Extract memory stats from process instances")
        print(
            "StatAnalyzer.py -PC <Binary Name> <1-csv, 2-sqlite db>"
            " : Extract average CPU usage stats from process instances")
        print(
            "StatAnalyzer.py -PR <Binary Name> <1-csv, 2-sqlite db>"
            " : Extract resource usage of a process instances")
        print(
            "StatAnalyzer.py -IO <1-csv, 2-sqlite db>"
            " : Extract IO stats of disks")
        print(
            "StatAnalyzer.py -UD <CSV file with Path>"
            " : Import to SQLite db from CSV")
        print(
            "StatAnalyzer.py -UCD <CSV file with Path> <SQLite TableNAME> <Comma Seperated Col Names - First Column Should be Time> <TimeFormat in csv if not epoch>"
            " : Import to SQLite db from custom CSV format")
        print(
            "StatAnalyzer.py -RD <SQL>"
            " : Retrieve data from SQLite database and print on console")
        print(
            "StatAnalyzer.py -RF <command file path>"
            " : Run commands from file")
        print("\n")

    finally:
        logger.log_info(
            "==================================== STOP ANALYZING ===========================================")
