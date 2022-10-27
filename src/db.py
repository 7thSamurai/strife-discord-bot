import sqlite3, os, datetime
from config import config

class DB:
    def __init__(self):
        exists = os.path.exists(config.DB_FILE)

        try:
            self.conn = sqlite3.connect(config.DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        except:
            pass # TODO

        # Initial Setup
        if not exists:
            self.conn.execute('''
                CREATE TABLE PUNISHMENTS
                (ID     INT         NOT NULL,
                 TYPE   CHAR(6)     NOT NULL,
                 END    TIMESTAMP   NOT NULL
                );''')

            self.conn.execute('''
                CREATE TABLE LOGS
                (ID     INT         NOT NULL,
                 TYPE   CHAR(6)     NOT NULL,
                 END    TIMESTAMP,
                 MOD    INT         NOT NULL,
                 TIME   TIMESTAMP   NOT NULL,
                 REASON TEXT        NOT NULL
                );''')

            self.conn.commit()

    def get_mute(self, id):
        """ Gets when a user's mute punishment ends, or None if it does not exist
        """
        cursor = self.conn.execute('SELECT end FROM PUNISHMENTS WHERE ID = ? AND TYPE = "mute";', [id])
        end = cursor.fetchone()
        if not end:
            return None

        return end[0]

    def get_ban(self, id):
        """ Gets when a user's ban punishment ends, or None if it does not exist
        """
        cursor = self.conn.execute('SELECT end FROM PUNISHMENTS WHERE ID = ? AND TYPE = "ban";', [id])
        end = cursor.fetchone()
        if not end:
            return None

        return end[0]

    def get_expired(self):
        """ Gets a list of the expired punishments
        """
        cursor = self.conn.execute('SELECT * FROM PUNISHMENTS WHERE END <= datetime("now");')
        expired = []

        for row in cursor:
            expired.append({'id': row[0], 'type': row[1]})

        return expired

    def get_user_log(self, id):
        """ Gets a log of a user's punishments
        """
        cursor = self.conn.execute('SELECT * FROM LOGS WHERE ID = ?;', [id])
        log = []

        for row in cursor:
            log.append({'id': row[0], 'type': row[1], 'end': row[2], 'mod': row[3], 'time': row[4], 'reason': row[5]})

        return log

    def get_mod_log(self, id):
        """ Gets a log of a mod's activities
        """
        cursor = self.conn.execute('SELECT * FROM LOGS WHERE MOD = ?;', [id])
        log = []

        for row in cursor:
            log.append({'id': row[0], 'type': row[1], 'end': row[2], 'mod': row[3], 'time': row[4], 'reason': row[5]})

        return log


    def get_num(self, id):
        """ Gets the total number of punishments that a user has received over the course of time
        """
        cursor = self.conn.execute('SELECT COUNT(*) FROM LOGS WHERE ID = ? AND TYPE != "unmute" AND TYPE != "unban"', [id])
        return cursor.fetchone()[0]

    def add_mute(self, id, end, mod, reason):
        """ Adds a mute-record for a user
        """
        cursor = self.conn.execute('SELECT * FROM PUNISHMENTS WHERE ID = ? AND TYPE = "mute"', [id])
        if cursor.fetchone() != None:
            self.conn.execute('UPDATE PUNISHMENTS SET END = ? WHERE ID = ? AND TYPE = "mute"', [end, id])
        else:
            self.conn.execute('INSERT INTO PUNISHMENTS (ID, TYPE, END) VALUES(?, "mute", ?);', [id, end])

        self.conn.execute('INSERT INTO LOGS (ID, TYPE, END, MOD, TIME, REASON) VALUES(?, "mute", ?, ?, ?, ?);', [id, end, mod, datetime.datetime.utcnow(), reason])
        self.conn.commit()

    def add_ban(self, id, end, mod, reason):
        """ Adds a ban-record for a user
        """
        cursor = self.conn.execute('SELECT * FROM PUNISHMENTS WHERE ID = ? AND TYPE = "ban"', [id])
        if cursor.fetchone() != None:
            self.conn.execute('UPDATE PUNISHMENTS SET END = ? WHERE ID = ? AND TYPE = "ban"', [end, id])
        else:
            self.conn.execute('INSERT INTO PUNISHMENTS (ID, TYPE, END) VALUES(?, "ban", ?);', [id, end])

        self.conn.execute('INSERT INTO LOGS (ID, TYPE, END, MOD, TIME, REASON) VALUES(?, "ban", ?, ?, ?, ?);', [id, end, mod, datetime.datetime.utcnow(), reason])
        self.conn.commit()

    def add_warn(self, id, mod, reason):
        """ Adds a warn-record for a user (Only logs it in this case)
        """
        self.conn.execute('INSERT INTO LOGS (ID, TYPE, MOD, TIME, REASON) VALUES(?, "warn", ?, ?, ?);', [id, mod, datetime.datetime.utcnow(), reason])
        self.conn.commit()

    def add_kick(self, id, mod, reason):
        """ Adds a kick-record for a user (Only logs it in this case)
        """
        self.conn.execute('INSERT INTO LOGS (ID, TYPE, MOD, TIME, REASON) VALUES(?, "kick", ?, ?, ?);', [id, mod, datetime.datetime.utcnow(), reason])
        self.conn.commit()

    def remove_mute(self, id, mod, reason):
        """ Removes a mute-record for a user
        """
        self.conn.execute('DELETE FROM PUNISHMENTS WHERE ID = ? AND type = "mute";', [id])
        self.conn.execute('INSERT INTO LOGS (ID, TYPE, MOD, TIME, REASON) VALUES(?, "unmute", ?, ?, ?);', [id, mod, datetime.datetime.utcnow(), reason])
        self.conn.commit()

    def remove_ban(self, id, mod, reason):
        """ Removes a ban-record for a user
        """
        self.conn.execute('DELETE FROM PUNISHMENTS WHERE ID = ? AND type = "ban";', [id])
        self.conn.execute('INSERT INTO LOGS (ID, TYPE, MOD, TIME, REASON) VALUES(?, "unban", ?, ?, ?);', [id, mod, datetime.datetime.utcnow(), reason])
        self.conn.commit()

    def remove_log(self, id):
        """ Removes all logs regarding a user
        """
        self.conn.execute('DELETE FROM LOGS WHERE ID = ?;', [id])
        self.conn.commit()

db = DB()
