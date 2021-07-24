#!/usr/bin/python
"""
Created by senalw on 9/17/2018.
"""
import csv
import sqlite3
from utils import CommonUtils
from settings import ROOT_DIR
from utils.Logger import Logger
from utils.PropertyReader import PropertyReader

import os


class OutputHandler:

    def __init__(self, stat):
        self.stats = stat
        self.logger = Logger()
        self.propertyReader = PropertyReader()
        self.db_timeout = float(self.propertyReader.getProperty("DB_CONNECTION_TIMEOUT"))
        self.db_name = self.propertyReader.getProperty("DB_NAME")

    def writeOutput(self, fileName):
        try:
            with open(os.path.join(ROOT_DIR, "output/", fileName + ".csv"), 'wb') as csvfile:
                writer = csv.writer(csvfile, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
                for (key, value) in sorted(self.stats.iteritems()):
                    writer.writerow([key, value])
                csvfile.close()
        except Exception as e:
            self.logger.log_errors("Unable to write %s.csv in output directory due to %s" % (fileName, e.message))

    def commitDb(self, tableName, columns, stats):
        connection = None
        cursor = None
        columns = str(columns).split(",")

        try:
            connection = sqlite3.connect(os.path.join(ROOT_DIR, "output/", self.db_name),
                                         timeout=self.db_timeout)  # timeout = 60s
            cursor = connection.cursor()
            tableCreateSql = 'CREATE TABLE IF NOT EXISTS "%s" %s;' % (tableName, self._createTableSQL(columns))
            cursor.execute(tableCreateSql)
            query = self._createInsertQuery(tableName, columns)
            statLst = []
            statLst = self._extractFromDict(stats, statLst)
            cursor.executemany(query, statLst)
        except Exception as e:
            self.logger.log_errors("Unable to commit to DB due to %s" % e.message)
        finally:
            cursor.close()
            connection.commit()
            connection.close()
            self.logger.log_info("QUERY = SELECT %s FROM %s" % (", ".join(columns), tableName))

    def _extractFromDict(self, stats, statList):
        statsarr = []
        if isinstance(stats, dict):
            for key, value in sorted(stats.iteritems()):
                temp = [key]
                if isinstance(value, basestring):
                    temp.extend(value.split(","))
                    statsarr.append(temp)
                else:
                    self._extractFromDict(value, statList)
            statList.extend(statsarr)
            return statList
        elif isinstance(stats, list):
            return stats

    def _createTableSQL(self, columns):
        str = []
        str.append("(")
        for index, column in enumerate(columns):
            if index == 0:
                str.append('"%s" REAL' % column)
            else:
                str.append('"%s" TEXT' % column)
            if index < len(columns) - 1:
                str.append(", ")
        str.append(", PRIMARY KEY(%s)" % ','.join(columns))
        str.append(")")
        return ''.join(str)

    def _retrieveData(self, sql):
        connection = None
        cursor = None
        try:
            connection = sqlite3.Connection(os.path.join(ROOT_DIR, "output/", self.db_name))
            cursor = connection.cursor()
            cursor.execute(sql)
            lst = cursor.fetchall()
            return lst
        except Exception as e:
            self.logger.log_debug("SQL [%s]" % sql)
            self.logger.log_errors("Unable to read from DB due to %s" % e.message)
        finally:
            cursor.close()
            connection.commit()
            connection.close()

    def readFromDB(self, sql):
        datDict = {}
        lst = self._retrieveData(sql)
        if lst is None or len(lst) == 0:
            raise Exception("No data found!")
        for index, row in enumerate(lst):
            datDict.update({"row_%s" % (str(index)): list(map(float, row))})
        datDict.keys().sort()
        return datDict

    def insertFromCSV(self, filePath, extractor):
        connection = None
        cursor = None
        columns = str(extractor.getColumns()).split(",")
        try:
            openfile = open(filePath, "r")
            connection = sqlite3.Connection(os.path.join(ROOT_DIR, "output/", self.db_name))
            cursor = connection.cursor()
            insert_sql = self._createInsertQuery(extractor.getTableName(), columns)
            for line in openfile:
                cursor.executemany(insert_sql, [line.split(",")])
            self.logger.log_info("Imported record to db from csv")
        except Exception as e:
            self.logger.log_errors("Unable to insert from csv due to %s" % e.message)
        finally:
            cursor.close()
            connection.commit()
            connection.close()

    def _createInsertQuery(self, tableName, columns):
        placeholders = ', '.join('?' * len(columns))
        return 'INSERT INTO %s VALUES (%s)' % (tableName, placeholders)

    def _loadFileToList(self, filePath, columns, timeFormat=None):
        stats = {}
        openfile = open(filePath, "r")
        column_size = len(columns.split(","))
        for line in openfile:
            row = line.replace("\n", "").split(",")
            if timeFormat is not None:
                row[0] = CommonUtils.to_epoch(row[0], timeFormat)
            if len(row) != column_size:
                self.logger.log_errors(
                    "Unable to export data to db since columns[%s] count doesn't match with csv columns[%s] data" % (
                        column_size, len(row)))
            stats.update({row[0]: ','.join(row[1:len(row)])})
        self.logger.log_info("Stat count is %s" % len(stats))
        return stats
