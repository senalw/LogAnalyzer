#!/usr/bin/python
"""
Created by senalw on 9/22/2018.
"""
import sqlparse
from sqlparse.sql import IdentifierList, Identifier, Where, Comparison, Parenthesis, Token
from sqlparse.tokens import Keyword


class SQLParser(object):

    def __init__(self, sql):
        self.tables = self.parse_sql_tables(sql)
        self.columns = self.parse_sql_columns(sql)
        self.where = self.process_Where_Clause(sql)

    def getTables(self):
        return self.tables

    def getColumns(self):
        return self.columns

    def getWhereClause(self):
        return self.where

    def isSql(self):
        if len(self.tables) > 0 and self.columns > 0:
            return True
        return False

    @staticmethod
    def parse_sql_columns(sql):
        columns = []
        parsed = sqlparse.parse(sql)
        stmt = parsed[0]
        for token in stmt.tokens:
            if isinstance(token, IdentifierList):
                for identifier in token.get_identifiers():
                    columns.append(identifier)
                    # columns.append(identifier.get_real_name())
            if isinstance(token, Identifier):
                columns.append(token.get_real_name())
            if token.ttype is Keyword:  # from
                break
        return columns

    @staticmethod
    def get_table_name_from_token(token):
        parent_name = token.get_parent_name()
        real_name = token.get_real_name()
        if parent_name:
            return parent_name + "." + real_name
        else:
            return real_name

    @staticmethod
    def process_Where_Clause(sql):
        where = []
        parsed = sqlparse.parse(sql)
        stmt = parsed[0]
        for token in stmt.tokens:
            if isinstance(token, Where):
                for insiders in token.tokens:
                    if isinstance(insiders, Comparison) or \
                            isinstance(insiders, Identifier) or isinstance(insiders, Parenthesis) or \
                            isinstance(insiders, Token):
                        where.append(insiders.value)
        return where

    @staticmethod
    def parse_sql_tables(sql):
        tables = []
        parsed = sqlparse.parse(sql)
        stmt = parsed[0]
        from_seen = False
        for token in stmt.tokens:
            if from_seen:
                if token.ttype is Keyword:
                    continue
                else:
                    if isinstance(token, IdentifierList):
                        for identifier in token.get_identifiers():
                            tables.append(SQLParser.get_table_name_from_token(identifier))
                    elif isinstance(token, Identifier):
                        tables.append(SQLParser.get_table_name_from_token(token))
                    else:
                        pass
            if token.ttype is Keyword and token.value.upper() == "FROM":
                from_seen = True
        return tables


# sqlparser = SQLParser("SELECT Time, WriteRate  FROM MachineIO where Disk in ('sda','sdb')")
# tables = sqlparser.getTables()
# where = sqlparser.getWhereClause()
# columns = list(map(str, sqlparser.getColumns()))
# print()
