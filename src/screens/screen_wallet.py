import os

#------------------------------------------------------------------------------

from kivy.metrics import dp
from kivy.properties import StringProperty  # @UnresolvedImport

#------------------------------------------------------------------------------

from kivy.clock import Clock

from kivymd.uix.list import TwoLineIconListItem

#------------------------------------------------------------------------------

from lib import system
from lib import api_client

from components import screen
from components import dialogs
from components import snackbar

#------------------------------------------------------------------------------

_Debug = True

#------------------------------------------------------------------------------

wallet_details_temlate_text = """
"""

#------------------------------------------------------------------------------

class TransactionItem(TwoLineIconListItem):

    tx_id = StringProperty()
    label = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = dp(48) if not self._height else self._height

    def on_pressed(self):
        if _Debug:
            print('TransactionItem.on_pressed', self)

#------------------------------------------------------------------------------

class WalletScreen(screen.AppScreen):

    def get_statuses(self):
        return {
            None: "blockchain service is not started",
            "ON": "blockchain is connected and synchronized",
            "OFF": "blockchain service is switched off",
            "NOT_INSTALLED": "blockchain service is not installed",
            "INFLUENCE": "turning off dependent network services",
            "STARTING": "blockchain service is starting",
            "DEPENDS_OFF": "related network services were not started yet",
            "STOPPING": "blockchain service is stopping",
            "CLOSED": "blockchain service is closed",
        }

    def on_enter(self, *args):
        self.ids.state_panel.attach(automat_id='service_bismuth_wallet')
        api_client.blockchain_wallet_balance(cb=self.on_blockchain_wallet_balance_result)
        api_client.blockchain_wallet_transactions(cb=self.on_blockchain_wallet_transactions_result)

    def on_leave(self, *args):
        self.ids.state_panel.release()

    def on_blockchain_wallet_balance_result(self, resp):
        if not api_client.is_ok(resp):
            self.ids.wallet_details.text = 'fetching blockchain info ...'
            return
        result = api_client.response_result(resp)
        if not result:
            self.ids.wallet_details.text = 'fetching blockchain info ...'
            return
        self.ids.wallet_details.text = str(result)

    def on_blockchain_wallet_transactions_result(self, resp):
        if not api_client.is_ok(resp):
            return
        self.ids.transactions_list_view.clear_widgets()
        for tx in api_client.response_result(resp):
            self.ids.transactions_list_view.clear_widgets()
            self.ids.conversations_list_view.add_widget(ConversationItem(
                type=conv['type'],
                conversation_id=conv['conversation_id'],
                key_id=conv['key_id'],
                state=conv['state'],
                label=conv['label'],
                automat_index=conv['automat_index'],
                automat_id=conv['automat_id'],
            ))
        # TODO: ...

    def on_wallet_details_ref_pressed(self, *args):
        if _Debug:
            print('WalletScreen.on_wallet_details_ref_pressed', args)
