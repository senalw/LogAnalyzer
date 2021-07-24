#!/usr/bin/python
"""
Created by senalw on 8/28/2018.
"""
import pandas as panda
import socket
import time
from datetime import timedelta
from flask import Flask, request, jsonify, abort
from flask_cors import CORS, cross_origin
from utils.OutputHandler import OutputHandler
from utils.SQLQueryProcessor import SQLParser
from utils import CommonUtils
from settings import ROOT_DIR
from utils.Logger import Logger
from utils.PropertyReader import PropertyReader
from utils.SqliteCache import SqliteCache

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
methods = ('GET', 'POST')
metric_finders = {}
metric_readers = {}
annotation_readers = {}
panel_readers = {}
queryServer = OutputHandler(None)
logger = Logger()
propertReader = PropertyReader()
cacheTimeOut = int(propertReader.getProperty("CACHE_TIMEOUT"))
sqliteCache = SqliteCache(ROOT_DIR + "/cache", default_timeout=cacheTimeOut)
global columName


def add_reader(name, reader):
    metric_readers[name] = reader


def add_finder(name, finder):
    metric_finders[name] = finder


def add_annotation_reader(name, reader):
    annotation_readers[name] = reader


def add_panel_reader(name, reader):
    panel_readers[name] = reader


@app.route('/', methods=methods)
@cross_origin()
def hello_world():
    print request.headers, request.get_json()
    return 'Jether\'s python Grafana datasource, used for rendering HTML panels and timeseries data.'


@app.route('/search', methods=methods)
@cross_origin()
def find_metrics():
    # print request.headers, request.get_json()
    req = request.get_json()

    target = req.get('target', '*')

    if ':' in target:
        finder, target = target.split(':', 1)
    else:
        finder = target

    if not target or finder not in metric_finders:
        metrics = []
        if target == '*':
            metrics += metric_finders.keys() + metric_readers.keys()
        else:
            metrics.append(target)

        return jsonify(metrics)
    else:
        return jsonify(list(metric_finders[finder](target)))


def dataframe_to_json_table(target, df):
    response = []

    if df.empty:
        return response

    if isinstance(df, panda.DataFrame):
        response.append({'type': 'table',
                         'columns': df.columns.map(lambda col: {"text": col}).tolist(),
                         'rows': df.where(panda.notnull(df), None).values.tolist()})
    else:
        abort(404, Exception('Received object is not a dataframe.'))

    return response


def annotations_to_response(target, df):
    response = []

    # Single series with DatetimeIndex and values as text
    if isinstance(df, panda.Series):
        for timestamp, value in df.iteritems():
            response.append({
                "annotation": target,  # The original annotation sent from Grafana.
                "time": timestamp.value // 10 ** 6,  # Time since UNIX Epoch in milliseconds. (required)
                "title": value,  # The title for the annotation tooltip. (required)
                # "tags": tags, # Tags for the annotation. (optional)
                # "text": text # Text for the annotation. (optional)
            })
    # Dataframe with annotation text/tags for each entry
    elif isinstance(df, panda.DataFrame):
        for timestamp, row in df.iterrows():
            annotation = {
                "annotation": target,  # The original annotation sent from Grafana.
                "time": timestamp.value // 10 ** 6,  # Time since UNIX Epoch in milliseconds. (required)
                "title": row.get('title', ''),  # The title for the annotation tooltip. (required)
            }

            if 'text' in row:
                annotation['text'] = str(row.get('text'))
            if 'tags' in row:
                annotation['tags'] = str(row.get('tags'))

            response.append(annotation)
    else:
        abort(404, Exception('Received object is not a dataframe or series.'))

    return response


def _series_to_annotations(df, target):
    if df.empty:
        return {'target': '%s' % (target),
                'datapoints': []}

    sorted_df = df.dropna().sort_index()
    timestamps = (sorted_df.index.astype(panda.np.int64) // 10 ** 6).values.tolist()
    values = sorted_df.values.tolist()

    return {'target': '%s' % (df.name),
            'datapoints': zip(values, timestamps)}


@app.route('/annotations', methods=methods)
@cross_origin(max_age=600)
def query_annotations():
    # print request.headers, request.get_json()
    req = request.get_json()

    results = []

    ts_range = {'$gt': panda.Timestamp(req['range']['from']).to_pydatetime(),
                '$lte': panda.Timestamp(req['range']['to']).to_pydatetime()}

    query = req['annotation']['query']

    if ':' not in query:
        abort(404, Exception('Target must be of type: <finder>:<metric_query>, got instead: ' + query))

    finder, target = query.split(':', 1)
    results.extend(annotations_to_response(query, annotation_readers[finder](target, ts_range)))

    return jsonify(results)


@app.route('/panels', methods=methods)
@cross_origin()
def get_panel():
    # print request.headers, request.get_json()
    req = request.args

    ts_range = {'$gt': panda.Timestamp(int(req['from']), unit='ms').to_pydatetime(),
                '$lte': panda.Timestamp(int(req['to']), unit='ms').to_pydatetime()}

    query = req['query']

    if ':' not in query:
        abort(404, Exception('Target must be of type: <finder>:<metric_query>, got instead: ' + query))

    finder, target = query.split(':', 1)
    return panel_readers[finder](target, ts_range)


@app.route('/query', methods=methods)
@cross_origin(max_age=600)
def query_metrics():
    # print request.headers, request.get_json()
    results = []
    try:
        req = request.get_json()

        ts_range = {'$gt': panda.Timestamp(req['range']['from']).to_pydatetime(),
                    '$lte': panda.Timestamp(req['range']['to']).to_pydatetime()}

        if 'intervalMs' in req:
            freq = str(req.get('intervalMs')) + 'ms'
        else:
            freq = None

        for target in req['targets']:

            req_type = target.get('type', 'timeserie')
            target = finder = target['target']
            if target is None:
                abort(404, Exception('Target must be of type: <Query>, got instead: ' + target['target']))
                logger.log_errors("Invalid sql query %s" % target)

            sqlparser = SQLParser(target)
            data = readFromSqlite(target, ts_range, sqlparser)
            if data is not None:
                add_reader(finder, createDataFrame(data, sqlparser))
                query_results = metric_readers.get(finder)

                if req_type == 'table':
                    results.extend(dataframe_to_json_table(target, query_results))
                else:
                    results.extend(dataframe_to_response(target, query_results, freq=freq))
    except Exception as e:
        # abort(404, Exception(e.message))
        print(e.message)

    return jsonify(results)


def readFromSqlite(sql, ts_range, sqlparser):
    if sqlparser.isSql() is False:
        return
    queryTimeDeltaOffset = str(propertReader.getProperty("QUERY_TIME_DELTA_OFFSET")).split(":")
    hours = queryTimeDeltaOffset[0]
    minutes = queryTimeDeltaOffset[1]
    seconds = queryTimeDeltaOffset[2]
    fromTime = CommonUtils.to_epoch(
        str(ts_range.get("$gt") + timedelta(hours=float(hours), minutes=float(minutes), seconds=float(seconds))).
            split("+")[0], "%Y-%m-%d %H:%M:%S.%f")
    toTime = CommonUtils.to_epoch(
        str(ts_range.get("$lte") + timedelta(hours=float(hours), minutes=float(minutes), seconds=float(seconds))).
            split("+")[0], "%Y-%m-%d %H:%M:%S.%f")

    timeCol = str(sqlparser.getColumns()[0]).upper().split("AS")[0]
    if len(sqlparser.getWhereClause()) > 0:
        sql = sql + (" AND (%s >= '%s' and %s <='%s')" % (timeCol, fromTime, timeCol, toTime))
    else:
        sql = sql + (" WHERE (%s >= '%s' and %s <='%s')" % (timeCol, fromTime, timeCol, toTime))

    startTime = time.time()
    data = _getData(sql)  # get date from db or cache
    endTime = time.time()
    if data is not None:
        logger.log_info(
            "SQL [%s] | Extracted Data Points = %s | Elapsed time %s" % (
                sql, len(data), str(endTime - startTime) + "s"))
    else:
        logger.log_errors("No data Extracted !")
    return data


def _getData(sql):
    isCacheEnabled = str(propertReader.getProperty("CACHE_ENABLED")).upper()
    data = None
    if isCacheEnabled == 'TRUE':
        data = sqliteCache.get(sql)  # get data from sqlite cache
        if data is not None:
            sqliteCache.update(sql, data, cacheTimeOut)  # update the timeout
    if data is None:
        logger.log_info("No cached data! Get data from DB")
        data = queryServer.readFromDB(sql)  # query db
        sqliteCache.add(sql, data, timeout=cacheTimeOut)
    return data


def dataframe_to_response(target, df, freq=None):
    response = []

    if df.empty:
        return response

    if freq is not None:
        if str(propertReader.getProperty("GRAPH_SUMMARIZATION_ENABLED")).upper() == 'TRUE':
            df.index = panda.to_datetime(df.index, unit="ns")
            df = df.tz_localize("UTC").tz_convert('UTC').resample(rule=freq, label='right', closed='right') \
                .mean().tz_convert(df.index)
            logger.log_info("Summarized dataframe size %s" % len(df))
        else:
            logger.log_info("Non-summarized dataframe size %s" % len(df))

    if isinstance(df, panda.Series):
        response.append(_series_to_response(df, target))
    elif isinstance(df, panda.DataFrame):
        for col in df:
            response.append(_series_to_response(df[col], target))
    else:
        abort(404, Exception('Received object is not a dataframe or series.'))

    return response


def _series_to_response(df, target):
    if df.empty:
        return {'target': '%s' % (target),
                'datapoints': []}

    sorted_df = df.dropna().sort_index()

    try:
        timestamps = (sorted_df.index.astype(panda.np.int64) // 10 ** 6).values.tolist()  # New pandas version
    except:
        timestamps = (sorted_df.index.astype(panda.np.int64) // 10 ** 6).tolist()

    values = sorted_df.values.tolist()

    return {'target': '%s' % (df.name),
            'datapoints': zip(values, timestamps)}


def createDataFrame(data, sqlparser):
    columns = []
    for col in sqlparser.getColumns():
        column = str(col).upper()
        if " as ".upper() in column.upper():
            columns.append(column.split(" AS ")[1])
        else:
            columns.append(column)
    return panda.DataFrame.from_dict(data, orient='index', columns=columns).set_index(columns[0])


if __name__ == '__main__':
    try:
        propertReader = PropertyReader()
        port = int(propertReader.getProperty("QUERY_SERVICE_PORT"))
        host = socket.gethostbyname(socket.gethostname())
        app.run(host=host, port=port, debug=False, threaded=True)
    except Exception as e:
        print(e)
