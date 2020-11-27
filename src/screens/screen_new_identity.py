import time

#------------------------------------------------------------------------------

from components.screen import AppScreen

from lib import websock
from lib import api_client

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

class NewIdentityScreen(AppScreen):

    def is_closable(self):
        return False

    def on_enter(self, *args):
        self.ids.create_identity_button.disabled = False
        self.ids.recover_identity_button.disabled = False
        self.ids.create_identity_result_message.text = ''

    def on_create_identity_button_clicked(self, *args):
        self.ids.create_identity_button.disabled = True
        self.ids.recover_identity_button.disabled = True
        api_client.identity_create(
            username=self.ids.username_input.text,
            join_network=True,
            cb=self.on_identity_create_result,
        )

    def on_identity_create_result(self, resp):
        if _Debug:
            print('on_identity_create_result', resp)
        self.ids.create_identity_button.disabled = False
        self.ids.recover_identity_button.disabled = False
        if not websock.is_ok(resp):
            self.ids.create_identity_result_message.text = '[color=#ff0000]{}[/color]'.format('\n'.join(websock.response_errors(resp)))
            return
        self.ids.create_identity_result_message.text = ''
        self.main_win().select_screen('welcome_screen')
        self.main_win().close_screen('new_identity_screen')
        self.main_win().close_screen('recover_identity_screen')
        self.control().identity_get_latest = time.time()
        self.main_win().state_identity_get = 1

    def on_recover_identity_button_clicked(self, *args):
        self.main_win().select_screen('recover_identity_screen')

#------------------------------------------------------------------------------

from kivy.lang.builder import Builder 
Builder.load_file('./screens/screen_new_identity.kv')