import sqlite3

cn = sqlite3.connect('makermon.db')

schema = {'members': ['name', 'fob_id']}

cn.execute('CREATE TABLE IF NOT EXISTS members (%s)' % ', '.join(schema['members']))
cn.commit()

def escape(s):
    return s.replace("'", "''")

def colnames(data):
    return '%s' % ', '.join([escape(key) for key in data.keys()]);

def valmask(data):
    return ', '.join(['?'] * len(data.keys()))

def vallist(data):
    return tuple([data[key] for key in data.keys()])

def members():
    c = cn.cursor()

    c.execute('SELECT ROWID, * FROM members')
    cols = ['member_id'] + schema['members']

    members = [dict(zip(cols, row)) for row in c.fetchall()]

    return members

def add_member(data):
    sql = 'INSERT INTO members (%s) VALUES (%s)' % (colnames(data), valmask(data))
    cn.execute(sql, vallist(data))
    cn.commit()

def delete_member(member_id):
    cn.execute('DELETE FROM members WHERE ROWID = ?', member_id)
    cn.commit()
