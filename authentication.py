import config
import json
import tornado.auth
import tornado.web

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
            if not user['email'].split('@')[-1] == config.settings["oauth2"]["requiredDomain"]:
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