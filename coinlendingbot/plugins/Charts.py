# coding=utf-8
from coinlendingbot.plugins.Plugin import Plugin
import os
import json
import sqlite3

DB_PATH = "market_data/loan_history.sqlite3"

class Charts(Plugin):

    def on_bot_init(self):
        super(Charts, self).on_bot_init()

        # If there's no history database, can't use this
        if not os.path.isfile(DB_PATH):
          self.log.log_error("DB Doesn't Exist. 'AccountStats' plugin must be enabled.")
          return

        self.log.addSectionLog("plugins", "charts", { 'navbar': True })

        self.db = sqlite3.connect('market_data/loan_history.sqlite3')
        self.last_dump = 0
        self.dump_interval = int(self.config.get("CHARTS", "DumpInterval", 21600))
        self.history_file = self.config.get("CHARTS", "HistoryFile", "www/history.json")


    def before_lending(self):
        return


    def after_lending(self):
        if self.get_db_version() > 0 and self.last_dump + self.dump_interval < sqlite3.time.time():
            self.dump_history()
            self.last_dump = sqlite3.time.time()


    def get_db_version(self):
        return self.db.execute("PRAGMA user_version").fetchone()[0]


    def dump_history(self):

        cursor = self.db.cursor()

        data = { }

        # Get distinct coins
        cursor.execute("SELECT DISTINCT currency FROM history ORDER BY currency DESC")
        for i in cursor:
            data[i[0]] = []

        # Loop over the coins and get data for each
        for coin in data:
            runningTotal = 0.0

            cursor.execute("SELECT strftime('%%s', strftime('%%Y-%%m-%%d 00:00:00', close)) ts, round(SUM(earned), 8) i " \
                           "FROM history WHERE currency = '%s' GROUP BY ts ORDER BY ts" % (coin));
            for row in cursor:
                runningTotal += float(row[1])
                data[coin].append([ int(row[0]), float(row[1]), float(runningTotal) ])

        # Dump data to file
        with open(self.history_file, "w") as hist:
            hist.write(json.dumps(data))

        self.log.log("Charts Plugin: History dumped. You can open charts.html.")
        cursor.close()
