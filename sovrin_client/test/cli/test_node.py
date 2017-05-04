import pytest
from plenum.common import util

from plenum.test import waits
from stp_core.loop.eventually import eventually

from stp_core.network.port_dispenser import genHa
from plenum.common.constants import NODE_IP, CLIENT_IP, CLIENT_PORT, NODE_PORT, \
    ALIAS, CLIENT_STACK_SUFFIX
from plenum.common.util import randomString
from plenum.test.cli.helper import exitFromCli


def doNodeCmd(do, nodeVals, expMsgs=None):
    expect = expMsgs or ['Node request completed']
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       within=8, expect=expect, mapper=nodeVals)


@pytest.fixture(scope="module")
def tconf(tconf, request):
    oldVal = tconf.UpdateGenesisPoolTxnFile
    tconf.UpdateGenesisPoolTxnFile = True

    def reset():
        tconf.UpdateGenesisPoolTxnFile = oldVal

    request.addfinalizer(reset)
    return tconf


@pytest.fixture(scope="module")
def newNodeAdded(be, do, poolNodesStarted, philCli, newStewardCli,
                 connectedToTest, newNodeVals):
    be(philCli)

    if not philCli._isConnectedToAnyEnv():
        do('connect test', within=3,
           expect=connectedToTest)

    be(newStewardCli)
    doNodeCmd(do, newNodeVals)
    newNodeData = newNodeVals["newNodeData"]

    def checkClientConnected(client):
        name = newNodeData[ALIAS] + CLIENT_STACK_SUFFIX
        assert name in client.nodeReg

    def checkNodeConnected(nodes):
        for node in nodes:
            name = newNodeData[ALIAS]
            assert name in node.nodeReg

    timeout = waits.expectedClientToPoolConnectionTimeout(
        util.getMaxFailures(len(philCli.nodeReg))
    )
    newStewardCli.looper.run(eventually(checkClientConnected,
                                        newStewardCli.activeClient,
                                        timeout=timeout))
    timeout = waits.expectedClientToPoolConnectionTimeout(
        util.getMaxFailures(len(philCli.nodeReg))
    )
    philCli.looper.run(eventually(checkClientConnected,
                                  philCli.activeClient,
                                  timeout=timeout))

    timeout = waits.expectedClientToPoolConnectionTimeout(
        util.getMaxFailures(len(philCli.nodeReg))
    )
    poolNodesStarted.looper.run(eventually(checkNodeConnected,
                                           list(
                                               poolNodesStarted.nodes.values()),
                                           timeout=timeout))
    return newNodeVals


def testAddNewNode(newNodeAdded):
    pass


def testConsecutiveAddSameNodeWithoutAnyChange(be, do, newStewardCli,
                                               newNodeVals, newNodeAdded):
    be(newStewardCli)
    doNodeCmd(do, newNodeVals,
              expMsgs=['node already has the same data as requested'])
    exitFromCli(do)


def testConsecutiveAddSameNodeWithNodeAndClientPortSame(be, do, newStewardCli,
                                                        newNodeVals,
                                                        newNodeAdded):
    be(newStewardCli)
    nodeIp, nodePort = genHa()
    newNodeVals['newNodeData'][NODE_IP] = nodeIp
    newNodeVals['newNodeData'][NODE_PORT] = nodePort
    newNodeVals['newNodeData'][CLIENT_IP] = nodeIp
    newNodeVals['newNodeData'][CLIENT_PORT] = nodePort
    doNodeCmd(do, newNodeVals,
              expMsgs=["node and client ha can't be same"])
    exitFromCli(do)


def testConsecutiveAddSameNodeWithNonAliasChange(be, do, newStewardCli,
                                                 newNodeVals, newNodeAdded):
    be(newStewardCli)
    nodeIp, nodePort = genHa()
    clientIp, clientPort = genHa()
    newNodeVals['newNodeData'][NODE_IP] = nodeIp
    newNodeVals['newNodeData'][NODE_PORT] = nodePort
    newNodeVals['newNodeData'][CLIENT_IP] = nodeIp
    newNodeVals['newNodeData'][CLIENT_PORT] = clientPort
    doNodeCmd(do, newNodeVals)
    exitFromCli(do)


def testConsecutiveAddSameNodeWithOnlyAliasChange(be, do,
                                                  newStewardCli, newNodeVals,
                                                  newNodeAdded):
    be(newStewardCli)
    newNodeVals['newNodeData'][ALIAS] = randomString(6)
    doNodeCmd(do, newNodeVals,
              expMsgs=['existing data has conflicts with request data'])
    exitFromCli(do)
