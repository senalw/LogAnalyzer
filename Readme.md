<h2>LogAnalyzer</h2>
<p>LogAnalyzer is a tool of collecting data points for a given statistic type from a unix OS and export them to csv for sqlite.</p>

e.g.
```
StatAnalyzer.py -MM <1-csv, 2-sqlite db> : Extract machine's used memory
StatAnalyzer.py -MC <1-csv, 2-sqlite db> : Extract machine's CPU usage in percentage
StatAnalyzer.py -PS <Full Qualified Process Name> <StatName Regex> <Description Regex> <1-csv, 2-sqlite db> : Extract stats from process instances
StatAnalyzer.py -PSS <Full Qualified Process Name> <StatName Regex> <Description Regex> <1-csv, 2-sqlite db> : Extract stats from process instances with String values
StatAnalyzer.py -PM <Binary Name> <1-Total Memory, 2-Resident Memory> <1-csv, 2-sqlite db> : Extract memory stats from process instances
StatAnalyzer.py -PC <Binary Name> <1-csv, 2-sqlite db> : Extract average CPU usage stats from process instances
StatAnalyzer.py -PR <Binary Name> <1-csv, 2-sqlite db> : Extract resource usage of a process instances
StatAnalyzer.py -IO <1-csv, 2-sqlite db> : Extract IO stats of disks
StatAnalyzer.py -UD <CSV file with Path> : Import to SQLite db from CSV
StatAnalyzer.py -UCD <CSV file with Path> <SQLite TableNAME> <Comma Seperated Col Names - First Column Should be Time> <TimeFormat in csv if not epoch> : Import to SQLite db from custom CSV format
StatAnalyzer.py -RD <SQL> : Retrieve data from SQLite database and print on console
StatAnalyzer.py -RF <command file path> : Run commands from file
```
<p>After exporting data points, you can plot them in Graphs from any desired graphing application. (e.g. Grafana)</p>

<h2>Python</h2>
3.0 or upper

<h2>Support Libraries</h2>

```
pip install Pandas
pip install sqlparse
pip install flask
pip install flask_cors
pip install enum
```

<h2>Contributing</h2>
Pull requests are welcome.


<h2>Author</h2>
Senal Weerasinghe (senaldulanjala@gmail.com)
