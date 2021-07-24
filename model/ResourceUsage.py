#!/usr/bin/python
"""
Created by senalw on 9/18/2018.
"""
from utils.PropertyReader import PropertyReader


class ResourceUsage:

    def __init__(self, PID, user, binaryName, fd, totalMem, resMem, CPU):
        self.propertyReader = PropertyReader()
        self.PID = PID
        self.user = user
        self.binaryName = binaryName
        self.fileDescriptor = fd
        self.totalMemory = totalMem
        self.residentMemory = resMem
        self.CPU = self._calculate_average_cpu(CPU)

    def _calculate_average_cpu(self, cpu):
        return [float(x) for x in (map(lambda x: x.replace("%", ""),
                                       filter(lambda y: "more..." not in y, cpu.split(","))))]
