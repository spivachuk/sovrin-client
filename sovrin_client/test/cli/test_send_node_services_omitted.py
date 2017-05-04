import pytest
from stp_core.loop.eventually import eventually

from plenum.common.constants import ALIAS, CLIENT_STACK_SUFFIX, SERVICES
from plenum.common.util import getMaxFailures
from plenum.test import waits


@pytest.fixture(scope='module')
def tconf(tconf, request):
    oldVal = tconf.UpdateGenesisPoolTxnFile
    tconf.UpdateGenesisPoolTxnFile = True

    def reset():
        tconf.UpdateGenesisPoolTxnFile = oldVal

    request.addfinalizer(reset)
    return tconf


def testNewNodeAddedWhenServicesParamOmitted(be, do, poolNodesStarted,
                                             philCli, newStewardCli,
                                             connectedToTest, newNodeVals):
    be(philCli)

    if not philCli._isConnectedToAnyEnv():
        do('connect test', within=3,
           expect=connectedToTest)

    # Verify that "send NODE" command succeeds when SERVICES parameter
    # has been omitted
    be(newStewardCli)

    del newNodeVals['newNodeData'][SERVICES]

    do('send NODE dest={newNodeIdr} data={newNodeData}',
       within=8, expect=['Node request completed'], mapper=newNodeVals)

    # Verify that the new node has been actually added to the pool
    newNodeData = newNodeVals['newNodeData']

    def checkClientConnected(client):
        name = newNodeData[ALIAS] + CLIENT_STACK_SUFFIX
        assert name in client.nodeReg

    def checkNodeConnected(nodes):
        for node in nodes:
            name = newNodeData[ALIAS]
            assert name in node.nodeReg

    timeout = waits.expectedClientToPoolConnectionTimeout(
        getMaxFailures(len(philCli.nodeReg))
    )
    newStewardCli.looper.run(eventually(checkClientConnected,
                                        newStewardCli.activeClient,
                                        timeout=timeout))
    timeout = waits.expectedClientToPoolConnectionTimeout(
        getMaxFailures(len(philCli.nodeReg))
    )
    philCli.looper.run(eventually(checkClientConnected,
                                  philCli.activeClient,
                                  timeout=timeout))

    timeout = waits.expectedClientToPoolConnectionTimeout(
        getMaxFailures(len(philCli.nodeReg))
    )
    poolNodesStarted.looper.run(
        eventually(checkNodeConnected,
                   list(poolNodesStarted.nodes.values()),
                   timeout=timeout))
