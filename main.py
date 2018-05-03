#!/usr/bin/python
import os
import sqlite3
import tornado.ioloop
import tornado.web
import time
import sys
import random

import database
import uimodules
import twitter

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
        print self.request,  time.time(), time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        sys.stdout.flush()
        paths = permPath.split( '/' )
        cn = sqlite3.connect('makermon.db')
        c = cn.cursor()
        fob_id = ( paths[1], )
        sql = 'SELECT * FROM members m, rfid_tokens r WHERE m.enabled = 1 AND r.member_id = m.id AND r.enabled = 1 AND r.token = ?'
        c.execute( sql, fob_id )
        self.set_status( 403 )
        if len( c.fetchall() ):
            self.set_status( 200 )
            try:
                curr_time = time.time()
                if (curr_time - self.settings['twitter_last_tweet']) > self.settings['twitter_cooldown_sec']:
                    tweet = random.choice(self.settings['twitter_tweet_pool'])
                    print "tweeting:",tweet
                    self.settings['twitter_api'].PostUpdate(tweet)
                    self.settings['twitter_last_tweet'] = curr_time
            except Exception, err:
                print "failed to post to twitter", err.message
                
            self.write( '{ "result": "authorized" }' )
        self.finish()
        #if paths[0] == 'frontdoor':
        #    self.set_status( 200 )
        #    self.finish()
    def post(self):
        pass

def make_app():

    key_dir = "twitter_keys/"
    with open(key_dir + "access-token.key","r") as f:
        access_token_key = f.readline().strip()
    with open(key_dir + "access-token-secret.key", "r") as f:
        access_token_secret = f.readline().strip()
    with open(key_dir + "consumer.key", "r") as f:
        consumer_key = f.readline().strip()
    with open(key_dir + "consumer-secret.key", "r") as f:
        consumer_secret = f.readline().strip()

    with open("twitter_pool.txt", "r") as f:
        pool_lines = f.readlines()
    pool = [line.strip() for line in pool_lines]
    print pool
		

    api = twitter.Api(consumer_key = consumer_key,
                      consumer_secret = consumer_secret,
                      access_token_key = access_token_key,
                      access_token_secret = access_token_secret)

    settings = {
        'debug': True,
        'static_path': os.path.join(PATH, 'static'),
        'template_path': os.path.join(PATH, 'templates'),
        'ui_modules': uimodules,
        'twitter_api': api,
        'twitter_tweet_pool': pool,
        'twitter_last_tweet': 0,
        'twitter_cooldown_sec': 60*10
    }

    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/perms/(.*)", PermHandler),
    ], **settings)

if __name__ == "__main__":
    db = database.Database( 'makermon.db', database.db_schema )
    app = make_app()
    app.listen(8888)
    print( "Makermon server started...", time.time(), time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()) )
    sys.stdout.flush()
    tornado.ioloop.IOLoop.current().start()
