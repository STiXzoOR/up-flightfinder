from pymysql.cursors import DictCursor
import pymysql


def _tosql(value=None, quote=False):
    if not value:
        return 'NULL'

    is_text, value = (True, value.strip()) if isinstance(
        value, str) else (False, value)

    if not is_text:
        return float(value)
    elif quote:
        return "'{value}'".format(value=value)

    return value


def _evaluate_operator(data={}, unquote={}, tosql=False):
    values = []
    param = {}

    for key, value in data.items():
        ex_key = key.strip().rsplit(' ', 1)
        key = ex_key[0].strip()
        operator = ex_key[1] if len(ex_key) == 2 else '='

        values.append('{key} {operator} %({key})s'.format(key=key,
                                                          operator=operator))
        param[key] = value if not tosql else _tosql(
            value, False if key in unquote else True)

    return {'data': values, 'params': param}


class DBHelper():
    def __init__(self, db=None, host='localhost', user='root', password='', socket=None):
        self._db = db
        self._host = host
        self._user = user
        self._password = password
        self._socket = socket

    def __connect__(self):
        try:
            self._connection = pymysql.connect(host=self._host,
                                               user=self._user,
                                               password=self._password,
                                               db=self._db,
                                               unix_socket=self._socket,
                                               charset='utf8mb4',
                                               cursorclass=DictCursor)
        except (pymysql.err.DatabaseError,
                pymysql.err.IntegrityError,
                pymysql.err.MySQLError) as e:
            print(e)
        finally:
            return None if self._connection is None else self._connection.cursor()

    def __diconnect__(self):
        self._connection.close()

    def _query(self, query, param=None, FETCHONE=False, FETCHALL=False, COMMIT=False):
        result = {}

        try:
            cur = self.__connect__()

            if param:
                cur.execute(query, param)
            else:
                cur.executr(query)

            if FETCHONE:
                result = cur.fetchone()
            elif FETCHALL:
                result = cur.fetchall()
            elif COMMIT:
                self._connection.commit()
        except Exception as e:
            print(e)
        finally:
            self.__diconnect__()

        return result

    def _select(self, tables=None, fields='*', condition='', con_data={}, start=0, limit=0, order_by='', group_by='', direction='', is_distinct=False, FETCHONE=False, FETCHALL=False):
        param = {}
        tables = ', '.join(tables)
        fields = ', '.join(fields)

        if isinstance(condition, str):
            param.update(con_data)
            where = condition
        else:
            params = _evaluate_operator(condition)
            where = 'WHERE {values}'.format(
                values=' and '.join(params['data']))
            param.update(params['params'])

        select = 'SELECT' if not is_distinct else 'SELECT DISTINCT'
        query = '{select} {fields} FROM {tables} {where}'.format(select=select,
                                                                 fields=fields,
                                                                 tables=tables,
                                                                 where=where)

        if group_by:
            param['group_by'] = group_by
            group_by = ' GROUP BY %(group_by)s'
            query += group_by

        if order_by:
            param['order_by'] = order_by
            order_by = ' ORDER BY %(order_by)s'
            query += order_by

        if direction:
            param['direction'] = direction
            query += str(direction)

        if limit:
            param['limit'] = limit
            param['start'] = start
            add_limit = ' LIMIT %(start)s, %(limit)s'
            query += add_limit

        self._query(query, param, FETCHONE=FETCHONE, FETCHALL=FETCHALL)

    def fetchrow(self, tables=None, fields='*', condition='', con_data={}, start=0, limit=0, order_by='', group_by='', direction='', is_distinct=False):
        return self._select(tables, fields, condition, con_data, start,
                            limit, order_by, group_by, direction, is_distinct, FETCHONE=True)[0]

    def fetchall(self, tables=None, fields='*', condition='', con_data={}, start=0, limit=0, order_by='', group_by='', direction='', is_distinct=False):
        return self._select(tables, fields, condition, con_data, start,
                            limit, order_by, group_by, direction, is_distinct, FETCHALL=True)

    def insert(self, table=None, data={}, unquote={}, ignore=False):
        keys = []
        vals = []
        param = {}
        for key, value in data.items():
            quote = False if key in unquote else True
            keys.append(key)
            vals.append('%({key})s'.format(key=key))
            param[key] = _tosql(value, quote)

        keys = ', '.join(keys)
        vals = ', '.join(vals)
        insert = 'INSERT' if not ignore else 'INSERT IGNORE'
        ins = "{insert} INTO `{table}` ({keys}) VALUES ({values})".format(insert=insert,
                                                                          table=table,
                                                                          keys=keys,
                                                                          values=vals)

        return self._query(ins, param, COMMIT=True)

    def update(self, table=None, data={}, condition=None, con_data={}, unquote={}):
        result = _evaluate_operator(data, unquote, tosql=True)

        vals = result['data']
        param = result['params']

        if isinstance(condition, str):
            param.update(con_data)
            where = condition
        else:
            params = _evaluate_operator(condition)
            where = 'WHERE {values}'.format(
                values=' and '.join(params['data']))
            param.update(params['params'])

        vals = ', '.join(vals)
        query = "UPDATE `{table}` SET {values} {where}".format(table=table,
                                                               values=vals,
                                                               where=where)

        return self._query(query, param, COMMIT=True)


if __name__ == '__main__':

    import datetime

    DB = DBHelper(db='feiflight', host='localhost', user='root',
                  password='root', socket='/Applications/MAMP/tmp/mysql/mysql.sock')

    From = 'Shanghai'
    to = 'Guangzhou'
    d_date = datetime.datetime.strptime('12/Nov/2019', '%d/%b/%Y').date()
    volume = 1
    cabin_class = 'Economy'

    fields = ['u.name', 'f.id', 'f.date', 'f.from', 'f.depart', 'f.to', 'f.arrival',
              'f.price', 'f.point', 'f.cancel_rule', 'f.change_rule', 'f.volume', 'f.class']
    tables = ['flight f', 'users u']
    where = {'f.company_id': 'u.id',
             'f.from': From,
             'f.to': to,
             'f.date': d_date,
             'f.volume >=': volume,
             'f.class': cabin_class,
             'f.canceled': 0}

    result = DB.fetchall(tables=tables, fields=fields,
                         condition=where, order_by='f.price')
    for item in result:
        print(item)
        print()
