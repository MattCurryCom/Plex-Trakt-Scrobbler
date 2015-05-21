from plugin.models.core import db
from plugin.models.account import Account

from playhouse.apsw_ext import *
from trakt import Trakt
import logging

log = logging.getLogger(__name__)


class TraktAccount(Model):
    class Meta:
        database = db
        db_table = 'trakt.account'

    account = ForeignKeyField(Account, 'trakt_accounts', unique=True)

    username = CharField(null=True, unique=True)

    def __init__(self, *args, **kwargs):
        super(TraktAccount, self).__init__(*args, **kwargs)

        self._basic_credential = None
        self._oauth_credential = None

    @property
    def basic(self):
        if self._basic_credential:
            return self._basic_credential

        return self.basic_credentials.first()

    @basic.setter
    def basic(self, value):
        self._basic_credential = value

    @property
    def oauth(self):
        if self._oauth_credential:
            return self._oauth_credential

        return self.oauth_credentials.first()

    @oauth.setter
    def oauth(self, value):
        self._oauth_credential = value

    def authorization(self):
        # OAuth
        oauth = self.oauth

        if oauth:
            return self.oauth_authorization(oauth)

        # Basic (legacy)
        basic = self.basic

        if basic:
            return self.basic_authorization(basic)

        # No account authorization available
        raise Exception("Account hasn't been authenticated")

    def basic_authorization(self, basic_credential=None):
        if basic_credential is None:
            basic_credential = self.basic

        log.debug('Using basic authorization for %r', self)

        return Trakt.configuration.auth(self.username, basic_credential.token)

    def oauth_authorization(self, oauth_credential=None):
        if oauth_credential is None:
            oauth_credential = self.oauth

        log.debug('Using oauth authorization for %r', self)

        return Trakt.configuration.oauth.from_response(oauth_credential.to_response(), refresh=True)

    def to_json(self, full=False):
        result = {
            'id': self.id,
            'username': self.username
        }

        if not full:
            return result

        # Merge authorization details
        result['authorization'] = {
            'basic': {'valid': False},
            'oauth': {'valid': False}
        }

        # - Basic credentials
        basic = self.basic

        if basic is not None:
            result['authorization']['basic'] = basic.to_json(self)

        # - OAuth credentials
        oauth = self.oauth

        if oauth is not None:
            result['authorization']['oauth'] = oauth.to_json()

        return result

    def __repr__(self):
        return '<Account username: %r>' % (
            self.username,
        )
