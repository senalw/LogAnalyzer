#!/usr/bin/python
"""
Created by senalw on 9/12/2018.
"""
import abc

ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})


class Director:
    _builder = None

    def setBuilder(self, builder):
        self._builder = builder

    def getExtractor(self):
        extractor = Extractor()
        extractor.setComponentName(self._builder.getComponentName())
        extractor.setStatName(self._builder.getStatName())
        extractor.setDescription(self._builder.getDescription())
        extractor.setStatType(self._builder.getStatType())
        extractor.setFileType(self._builder.getFileType())
        extractor.setMachineName(self._builder.getMachineName())
        extractor.setColumns(self._builder.getColumns())
        extractor.setTableName(self._builder.getTableName())
        extractor.setMultipleStat(self._builder.isMultipleStat())
        extractor.setOption(self._builder.getOption())
        return extractor


class Extractor:

    def __init__(self):
        self._component_name = None
        self._statType = None
        self._statName = None
        self._description = None
        self._fileType = None
        self._machineName = None
        self._columns = None
        self._tableName = None
        self._isMultipleStat = False
        self._option = None

    def setComponentName(self, componentName):
        self._component_name = componentName

    def setStatType(self, statType):
        self._statType = statType

    def setStatName(self, statName):
        self._statName = statName

    def setDescription(self, description):
        self._description = description

    def setFileType(self, fileType):
        self._fileType = fileType

    def setMachineName(self, machineName):
        self._machineName = machineName

    def setColumns(self, columns):
        self._columns = columns

    def setTableName(self, tableName):
        self._tableName = tableName

    def setMultipleStat(self, isMultipleStat):
        self._isMultipleStat = isMultipleStat

    def setOption(self, option):
        self._option = option

    def getComponentName(self):
        return self._component_name

    def getStatType(self):
        return self._statType

    def getStatName(self):
        return self._statName

    def getDescription(self):
        return self._description

    def getFileType(self):
        return self._fileType

    def getMachineName(self):
        return self._machineName

    def getColumns(self):
        return self._columns

    def getTableName(self):
        return self._tableName

    def isMultipleStat(self):
        return self._isMultipleStat

    def getOption(self):
        return self._option


class Builder(ABC):

    @abc.abstractmethod
    def getComponentName(self):
        pass

    @abc.abstractmethod
    def getStatType(self):
        pass

    @abc.abstractmethod
    def getStatName(self):
        pass

    @abc.abstractmethod
    def getDescription(self):
        pass

    @abc.abstractmethod
    def getFileType(self):
        pass

    @abc.abstractmethod
    def getMachineName(self):
        pass

    @abc.abstractmethod
    def getColumns(self):
        pass

    @abc.abstractmethod
    def getTableName(self):
        pass

    @abc.abstractmethod
    def isMultipleStat(self):
        pass

    @abc.abstractmethod
    def getOption(self):
        pass
