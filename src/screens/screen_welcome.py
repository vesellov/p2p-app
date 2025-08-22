from kivy.clock import Clock
from kivy.metrics import dp

#------------------------------------------------------------------------------

from lib import api_client

from components import webfont
from components import screen
from components import buttons
from components import labels
from components import spinner

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

class WelcomeScreen(screen.AppScreen):

    def __init__(self, **kw):
        self.refresh_task = None
        self.spinner = None
        super(WelcomeScreen, self).__init__(**kw)

    def get_statuses(self):
        return {
            None: '',
            'AT_STARTUP': 'starting',
            'LOCAL': 'initializing local environment',
            'MODULES': 'starting sub-modules',
            'INSTALL': 'installing application',
            'READY': 'application is ready',
            'STOPPING': 'application is shutting down',
            'SERVICES': 'starting network services',
            'INTERFACES': 'starting application interfaces',
            'EXIT': 'application is closed',
        }

    def populate(self):
        if self.refresh_task:
            self.refresh_task.cancel()
            self.refresh_task = None
        self.refresh_task = Clock.schedule_once(lambda dt: self.do_populate(), 0)

    def do_spinner_start(self, label):
        if not self.spinner:
            self.spinner = spinner.CircularProgressBar(
                size_hint=(None, None),
                width=dp(100),
                height=dp(100),
                pos_hint={'center_x': .5},
                max=360,
            )
            self.ids.central_widget.add_widget(self.spinner)
        self.spinner.start(label=label)

    def do_spinner_stop(self):
        if self.spinner:
            self.spinner.stop()
            self.ids.central_widget.remove_widget(self.spinner)
            self.spinner = None

    def do_remove_widgets(self):
        to_remove = []
        for w in self.ids.central_widget.children:
            if isinstance(w, buttons.FillRoundFlatButton):
                to_remove.append(w)
            if isinstance(w, labels.HFlexMarkupLabel):
                to_remove.append(w)
        for w in to_remove:
            self.ids.central_widget.remove_widget(w)
        to_remove.clear()

    def do_add_welcome_items(self):
        self.ids.central_widget.add_widget(labels.HFlexMarkupLabel(text=""))
        self.ids.central_widget.add_widget(labels.HFlexMarkupLabel(text=""))
        self.ids.central_widget.add_widget(labels.HFlexMarkupLabel(text=""))
        self.ids.central_widget.add_widget(labels.HFlexMarkupLabel(text=""))
        self.ids.central_widget.add_widget(labels.HFlexMarkupLabel(text=""))
        btn = buttons.FillRoundFlatButton(
            text="[size=22sp]{}[/size]  [size=16sp][b]create new identity[/b][/size]".format(webfont.md_icon("account-plus")),
            pos_hint={'center_x': .5},
            md_bg_color=self.app().color_success_green,
            text_color=self.app().color_white99,
            on_release=self.on_create_identity_button_clicked,
        )
        self.ids.central_widget.add_widget(btn)
        lbl = labels.HFlexMarkupLabel(
            pos_hint={'center_x': .5},
            markup=True,
            text="[u][color=#0000ff][ref=link]restore existing identity[/ref][/color][/u]",
        )
        lbl.bind(on_ref_press=self.on_restore_existing_identity_pressed)
        self.ids.central_widget.add_widget(lbl)
        self.ids.central_widget.add_widget(labels.HFlexMarkupLabel(text=""))
        self.ids.central_widget.add_widget(labels.HFlexMarkupLabel(text=""))
        self.ids.central_widget.add_widget(labels.HFlexMarkupLabel(text=""))
        self.ids.central_widget.add_widget(labels.HFlexMarkupLabel(text=""))
        self.ids.central_widget.add_widget(labels.HFlexMarkupLabel(text=""))
        # TODO: to be completed
        # lbl = labels.HFlexMarkupLabel(
        #     pos_hint={'center_x': .5},
        #     markup=True,
        #     text="[color=#a0a0a0][ref=link][ network configuration ][/ref][/color]",
        # )
        # lbl.bind(on_ref_press=self.on_network_configuration_pressed)
        # self.ids.central_widget.add_widget(lbl)

    def do_add_home_page_items(self):
        link_search_people = labels.HFlexMarkupLabel(
            pos_hint={'center_x': .5}, markup=True,
            text="[u][color=#0000ff][ref=link]search people[/ref][/color][/u]",
        )
        link_search_people.bind(on_ref_press=self.on_search_people_link_pressed)
        self.ids.central_widget.add_widget(link_search_people)
        link_chat = labels.HFlexMarkupLabel(
            pos_hint={'center_x': .5}, markup=True,
            text="[u][color=#0000ff][ref=link]chat with friends[/ref][/color][/u]",
        )
        link_chat.bind(on_ref_press=self.on_chat_with_friends_link_pressed)
        self.ids.central_widget.add_widget(link_chat)
        link_upload_file = labels.HFlexMarkupLabel(
            pos_hint={'center_x': .5}, markup=True,
            text="[u][color=#0000ff][ref=link]upload a file[/ref][/color][/u]",
        )
        link_upload_file.bind(on_ref_press=self.on_upload_file_link_pressed)
        self.ids.central_widget.add_widget(link_upload_file)
        link_share_file = labels.HFlexMarkupLabel(
            pos_hint={'center_x': .5}, markup=True,
            text="[u][color=#0000ff][ref=link]share a file[/ref][/color][/u]",
        )
        link_share_file.bind(on_ref_press=self.on_share_file_link_pressed)
        self.ids.central_widget.add_widget(link_share_file)

    def do_populate(self):
        self.refresh_task = None
        process_health = self.main_win().state_process_health
        identity_get = self.main_win().state_identity_get
        network_connected = self.main_win().state_network_connected
        if _Debug:
            print('WelcomeScreen.populate process_health=%r identity_get=%r network_connected=%r' % (
                process_health, identity_get, network_connected, ))
        if process_health != 1:
            if _Debug:
                print('    spinner starting, removed widgets')
            self.do_spinner_start(label='starting')
            self.do_remove_widgets()
        else:
            if identity_get == 0:
                if _Debug:
                    print('    spinner starting, removed widgets')
                self.do_spinner_start(label='starting')
                self.do_remove_widgets()
            else:
                if identity_get == -1:
                    if _Debug:
                        print('    spinner stopped')
                    self.do_spinner_stop()
                    btn_exists = False
                    for w in self.ids.central_widget.children:
                        if isinstance(w, buttons.FillRoundFlatButton):
                            if w.text.count('create new identity'):
                                btn_exists = True
                                break
                    if not btn_exists:
                        if _Debug:
                            print('    added create/restore identity buttons')
                        self.do_add_welcome_items()
                else:
                    if _Debug:
                        print('    removed widgets')
                    self.do_remove_widgets()
                    if network_connected != 1:
                        if _Debug:
                            print('    spinner connecting')
                        self.do_spinner_start(label='connecting')
                    else:
                        if _Debug:
                            print('    spinner stopped')
                        self.do_spinner_stop()
                        if identity_get == 1:
                            link_exists = False
                            for w in self.ids.central_widget.children:
                                if isinstance(w, labels.HFlexMarkupLabel):
                                    if w.text.count('search people'):
                                        link_exists = True
                                        break
                            if not link_exists:
                                if _Debug:
                                    print('    added links')
                                self.do_add_home_page_items()

    def call_identity_get(self):
        api_client.identity_get(cb=self.on_identity_get_result)

    def on_search_people_link_pressed(self, instance, value):
        screen.select_screen('search_people_screen')

    def on_chat_with_friends_link_pressed(self, instance, value):
        screen.select_screen('conversations_screen')

    def on_upload_file_link_pressed(self, instance, value):
        screen.select_screen('private_files_screen')

    def on_share_file_link_pressed(self, instance, value):
        screen.select_screen('shares_screen')

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='initializer')

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def on_nav_button_clicked(self):
        pass

    def on_create_identity_button_clicked(self, *args):
        screen.select_screen('new_identity_screen')

    def on_identity_get_result(self, resp):
        if _Debug:
            print('WelcomeScreen.on_identity_get_result', self.main_win().state_process_health, self.main_win().state_identity_get, resp)
        if self.main_win().state_process_health == 1 and self.main_win().state_identity_get != 1 and not api_client.is_ok(resp):
            self.populate()
        else:
            if self.main_win().state_process_health != 1:
                self.populate()
            else:
                self.populate()

    def on_upload_file_button_clicked(self, *args):
        if _Debug:
            print('WelcomeScreen.on_upload_file_button_clicked', args)

    def on_restore_existing_identity_pressed(self, *args):
        screen.select_screen('recover_identity_screen')

    def on_network_configuration_pressed(self, *args):
        screen.select_screen('network_config')
