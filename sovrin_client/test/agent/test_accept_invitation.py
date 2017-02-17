import logging

import pytest

from sovrin_client.test.agent.conftest import checkAcceptInvitation

concerningLogLevels = [logging.WARNING,
                       logging.ERROR,
                       logging.CRITICAL]

# TODO need to solve the root cause of this warning, which is agents
# presuming an identifier is already created on startup
whitelist = ['discarding message.*GET_TXNS.*UnknownIdentifier']


def testFaberCreateLink(faberLinkAdded):
    pass


def testAliceLoadsFaberInvitation(aliceFaberInvitationLoaded):
    pass


def testAliceSyncsFaberInvitationLink(aliceFaberInvitationLinkSynced):
    pass


def testFaberAdded(faberAdded):
    pass


def testAliceAgentConnected(faberAdded, aliceAgentConnected):
    pass


@pytest.mark.skipif('sys.platform == "win32"', reason='SOV-332')
def testAliceAcceptFaberInvitation(aliceAcceptedFaber):
    pass


@pytest.mark.skipif('sys.platform == "win32"', reason='SOV-332')
def testAliceAcceptAcmeInvitation(aliceAcceptedAcme):
    pass


@pytest.mark.skipif(True, reason="Not yet implemented")
def testAddSchema():
    raise NotImplementedError


@pytest.mark.skipif(True, reason="Not yet implemented")
def testAddIssuerKeys():
    raise NotImplementedError


@pytest.mark.skipif(True, reason="Incomplete implementation")
def testMultipleAcceptance(aliceAcceptedFaber,
                           faberIsRunning,
                           faberLinkAdded,
                           faberAdded,
                           walletBuilder,
                           agentBuilder,
                           emptyLooper,
                           faberNonceForAlice):
    """
    For the test agent, Faber. Any invite nonce is acceptable.
    """
    faberAgent, _ = faberIsRunning
    assert len(faberAgent.wallet._links) == 1
    link = next(faberAgent.wallet._links.values())
    wallet = walletBuilder("Bob")
    otherAgent = agentBuilder(wallet)
    emptyLooper.add(otherAgent)

    checkAcceptInvitation(emptyLooper,
                          nonce=faberNonceForAlice,
                          inviteeAgent=otherAgent,
                          inviterAgentAndWallet=faberIsRunning, linkName=link.name)

    assert len(faberAgent.wallet._links) == 2
