import json

import pytest

from plenum.common.constants import PUBKEY
from plenum.common.exceptions import BlowUp
from plenum.common.util import cryptonymToHex

# noinspection PyUnresolvedReferences
from sovrin_client.test.cli.conftest \
    import faberMap as faberMapWithoutEndpointPubkey

# noinspection PyUnresolvedReferences
from sovrin_client.test.cli.test_tutorial import aliceAcceptedFaberInvitation, \
    aliceCli, preRequisite, faberWithEndpointAdded, acmeWithEndpointAdded, \
    thriftWithEndpointAdded, walletCreatedForTestEnv, \
    faberInviteSyncedWithEndpoint, faberInviteSyncedWithoutEndpoint, \
    faberInviteLoadedByAlice, acceptInvitation

from sovrin_common.constants import ENDPOINT


@pytest.fixture(scope="module")
def faberMap(faberMapWithoutEndpointPubkey):
    map = faberMapWithoutEndpointPubkey
    endpointAttr = json.loads(map["endpointAttr"])
    base58Key = '5hmMA64DDQz5NzGJNVtRzNwpkZxktNQds21q3Wxxa62z'
    hexKey = cryptonymToHex(base58Key).decode()
    endpointAttr[ENDPOINT][PUBKEY] = hexKey
    map["endpointAttr"] = json.dumps(endpointAttr)
    return map


def testInvitationNotAcceptedIfAgentWasAddedUsingHexAsPubkey(
        be, do, aliceCli, faberMap, preRequisite,
        syncedInviteAcceptedWithClaimsOut, faberInviteSyncedWithEndpoint):
    with pytest.raises(BlowUp):
        acceptInvitation(be, do, aliceCli, faberMap,
                         syncedInviteAcceptedWithClaimsOut)
