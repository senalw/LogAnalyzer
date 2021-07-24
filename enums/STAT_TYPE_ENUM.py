#!/usr/bin/python
"""
Created by senalw on 9/14/2018.
"""

from enum import Enum


class StatTypeEnum(Enum):
    PROCESS_STAT = 0
    PROCESS_MEM_STAT = 1
    PROCESS_CPU_STAT = 2
    MACHINE_MEM_STAT = 3
    MACHINE_CPU_STAT = 4
    PROCESS_RESOURCE_USAGE_STAT = 5
    MACHINE_IO_STAT = 6
