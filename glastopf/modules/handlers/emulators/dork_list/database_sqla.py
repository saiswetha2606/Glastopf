# Copyright (C) 2012  Lukas Rist
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import logging
from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.sql import text
from sqlalchemy import select

logger = logging.getLogger(__name__)


class Database(object):
    """
    Responsible for all dork related communication with the glastopf sql database.
    """

    DORK_MAX_LENGTH = 200

    def __init__(self, engine):

        meta = MetaData()
        self.engine = engine

        self.tables = self.create(meta, self.engine)

    def select_data(self, pattern="rfi"):
        url_list = []

        data = self.get_pattern_requests_sql(pattern=pattern)
        data = list(set(data))

        for request in data:
            if request:
                url = request.split('=', 1)[0]
                url_list.append(url)
        return url_list

    def get_pattern_requests_sql(self, pattern="rfi"):
        return_list = []
        sql = text("SELECT request_url FROM events WHERE pattern = :x")
        results = self.engine.connect().execute(sql, x=pattern).fetchall()
        for row in results:
            return_list.append(row[0])
        return return_list

    @classmethod
    def create(cls, meta, engine):
        logger.debug('Creating SQLite database.')
        tables = {}
        tablenames = ["intitle", "intext", "inurl", "filetype", "ext", "allinurl"]
        for table in tablenames:
            tables[table] = Table(
                table, meta,
                Column('content', String(Database.DORK_MAX_LENGTH), primary_key=True),
                Column('count', Integer),
                Column('firsttime', String(30)),
                Column('lasttime', String(30)),
            )
        meta.create_all(engine)
        return tables

    def insert_dorks(self, insert_list):
        logger.debug('Starting insert of {0} dorks into the database.'.format(len(insert_list)))
        if len(insert_list) == 0:
            return

        conn = self.engine.connect()
        trans = conn.begin()

        log = {}
        for item in insert_list:
            tablename = item['table']
            table = self.tables[tablename]
            content = item['content']

            if tablename not in log:
                log[tablename] = 0

            #skip empty
            if not content:
                continue
            content = item['content'][:Database.DORK_MAX_LENGTH]
            dt_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #check table if content exists - content is primary key.
            db_content = conn.execute(
                select([table]).
                where(table.c.content == content)).fetchone()
            if db_content is None:
                conn.execute(
                    table.insert().values({'content': content,
                                           'count': 1,
                                           'firsttime': dt_string,
                                           'lasttime': dt_string}))
                log[tablename] += 1
            else:
                #update existing entry
                conn.execute(
                    table.update().
                    where(table.c.content == content).
                    values(lasttime=dt_string,
                           count=table.c.count + 1))
        trans.commit()
        conn.close()
        logger.debug('Done with insert of {0} dorks into the database.'.format(len(insert_list)))
        logger.debug('New dorks inserted: {0}'.format(log))

    def get_dork_list(self, tablename, starts_with=None):
        conn = self.engine.connect()
        table = self.tables[tablename]

        if starts_with is None:
            result = conn.execute(select([table]))
        else:
            result = conn.execute(
                table.select().
                where(table.c.content.like('%{0}'.format(starts_with))))

        return_list = []
        for entry in result:
            return_list.append(entry[0])
        logger.debug('Returned {0} dorks from the database (starts with: {1})'.format(len(return_list), starts_with))
        return return_list
