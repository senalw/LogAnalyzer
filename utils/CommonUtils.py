#!/usr/bin/python
"""
Created by senalw on 9/19/2018.
"""
import re
from utils.PropertyReader import PropertyReader
from datetime import datetime


def _extractByRegex(regex, string):
    result = None
    if re.search(regex, string):
        match = re.search(regex, string)
        result = match.group(0)
    return result


def _extractNumberInString(str):
    numberVal = None
    if str is not None:
        [float(numberVal) for numberVal in re.findall(r'-?\d+\.?\d*', str)]
    return numberVal


def _extractOnlyCharsInString(str):
    return "".join(re.findall("[a-zA-Z]+", str))


def _getCommonMemModel(stat):
    result = 0
    memConfig = PropertyReader().getProperty("COMMON_MEMORY_REPRESENTATION")
    if memConfig.upper() == "K" and _extractOnlyCharsInString(stat).upper() == "K":
        result = float(_extractNumberInString(stat))
    elif memConfig.upper() == "K" and _extractOnlyCharsInString(stat).upper() == "M":
        result = float(_extractNumberInString(stat)) * 1024
    elif memConfig.upper() == "K" and _extractOnlyCharsInString(stat).upper() == "G":
        result = float(_extractNumberInString(stat)) * 1024 * 1024

    elif memConfig.upper() == "M" and _extractOnlyCharsInString(stat).upper() == "M":
        result = float(_extractNumberInString(stat))
    elif memConfig.upper() == "M" and _extractOnlyCharsInString(stat).upper() == "K":
        result = float(_extractNumberInString(stat)) / 1024
    elif memConfig.upper() == "M" and _extractOnlyCharsInString(stat).upper() == "G":
        result = float(_extractNumberInString(stat)) * 1024

    elif memConfig.upper() == "G" and _extractOnlyCharsInString(stat).upper() == "G":
        result = float(_extractNumberInString(stat))
    elif memConfig.upper() == "G" and _extractOnlyCharsInString(stat).upper() == "K":
        result = float(_extractNumberInString(stat)) / (1024 * 1024)
    elif memConfig.upper() == "G" and _extractOnlyCharsInString(stat).upper() == "M":
        result = float(_extractNumberInString(stat)) / 1024

    return round(result, 2)


def _logTimeConverter(time, format):
    if "." in time:
        date_obj = getDateTimeObj(time, '%Y%m%d%H%M%S.%f')  # GSD log format
    else:
        date_obj = getDateTimeObj(time, '%b %d %Y %H:%M:%S')  # SSM lof time format
    return datetime.strftime(date_obj, format)[:-3]


def getDateTimeObj(time, format):
    return datetime.strptime(time, format)


def timeFormatter(time, currentFormat, expectedFormat):
    datetimeObject = datetime.strptime(time, currentFormat)
    return datetime.strftime(datetimeObject, expectedFormat)


def to_epoch(dt_format, timeFormat=None):
    if timeFormat is None:
        timeFormat = PropertyReader().getProperty("TIME_SERIES_FORMAT")
    if "." in timeFormat and "." in dt_format:
        dateTimeFormat = dt_format.split(".")
        accuracyLevel = dateTimeFormat[-1]
        dt_format = dateTimeFormat[0]
        timeFormat = timeFormat.split(".")[0]
        if len(accuracyLevel) > 0:
            multiplication_power = 9 - len(accuracyLevel)  # purpose of converting to nano second level
            epoch = (((int((datetime.strptime(dt_format, timeFormat) - datetime(1970, 1, 1)).total_seconds())) * (
                    1 * pow(10, len(accuracyLevel)))) + int(accuracyLevel)) * pow(10, multiplication_power)
        else:
            epoch = int((datetime.strptime(dt_format, timeFormat) - datetime(1970, 1, 1)).total_seconds()) * 1000000000
        return epoch
    else:
        timeFormat = '%Y-%m-%d %H:%M:%S'  # common time format
        epoch = int((datetime.strptime(dt_format, timeFormat) - datetime(1970, 1, 1)).total_seconds()) * 1000000000
        return epoch
