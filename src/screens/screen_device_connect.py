from kivy.clock import Clock

from kivymd.uix.tab import MDTabsBase
from kivymd.uix.floatlayout import MDFloatLayout

#------------------------------------------------------------------------------

from lib import system
from lib import util
from lib import web_sock_remote

from components import screen
from components import dialogs
from components import snackbar

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class TabLocalDevice(MDFloatLayout, MDTabsBase):

    def on_local_device_button_clicked(self, *args):
        if _Debug:
            print('TabLocalDevice.on_local_device_button_clicked', args)
        screen.main_window().state_node_local = True
        screen.my_app().client_info['local'] = screen.main_window().state_node_local
        screen.my_app().save_client_info()
        screen.stack_clear()
        screen.stack_append('welcome_screen')
        screen.my_app().do_start_controller()

#------------------------------------------------------------------------------

class WebSocketConnectorController(object):

    server_code_input_dialog = None
    confirmation_code_dialog = None
    spinner_dialog = None
    device_check_task = None
    busy = False
    callback_on_success = None
    callback_on_fail = None

    def start_connecting(self, router_url, on_success=None, on_fail=None): 
        if not router_url:
            if on_fail:
                on_fail(None)
            return
        if self.busy:
            if on_fail:
                on_fail(None)
            return
        self.busy = True
        self.callback_on_success = on_success
        self.callback_on_fail = on_fail
        router_url = util.unpack_device_url(router_url.strip())
        screen.main_window().state_node_local = False
        screen.my_app().client_info['local'] = screen.main_window().state_node_local
        screen.my_app().client_info['routers'] = [router_url, ]
        screen.my_app().client_info.pop('key', None)
        screen.my_app().client_info.pop('server_public_key', None)
        screen.my_app().client_info.pop('auth_token', None)
        screen.my_app().client_info.pop('session_key', None)
        screen.my_app().save_client_info()
        self.spinner_dialog = dialogs.open_spinner_dialog(
            title='',
            label='connecting',
            button_cancel='[u][color=#0000dd]Cancel[/color][/u]',
            cb_cancel=self.on_cancel_spinner_dialog,
        )
        if web_sock_remote.is_started():
            web_sock_remote.stop()
        Clock.schedule_once(self._do_connect, 1)

    def on_websocket_open(self, ws_inst):
        if _Debug:
            print('WebSocketConnectorController.on_websocket_open', ws_inst)

    def on_websocket_connect(self, ws_inst):
        if _Debug:
            print('WebSocketConnectorController.on_websocket_connect', ws_inst)
        if self.spinner_dialog:
            self.spinner_dialog.dismiss()
            self.spinner_dialog = None
        if web_sock_remote.is_started():
            web_sock_remote.stop()
        screen.my_app().load_client_info()
        success = bool(screen.my_app().client_info.get('auth_token'))
        # self.ids.qr_scan_open_button.disabled = not system.is_mobile()
        if self.confirmation_code_dialog:
            self.confirmation_code_dialog.dismiss()
            self.confirmation_code_dialog = None
        if success:
            snackbar.info(text='device authorized successfully')
        else:
            snackbar.error(text='device was not authorized')
        if success:
            if self.callback_on_success:
                self.callback_on_success(ws_inst)
                self.callback_on_success = None
        else:
            if self.callback_on_fail:
                self.callback_on_fail(Exception('device was not authorized'), (ws_inst, ))
                self.callback_on_fail = None

    def on_websocket_handshake_failed(self, ws_inst, error):
        if _Debug:
            print('WebSocketConnectorController.on_websocket_handshake_failed', ws_inst, error)
        self.busy = False
        if self.spinner_dialog:
            self.spinner_dialog.dismiss()
            self.spinner_dialog = None
        if self.confirmation_code_dialog:
            self.confirmation_code_dialog.dismiss()
            self.confirmation_code_dialog = None
        if self.server_code_input_dialog:
            self.server_code_input_dialog.dismiss()
            self.server_code_input_dialog = None
        if self.callback_on_fail:
            self.callback_on_fail(error, (ws_inst, ))
            self.callback_on_fail = None

    def on_websocket_error(self, ws_inst, error):
        if _Debug:
            print('WebSocketConnectorController.on_websocket_error', ws_inst, error)
        self.busy = False
        if self.spinner_dialog:
            self.spinner_dialog.dismiss()
            self.spinner_dialog = None
        snackbar.error(text=str(error))
        # self.ids.qr_scan_open_button.disabled = not system.is_mobile()

    def on_websocket_handshake_started(self, ws_inst):
        if _Debug:
            print('WebSocketConnectorController.on_websocket_handshake_started', ws_inst)
        if self.spinner_dialog:
            self.spinner_dialog.dismiss()
            self.spinner_dialog = None
        self.server_code_input_dialog = dialogs.open_number_input_dialog(
            title='Device authorization code',
            text='Please enter the 4 digits authorization code generated in BitDust node running on your desktop/server computer:',
            min_text_length=4,
            max_text_length=4,
            button_confirm='Continue',
            button_cancel='Back',
            cb=self.on_server_code_entered,
        )

    def on_websocket_server_disconnected(self, ws_inst):
        if _Debug:
            print('WebSocketConnectorController.on_websocket_server_disconnected', ws_inst)
        if web_sock_remote.is_started():
            web_sock_remote.stop()
        if self.device_check_task:
            self.device_check_task.cancel()
            self.device_check_task = None
        self.device_check_task = Clock.schedule_once(self._do_connect, 2)

    def on_server_code_entered(self, inp):
        if _Debug:
            print('WebSocketConnectorController.on_server_code_entered', inp, self.server_code_input_dialog)
        if not self.server_code_input_dialog:
            return
        self.server_code_input_dialog = None
        if not inp:
            self.busy = False
            # self.ids.qr_scan_open_button.disabled = not system.is_mobile()
            if web_sock_remote.is_started():
                web_sock_remote.stop()
            return
        client_code = web_sock_remote.continue_handshake(server_code=inp)
        self.confirmation_code_dialog = dialogs.open_message_dialog(
            title='Device confirmation code',
            text='[color=#000]Here is your device confirmation code:\n\n[size=24sp]%s[/size]\n\nEnter those 4 digits in the BitDust node running on your desktop/server computer to complete device authorization procedure.[/color]' % client_code,
            button_confirm='Continue',
            cb=self.on_confirmation_code_dialog_closed,
        )

    def on_confirmation_code_dialog_closed(self, *args, **kwargs):
        self.confirmation_code_dialog = None
        self.busy = False
        # self.ids.qr_scan_open_button.disabled = not system.is_mobile()

    def on_cancel_spinner_dialog(self):
        self.busy = False
        # self.ids.qr_scan_open_button.disabled = not system.is_mobile()
        self.spinner_dialog = None
        if web_sock_remote.is_started():
            web_sock_remote.stop()

    def _do_connect(self, interval=None):
        if _Debug:
            print('WebSocketConnectorController._do_connect')
        web_sock_remote.start(
            callbacks={
                'on_open': self.on_websocket_open,
                'on_handshake_failed': self.on_websocket_handshake_failed,
                'on_connect': self.on_websocket_connect,
                'on_error': self.on_websocket_error,
                'on_handshake_started': self.on_websocket_handshake_started,
                'on_server_disconnected': self.on_websocket_server_disconnected,
            },
            client_info_filepath=screen.my_app().client_info_file_path,
        )

#------------------------------------------------------------------------------

class TabRemoteDevice(MDFloatLayout, MDTabsBase, WebSocketConnectorController):

    def on_remote_device_text_ref_pressed(self, *args):
        if _Debug:
            print('TabRemoteDevice.on_remote_device_text_ref_pressed', args)
        if args[1] == 'web_site_link':
            system.open_url('https://bitdust.io')
        
    def on_qr_scan_open_button_clicked(self, *args):
        if _Debug:
            print('TabRemoteDevice.on_qr_scan_open_button_clicked', args)
        screen.select_screen(
            screen_id='scan_qr_screen',
            scan_qr_callback=self.on_scan_qr_ready,
        )

    def on_scan_qr_ready(self, *args):
        if _Debug:
            print('TabRemoteDevice.on_scan_qr_ready', args)
        screen.screen_back()
        router_url = None
        if args:
            router_url = args[0].strip()
        if not router_url:
            return
        self.start_connecting(
            router_url=router_url,
            on_success=self.on_connection_success,
            on_fail=self.on_connection_failed,
        )

    def on_connection_success(self, err, args):
        if _Debug:
            print('TabRemoteDevice.on_connection_success', err, args)
        screen.my_app().load_client_info()
        screen.my_app().client_info['local'] = False
        screen.my_app().client_info.pop('client_code', None)
        screen.my_app().save_client_info()
        screen.main_window().state_node_local = False
        screen.main_window().state_device_authorized = True
        screen.stack_clear()
        screen.stack_append('welcome_screen')
        screen.my_app().do_start_controller()

    def on_connection_failed(self, err, args):
        if _Debug:
            print('TabRemoteDevice.on_connection_failed', err, args)
        snackbar.error(text=str(err))
        # self.ids.qr_scan_open_button.disabled = not system.is_mobile()

#------------------------------------------------------------------------------

class TabServerDevice(MDFloatLayout, MDTabsBase, WebSocketConnectorController):

    url_input_dialog = None

    def on_server_text_ref_pressed(self, *args):
        if _Debug:
            print('TabServerDevice.on_server_text_ref_pressed', args)
        if args[1] == 'wiki_install_page_link':
            system.open_url('https://bitdust.io/wiki/install.html')
        elif args[1] == 'wiki_device_config_page_link':
            system.open_url('https://bitdust.io/wiki/devices.html')
        
    def on_url_enter_button_clicked(self, *args):
        if _Debug:
            print('TabServerDevice.on_url_enter_button_clicked', args)
        self.url_input_dialog = dialogs.open_text_input_dialog(
            title='Connection info',
            text='Enter device connection URL generated on the remote BitDust node:',
            button_confirm='Continue',
            button_cancel='Back',
            cb=self.on_url_entered,
        )

    def on_url_entered(self, inp):
        if _Debug:
            print('TabServerDevice.on_url_entered', inp)
        self.url_input_dialog = None
        if not inp:
            return
        self.start_connecting(
            router_url=inp,
            on_success=self.on_connection_success,
            on_fail=self.on_connection_failed,
        )

    def on_connection_success(self, err, args):
        if _Debug:
            print('TabServerDevice.on_connection_success', err, args)
        if self.url_input_dialog:
            self.url_input_dialog.dismiss()
            self.url_input_dialog = None
        screen.my_app().load_client_info()
        screen.my_app().client_info['local'] = False
        screen.my_app().client_info.pop('client_code', None)
        screen.my_app().save_client_info()
        screen.main_window().state_node_local = False
        screen.main_window().state_device_authorized = True
        screen.stack_clear()
        screen.stack_append('welcome_screen')
        screen.my_app().do_start_controller()

    def on_connection_failed(self, err, args):
        if _Debug:
            print('TabServerDevice.on_connection_failed', err, args)
        if self.url_input_dialog:
            self.url_input_dialog.dismiss()
            self.url_input_dialog = None
        snackbar.error(text=str(err))
        # self.ids.qr_scan_open_button.disabled = not system.is_mobile()

#------------------------------------------------------------------------------

class TabDemoDevice(MDFloatLayout, MDTabsBase):

    access_key_input_dialog = None

    def on_access_key_enter_button_clicked(self, *args):
        if _Debug:
            print('TabDemoDevice.on_access_key_enter_button_clicked', args)
        # open dialog to paste generated on the server client device info
        self.access_key_input_dialog = dialogs.open_text_input_dialog(
            title='Access key',
            text='Paste access key text content:',
            multiline=True,
            button_confirm='Continue',
            button_cancel='Back',
            cb=self.on_access_key_entered,
        )

    def on_access_key_entered(self, inp):
        if _Debug:
            print('TabDemoDevice.on_access_key_entered', inp)
        self.access_key_input_dialog = None
        if not inp:
            return
        self.start_connecting(
            router_url=inp,
            on_success=self.on_connection_success,
            on_fail=self.on_connection_failed,
        )

    def on_connection_success(self, err, args):
        if _Debug:
            print('TabDemoDevice.on_connection_success', err, args)
        if self.access_key_input_dialog:
            self.access_key_input_dialog.dismiss()
            self.access_key_input_dialog = None
        screen.my_app().load_client_info()
        screen.my_app().client_info['local'] = False
        screen.my_app().client_info.pop('client_code', None)
        screen.my_app().save_client_info()
        screen.main_window().state_node_local = False
        screen.main_window().state_device_authorized = True
        screen.stack_clear()
        screen.stack_append('welcome_screen')
        screen.my_app().do_start_controller()

    def on_connection_failed(self, err, args):
        if _Debug:
            print('TabDemoDevice.on_connection_failed', err, args)
        if self.access_key_input_dialog:
            self.access_key_input_dialog.dismiss()
            self.access_key_input_dialog = None
        snackbar.error(text=str(err))
        # self.ids.qr_scan_open_button.disabled = not system.is_mobile()

    def on_demo_text_ref_pressed(self, *args):
        if _Debug:
            print('TabDemoDevice.on_demo_text_ref_pressed', args)
        if args[1] == 'bitdust_email_link':
            system.open_url('mailto:bitdust.io@gmail.com')
        elif args[1] == 'bitdust_telegram_link':
            system.open_url('https://t.me/bitdust')

#------------------------------------------------------------------------------

class TabWebdockIODevice(MDFloatLayout, MDTabsBase):

    def on_webdock_io_api_token_enter_button_clicked(self, *args):
        if _Debug:
            print('TabWebdockIODevice.on_webdock_io_api_token_enter_button_clicked', args)

    def on_webdock_io_text_ref_pressed(self, *args):
        if _Debug:
            print('TabWebdockIODevice.on_webdock_io_text_ref_pressed', args)
        if args[1] == 'webdock_io_link':
            system.open_url('https://webdock.io')
        elif args[1] == 'webdock_io_profile_page_link':
            system.open_url('https://webdock.io/en/dash/profile')

#------------------------------------------------------------------------------

class DeviceConnectScreen(screen.AppScreen):

    def get_title(self):
        return 'node configuration'

    def on_tab_switched(self, *args):
        if _Debug:
            print('DeviceConnectScreen.on_tab_switched', args)

    def on_enter(self, *args):
        if _Debug:
            print('DeviceConnectScreen.on_enter', args)
        if not self.ids.selection_tabs.ids.carousel.slides:
            if not system.is_mobile():
                self.ids.selection_tabs.add_widget(TabLocalDevice(title='This device'))
            if system.is_mobile():
                self.ids.selection_tabs.add_widget(TabRemoteDevice(title='Remote desktop'))
            self.ids.selection_tabs.add_widget(TabServerDevice(title='Remote server'))
            # self.ids.selection_tabs.add_widget(TabWebdockIODevice(title='Webdock.io'))
            # self.ids.selection_tabs.add_widget(TabDemoDevice(title='Demo'))

    def on_leave(self, *args):
        if _Debug:
            print('DeviceConnectScreen.on_leave', args)
