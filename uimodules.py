import tornado

import members

class Members(tornado.web.UIModule):
    def add_member(handler):
        data = { k: handler.get_argument(k) for k in filter(lambda key: not key.startswith('_'), handler.request.arguments) }
        members.add_member(data)

    add_member = staticmethod(add_member)

    def delete_member(handler):
        member_id = handler.get_argument('member_id')
        members.delete_member(member_id)

    delete_member = staticmethod(delete_member)

    def add_token(handler):
        data = { k: handler.get_argument(k) for k in filter( lambda key: not key.startswith('_'), handler.request.arguments) }
        members.add_token( data )
    
    add_token = staticmethod( add_token )

    def delete_token(handler):
        token_id = handler.get_argument('token_id')
        members.delete_token( token_id )
    
    delete_token = staticmethod( delete_token )

    def render(self):
        return self.render_string( 'module-members.html', members=members.members(), tokens=members.tokens() )

service_actions = {
    'add_member': Members.add_member,
    'delete_member': Members.delete_member,
    'delete_token': Members.delete_token,
    'add_token': Members.add_token
}
