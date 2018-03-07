import os
import sys
import sqlite3
import tornado.ioloop
import tornado.web

import database
import uimodules


PATH = os.path.dirname(os.path.realpath(__file__))
pid = str( os.getpid() )
pid_file = open( 'm_server.pid', 'r+' )
pid_file.write( pid )

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html', title='home')

    def post(self):
        service_action = self.get_argument('_service_action')
        if service_action in uimodules.service_actions:
            uimodules.service_actions[service_action](self)
        self.render('index.html', title='home')

class PermHandler(tornado.web.RequestHandler):
    def get(self,permPath):
        paths = permPath.split( '/' )
        cn = sqlite3.connect('makermon.db')
        c = cn.cursor()
        fob_id = ( paths[1], )
        sql = 'SELECT * FROM members m, rfid_tokens r WHERE m.enabled = 1 AND r.member_id = m.id AND r.enabled = 1 AND r.token = ?'
        c.execute( sql, fob_id )
        self.set_status( 403 )
        if len( c.fetchall() ):
            self.set_status( 200 )
            self.write( '{ "result": "authorized" }' )
        self.finish()
        #if paths[0] == 'frontdoor':
        #    self.set_status( 200 )
        #    self.finish()
    def post(self):
        pass

def make_app():
    settings = {
        'debug': True,
        'static_path': os.path.join(PATH, 'static'),
        'template_path': os.path.join(PATH, 'templates'),
        'ui_modules': uimodules
    }

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/perms/(.*)", PermHandler),
    ], **settings)

if __name__ == "__main__":
    db = database.Database( 'makermon.db', database.db_schema )
    app = make_app()
    app.listen(8888)
    print( "Makermon server started..." )
    tornado.ioloop.IOLoop.current().start()
