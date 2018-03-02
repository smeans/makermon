import sqlite3

cn = sqlite3.connect('makermon.db')

schema = { 
    'members': [ 'id', 'first_name', 'last_name', 'email', 'start_date', 'expiration_date', 'admin'  ],
    'rfid_tokens': [ 'id', 'member_id', 'token' ]
}

#cn.execute('CREATE TABLE IF NOT EXISTS members (%s)' % ', '.join(schema['members']))
#cn.commit()

def escape(s):
    return s.replace("'", "''")

def colnames(data):
    return '%s' % ', '.join([escape(key) for key in data.keys()])

def valmask(data):
    return ', '.join(['?'] * len(data.keys()))

def vallist(data):
    return tuple([data[key] for key in data.keys()])

def tokens():
    c = cn.cursor()
    c.execute( 'SELECT * FROM rfid_tokens WHERE enabled = 1' )

    return [dict(zip(schema['rfid_tokens'], row)) for row in c.fetchall()]
    
def members():
    c = cn.cursor()

    c.execute('SELECT * FROM members WHERE enabled = 1')
    cols = schema['members']

    members = [dict(zip(cols, row)) for row in c.fetchall()]

    return members

def add_member(data):
    sql = 'INSERT INTO members (%s) VALUES (%s)' % (colnames(data), valmask(data))
    cn.execute(sql, vallist(data))
    cn.commit()

def delete_member(member_id):
    cn.execute('UPDATE members SET enabled = 0 WHERE id = ?', member_id)
    cn.commit()

def add_token( data ):
    sql = 'INSERT INTO rfid_tokens (%s) VALUES (%s)' % ( colnames( data ), valmask( data ) )
    cn.execute( sql, vallist( data ) )
    cn.commit()
    
def delete_token( token_id ):
    cn.execute( 'UPDATE rfid_tokens SET enabled = 0 WHERE id = ?', token_id )
    cn.commit()