import tornado

import members

class Members(tornado.web.UIModule):
    def add_member(handler):
        data = { k: handler.get_argument(k) for k in filter(lambda key: not key.startswith('_'), handler.request.arguments) }
        members.add_member(data)
        
    add_member = staticmethod(add_member)

    def render(self):
        return self.render_string('module-members.html', members=members.members())

service_actions = {'add_member': Members.add_member}
