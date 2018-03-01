import config
import json
import os
import sqlite3
import tornado.auth
import tornado.ioloop
import tornado.web

import uimodules

PATH = os.path.dirname(os.path.realpath(__file__))

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
        fob_id = paths[1]
        sql = 'SELECT * FROM members WHERE fob_id = "%s"' % ( fob_id )
        c.execute( sql )
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

class GoogleOAuth2LoginHandler(tornado.web.RequestHandler, tornado.auth.GoogleOAuth2Mixin):
    @tornado.gen.coroutine
    def get(self):
        if self.get_current_user():
            print 'someone hit login page but they already logged in'
            self.redirect('/')
            return

        if self.get_argument('code', False):
            print 'someone hit login page with oauth2 token'
            user = yield self.get_authenticated_user(redirect_uri='http://localhost:8888/auth/login', code=self.get_argument('code'))
            if not user:
                print 'not user'
                self.clear_all_cookies() 
                raise tornado.web.HTTPError(500, 'Google authentication failed')

            access_token = str(user['access_token'])
            http_client = self.get_auth_http_client()
            response =  yield http_client.fetch('https://www.googleapis.com/oauth2/v1/userinfo?access_token='+access_token)
            if not response:
                self.clear_all_cookies() 
                raise tornado.web.HTTPError(500, 'Google authentication failed')
            user = json.loads(response.body)
            #TODO: Determine if user['email'] exists in our member table. If so, auth'd. If not, not.
            #For now, this simple check:
            if not user['email'].split('@')[-1] == config.settings["domain"]:
                print 'User ' + user['email'] + ' is not authorized to use this application.'
                self.clear_all_cookies() 
                self.redirect('/')
                return

            print 'User ' + user['email'] + ' logged in via OAuth2.'
            self.set_secure_cookie(config.settings["authCookie"]["name"], user['email'], 1) 
            self.redirect('/')
            return

        elif self.get_secure_cookie(config.settings["authCookie"]["name"]):
            print 'someone hit login page but already has auth session cookie'
            print self.get_secure_cookie(config.settings["authCookie"]["name"])
            self.redirect('/')
            return

        else:
            print 'someone hit login page directly'
            yield self.authorize_redirect(
                redirect_uri='http://localhost:8888/auth/login',
                client_id=config.settings["oauth2"]["clientId"],
                scope=['email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})

class LogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie(config.settings["authCookie"]["name"])
        self.render('logout.html', title='Logged Out')

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
        (r"/auth/login", GoogleOAuth2LoginHandler),
        (r"/auth/logout", LogoutHandler),
        (r"/perms/(.*)", PermHandler),
    ], **settings)

if __name__ == "__main__":
    config.init()
    app = make_app()
    app.listen(8888)
    print( "Makermon server started..." )
    tornado.ioloop.IOLoop.current().start()
