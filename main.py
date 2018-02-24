import os
import sqlite3
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

def make_app():
    settings = {
        'debug': True,
        'static_path': os.path.join(PATH, 'static'),
        'template_path': os.path.join(PATH, 'templates'),
        'ui_modules': uimodules
    }

    return tornado.web.Application([
        (r"/", MainHandler),
    ], **settings)

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
