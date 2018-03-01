# Handle database connections / requests and initial database creation / schema tracking
# The schema set up like this might be mostly useless after initial db creation... 
# might still be good to have for schema tracking??
import sqlite3

database = "makermon.db"
db_con = None
db_schema = {
    'members': [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',     #autoincrement this instead of rowid so that id linking is not broken if a rowid is reused after a delete or db change
        'first_name VARCHAR(25)',                   #apparently sqlite doesn't use the length of a varchar, just treats column as text
        'last_name VARCHAR(25)',
        'email VARCHAR(50)',
        'start_date INTEGER',                       #integer for date fields will use unix time
        'expiration_date INTEGER',
        'admin INTEGER'                             #has admin privileges
    ],
    'rfid_tokens': [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'member_id INTEGER',
        'token VARCHAR(50)',                        #the token id stored on the card
        'enabled INTEGER',
        'FOREIGN KEY( member_id ) REFERENCES members( id )'
    ],
    'items': [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'description TEXT',
        'enabled INTEGER',
        'disabled_reason TEXT'
    ],
    'training': [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'description TEXT',
        'valid_length INTEGER'
    ],
    'required_training': [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'training_id INTEGER',
        'item_id INTEGER',
        'FOREIGN KEY( training_id ) REFERENCES training( id )',
        'FOREIGN KEY( item_id ) REFERENCES items( id )'
    ],
    'completed_training': [
        'id INTEGER PRIMARY KEY AUTOINCREMENT',
        'training_id INTEGER',
        'member_id INTEGER',
        'complete_date INTEGER',
        'expiration_date INTEGER',
        'FOREIGN KEY( training_id ) REFERENCES training( id )',
        'FOREIGN KEY( member_id ) REFERENCES members( id )'
    ]
}

#after connecting to database must execute
#PRAGMA foreign_keys = ON;
#disabled by defaul for backwards compat with sqlite2.
def db_initialize():
    #TODO: probably need to add a try / catch here to confirm connection
    db_con = sqlite3.connect( database )
    db_con.execute( 'PRAGMA foreign_keys = ON;' )    
    
    #initialize database creating non existant tables
    for table in db_schema:
        db_con.execute( 'CREATE TABLE IF NOT EXISTS %s ( %s )' % ( table, ', '.join( db_schema[ table ] ) ) )
    
    db_con.commit()

db_initialize()