import os

#------------------------------------------------------------------------------

from lib import api_client
from lib import system

from components import screen

#------------------------------------------------------------------------------

_Debug = False

#------------------------------------------------------------------------------

network_config_content_text = """[size={text_size}]
[color=#909090]name:[/color] {name}
[color=#909090]description:[/color] {label}
[color=#909090]maintainer:[/color] {maintainer}
[color=#909090]contact email:[/color] {contact_email}
[color=#909090]seed nodes:[/color] {seed_nodes}
[/size]"""

#------------------------------------------------------------------------------

class NetworkConfigScreen(screen.AppScreen):

    def populate(self):
        api_client.network_configuration(cb=self.on_network_configuration_result)

    def on_created(self):
        if not system.is_mobile():
            self.ids.qr_scan_open_button.disabled = True

    def on_enter(self, *args):
        if _Debug:
            print('NetworkConfigScreen.on_enter')
        self.populate()

    def on_leave(self, *args):
        if _Debug:
            print('NetworkConfigScreen.on_leave')

    def on_network_configuration_result(self, resp):
        if _Debug:
            print('NetworkConfigScreen.on_network_configuration_result', resp)
        result = api_client.result(resp)
        ctx = dict(
            text_size='{}sp'.format(self.app().font_size_normal_absolute),
        )
        ctx.update(result)
        seed_nodes = set()
        seed_nodes.update(set([n['host'] for n in ((result.get('service_entangled_dht') or {}).get('known_nodes') or [])]))
        seed_nodes.update(set([s['host'] for s in ((result.get('service_identity_propagate') or {}).get('known_servers') or [])]))
        seed_nodes.update(set([n['host'] for n in ((result.get('service_bismuth_blockchain') or {}).get('known_nodes') or [])]))
        ctx['seed_nodes'] = ', '.join(list(seed_nodes))
        self.ids.network_config_content_label.text = network_config_content_text.format(**ctx)

    def on_network_config_content_label_link_pressed(self, *args):
        if _Debug:
            print('NetworkConfigScreen.on_network_config_content_label_link_pressed', args)

    def on_help_text_link_pressed(self, *args):
        if _Debug:
            print('NetworkConfigScreen.on_help_text_link_pressed', args)
        if args[1] == 'wiki_seed_node_link':
            system.open_url('https://bitdust.io/wiki/seed_node.html')

    def on_qr_scan_open_button_clicked(self, *args):
        if _Debug:
            print('NetworkConfigScreen.on_qr_scan_open_button_clicked', args)

    def on_url_enter_button_clicked(self, *args):
        if _Debug:
            print('NetworkConfigScreen.on_url_enter_button_clicked', args)
