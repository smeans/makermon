import authentication
import config
import os
import sys
import fcntl
import sqlite3
import tornado.ioloop
import tornado.web

import database
import uimodules


PATH = os.path.dirname(os.path.realpath(__file__))
pid = str( os.getpid() )
try:
    pid_file = open( 'm_server.pid', 'w+' )
    fcntl.flock( pid_file, fcntl.LOCK_EX | fcntl.LOCK_NB )
    pid_file.write( pid )
    pid_file.flush()
except IOError:
    print( "Failed to acquire lock on PID file, program must already be running" )
    sys.exit()

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

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie(config.settings["authCookie"]["name"])

class ExampleAuthRequiredHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        print('user can see secret area')
        self.render('index.html', title='Secret Area')

def make_app():    
    settings = {
        'debug': True,
        'cookie_secret': config.settings["authCookie"]["secret"],
        'google_oauth': {
            'key': config.settings["oauth2"]["clientId"],
            'secret': config.settings["oauth2"]["clientSecret"]
        },
        'login_url': '/auth/login',
        'static_path': os.path.join(PATH, 'static'),
        'template_path': os.path.join(PATH, 'templates'),
        'ui_modules': uimodules
    }

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/auth/login", authentication.GoogleOAuth2LoginHandler),
        (r"/auth/logout", authentication.LogoutHandler),
        (r"/secure", ExampleAuthRequiredHandler),
        (r"/perms/(.*)", PermHandler),
    ], **settings)

if __name__ == "__main__":
    config.init()
    db = database.Database( 'makermon.db', database.db_schema )
    app = make_app()
    app.listen(8888)
    print( "Makermon server started..." )
    tornado.ioloop.IOLoop.current().start()
