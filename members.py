import sqlite3

cn = sqlite3.connect('makermon.db')

schema = {'members': ['name', 'fob_id']}

cn.execute('CREATE TABLE IF NOT EXISTS members (%s)' % ', '.join(schema['members']))

def escape(s):
    return s.replace("'", "''")

def colnames(data):
    return '(%s)' % ', '.join([escape(key) for key in data.keys()]);

def valmask(data):
    return ['?'] * len(data.keys())

def vallist(data):
    return tuple([data[key] for key in data.keys()])

def members():
    return []

def add_member(data):
    sql = 'INSERT INTO members (%s) VALUES (%s)' % (colnames(data), valmask(data))

    #cn.execute(sql, vallist(data))
