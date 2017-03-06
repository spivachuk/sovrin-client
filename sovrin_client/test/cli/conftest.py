import json
import os
import tempfile
import traceback

import itertools
from time import sleep
import re
from typing import List

import plenum
import pytest
from plenum.common.log import getlogger
from plenum.common.raet import initLocalKeep
from plenum.common.eventually import eventually
from plenum.test.conftest import tconf, conf, tdirWithPoolTxns, poolTxnData, \
    dirName, tdirWithDomainTxns, poolTxnNodeNames
from plenum.test.helper import createTempDir

from sovrin_client.cli.helper import USAGE_TEXT, NEXT_COMMANDS_TO_TRY_TEXT
from sovrin_common.txn import SPONSOR, ENDPOINT
from sovrin_node.test.conftest import domainTxnOrderedFields
from sovrin_client.test.helper import createNym, buildStewardClient

plenum.common.util.loggingConfigured = False

from plenum.common.looper import Looper
from plenum.test.cli.helper import newKeyPair, checkAllNodesStarted, \
    checkCmdValid, doByCtx

from sovrin_common.config_util import getConfig
from sovrin_client.test.cli.helper import ensureNodesCreated, getLinkInvitation, \
    getPoolTxnData, newCLI, getCliBuilder, P
from sovrin_client.test.agent.conftest import faberIsRunning as runningFaber, \
    emptyLooper, faberWallet, faberLinkAdded, acmeWallet, acmeLinkAdded, \
    acmeIsRunning as runningAcme, faberAgentPort, acmeAgentPort, faberAgent, \
    acmeAgent, thriftIsRunning as runningThrift, thriftAgentPort, thriftWallet,\
    thriftAgent, agentIpAddress

from plenum.test.conftest import nodeAndClientInfoFilePath

config = getConfig()


@pytest.yield_fixture(scope="session")
def cliTempLogger():
    file_name = "sovrin_cli_test.log"
    file_path = os.path.join(tempfile.tempdir, file_name)
    with open(file_path, 'w') as f:
        pass
    return file_path


@pytest.yield_fixture(scope="module")
def looper():
    with Looper(debug=False) as l:
        yield l


# TODO: Probably need to remove
@pytest.fixture("module")
def nodesCli(looper, tdir, nodeNames):
    cli = newCLI(looper, tdir)
    cli.enterCmd("new node all")
    checkAllNodesStarted(cli, *nodeNames)
    return cli


@pytest.fixture("module")
def cli(looper, tdir):
    return newCLI(looper, tdir)


@pytest.fixture(scope="module")
def newKeyPairCreated(cli):
    return newKeyPair(cli)


@pytest.fixture(scope="module")
def CliBuilder(tdir, tdirWithPoolTxns, tdirWithDomainTxns, tconf, cliTempLogger):
    return getCliBuilder(tdir, tconf, tdirWithPoolTxns, tdirWithDomainTxns,
                         logFileName=cliTempLogger)


@pytest.fixture(scope="module")
def aliceMap():
    return {
        'keyring-name': 'Alice',
    }


@pytest.fixture(scope="module")
def earlMap():
    return {
        'keyring-name': 'Earl',
    }


@pytest.fixture(scope="module")
def susanMap():
    return {
        'keyring-name': 'Susan',
    }


@pytest.fixture(scope="module")
def faberMap(agentIpAddress, faberAgentPort):
    endpoint = "{}:{}".format(agentIpAddress, faberAgentPort)
    return {'inviter': 'Faber College',
            'invite': "sample/faber-invitation.sovrin",
            'invite-not-exists': "sample/faber-invitation.sovrin.not.exists",
            'inviter-not-exists': "non-existing-inviter",
            "target": "FuN98eH2eZybECWkofW6A9BKJxxnTatBCopfUiNxo6ZB",
            "nonce": "b1134a647eb818069c089e7694f63e6d",
            ENDPOINT: endpoint,
            "invalidEndpointAttr": json.dumps({ENDPOINT: " 127.0.0.1:4578"}),
            "endpointAttr": json.dumps({ENDPOINT: endpoint}),
            "claims": "Transcript",
            "claim-to-show": "Transcript",
            "proof-req-to-match": "Transcript",
            }


@pytest.fixture(scope="module")
def acmeMap(agentIpAddress, acmeAgentPort):
    endpoint = "{}:{}".format(agentIpAddress, acmeAgentPort)
    return {'inviter': 'Acme Corp',
            'invite': "sample/acme-job-application.sovrin",
            'invite-not-exists': "sample/acme-job-application.sovrin.not.exists",
            'inviter-not-exists': "non-existing-inviter",
            "target": "7YD5NKn3P4wVJLesAmA1rr7sLPqW9mR1nhFdKD518k21",
            "nonce": "57fbf9dc8c8e6acde33de98c6d747b28c",
            ENDPOINT: endpoint,
            "invalidEndpointAttr": json.dumps({ENDPOINT: "127.0.0.1 :4578"}),
            "endpointAttr": json.dumps({ENDPOINT: endpoint}),
            "proof-requests": "Job-Application",
            "proof-request-to-show": "Job-Application",
            "claim-ver-req-to-show": "0.2",
            "proof-req-to-match": "Job-Application",
            "claims": "<claim-name>",
            "rcvd-claim-transcript-provider": "Faber College",
            "rcvd-claim-transcript-name": "Transcript",
            "rcvd-claim-transcript-version": "1.2"
            }


@pytest.fixture(scope="module")
def thriftMap(agentIpAddress, thriftAgentPort):
    endpoint = "{}:{}".format(agentIpAddress, thriftAgentPort)
    return {'inviter': 'Thrift Bank',
            'invite': "sample/thrift-loan-application.sovrin",
            'invite-not-exists': "sample/thrift-loan-application.sovrin.not.exists",
            'inviter-not-exists': "non-existing-inviter",
            "target": "9jegUr9vAMqoqQQUEAiCBYNQDnUbTktQY9nNspxfasZW",
            "nonce": "77fbf9dc8c8e6acde33de98c6d747b28c",
            ENDPOINT: endpoint,
            "invalidEndpointAttr": json.dumps({ENDPOINT: "127.0.0.1:4A78"}),
            "endpointAttr": json.dumps({ENDPOINT: endpoint}),
            "proof-requests": "Loan-Application-Basic, Loan-Application-KYC",
            "claim-ver-req-to-show": "0.1"
            }


@pytest.fixture(scope="module")
def loadInviteOut(nextCommandsToTryUsageLine):
    return ["1 link invitation found for {inviter}.",
            "Creating Link for {inviter}.",
            ''] + \
           nextCommandsToTryUsageLine + \
           ['    show link "{inviter}"',
            '    accept invitation from "{inviter}"',
            '',
            '']


@pytest.fixture(scope="module")
def fileNotExists():
    return ["Given file does not exist"]


@pytest.fixture(scope="module")
def connectedToTest():
    return ["Connected to test"]


@pytest.fixture(scope="module")
def canNotSyncMsg():
    return ["Cannot sync because not connected"]


@pytest.fixture(scope="module")
def syncWhenNotConnected(canNotSyncMsg, connectUsage):
    return canNotSyncMsg + connectUsage


@pytest.fixture(scope="module")
def canNotAcceptMsg():
    return ["Cannot accept because not connected"]


@pytest.fixture(scope="module")
def acceptWhenNotConnected(canNotAcceptMsg, connectUsage):
    return canNotAcceptMsg + connectUsage


@pytest.fixture(scope="module")
def acceptUnSyncedWithoutEndpointWhenConnected(
        commonAcceptInvitationMsgs, syncedInviteAcceptedOutWithoutClaims):
    return commonAcceptInvitationMsgs + \
        syncedInviteAcceptedOutWithoutClaims


@pytest.fixture(scope="module")
def commonAcceptInvitationMsgs():
    return ["Invitation not yet verified",
            "Link not yet synchronized.",
            ]


@pytest.fixture(scope="module")
def acceptUnSyncedWhenNotConnected(commonAcceptInvitationMsgs,
                                   canNotSyncMsg, connectUsage):
    return commonAcceptInvitationMsgs + \
            ["Invitation acceptance aborted."] + \
            canNotSyncMsg + connectUsage


@pytest.fixture(scope="module")
def usageLine():
    return [USAGE_TEXT]


@pytest.fixture(scope="module")
def nextCommandsToTryUsageLine():
    return [NEXT_COMMANDS_TO_TRY_TEXT]


@pytest.fixture(scope="module")
def connectUsage(usageLine):
    return usageLine + ["    connect <test|live>"]


@pytest.fixture(scope="module")
def notConnectedStatus(connectUsage):
    return ['Not connected to Sovrin network. Please connect first.', ''] +\
            connectUsage +\
            ['', '']


@pytest.fixture(scope="module")
def newKeyringOut():
    return ["New keyring {keyring-name} created",
            'Active keyring set to "{keyring-name}"'
            ]


@pytest.fixture(scope="module")
def linkAlreadyExists():
    return ["Link already exists"]


@pytest.fixture(scope="module")
def jobApplicationProofRequestMap():
    return {
        'proof-request-version': '0.2',
        'proof-request-attr-first_name': 'first_name',
        'proof-request-attr-last_name': 'last_name',
        'proof-request-attr-phone_number': 'phone_number',
        'proof-request-attr-degree': 'degree',
        'proof-request-attr-status': 'status',
        'proof-request-attr-ssn': 'ssn'
    }


@pytest.fixture(scope="module")
def unsyncedInviteAcceptedWhenNotConnected(availableClaims):
    return [
        "Response from {inviter}",
        "Trust established.",
        "Identifier created in Sovrin."
    ] + availableClaims + [
        "Cannot check if identifier is written to Sovrin."
    ]


@pytest.fixture(scope="module")
def syncedInviteAcceptedOutWithoutClaims():
    return [
        "Signature accepted.",
        "Trust established.",
        "Identifier created in Sovrin.",
        "Synchronizing...",
        "Confirmed identifier written to Sovrin."
    ]


@pytest.fixture(scope="module")
def availableClaims():
    return ["Available Claim(s): {claims}"]


@pytest.fixture(scope="module")
def syncedInviteAcceptedWithClaimsOut(
        syncedInviteAcceptedOutWithoutClaims, availableClaims):
    return syncedInviteAcceptedOutWithoutClaims + availableClaims


@pytest.fixture(scope="module")
def unsycedAcceptedInviteWithoutClaimOut(syncedInviteAcceptedOutWithoutClaims):
    return [
        "Invitation not yet verified",
        "Attempting to sync...",
        "Synchronizing...",
    ] + syncedInviteAcceptedOutWithoutClaims + \
           ["Confirmed identifier written to Sovrin."]


@pytest.fixture(scope="module")
def unsycedAlreadyAcceptedInviteAcceptedOut():
    return [
        "Invitation not yet verified",
        "Attempting to sync...",
        "Synchronizing..."
    ]


@pytest.fixture(scope="module")
def showTranscriptProofOut():
    return [
        "Claim ({rcvd-claim-transcript-name} "
        "v{rcvd-claim-transcript-version} "
        "from {rcvd-claim-transcript-provider})",
        "student_name: {attr-student_name}",
        "ssn: {attr-ssn}",
        "degree: {attr-degree}",
        "year: {attr-year}",
        "status: {attr-status}",
    ]


@pytest.fixture(scope="module")
def showJobAppProofRequestOut(showTranscriptProofOut):
    return [
        'Found proof request "{proof-req-to-match}" in link "{inviter}"',
        "Name: {proof-request-to-show}",
        "Version: {proof-request-version}",
        "Status: Requested",
        "Attributes:",
        "{proof-request-attr-first_name}: {set-attr-first_name}",
        "{proof-request-attr-last_name}: {set-attr-last_name}",
        "{proof-request-attr-phone_number}: {set-attr-phone_number}",
        "{proof-request-attr-degree}: {attr-degree}",
        "{proof-request-attr-status}: {attr-status}",
        "{proof-request-attr-ssn}: {attr-ssn}"
    ] + showTranscriptProofOut


@pytest.fixture(scope="module")
def showBankingProofOut():
    return [
        "Claim ({rcvd-claim-banking-name} "
        "v{rcvd-claim-banking-version} "
        "from {rcvd-claim-banking-provider})",
        "title: {attr-title}",
        "first_name: {attr-first_name}",
        "last_name: {attr-last_name}",
        "address_1: {attr-address_1}",
        "address_2: {attr-address_2}",
        "address_3: {attr-address_3}",
        "postcode_zip: {attr-postcode_zip}",
        "date_of_birth: {attr-date_of_birth}",
        "account_type: {attr-account_type}",
        "year_opened: {attr-year_opened}",
        "account_status: {attr-account_status}"
    ]


@pytest.fixture(scope="module")
def proofRequestNotExists():
    return ["No matching Proof Requests found in current keyring"]


@pytest.fixture(scope="module")
def linkNotExists():
    return ["No matching link invitations found in current keyring"]


@pytest.fixture(scope="module")
def faberInviteLoaded(aliceCLI, be, do, faberMap, loadInviteOut):
    be(aliceCLI)
    do("load {invite}", expect=loadInviteOut, mapper=faberMap)


@pytest.fixture(scope="module")
def acmeInviteLoaded(aliceCLI, be, do, acmeMap, loadInviteOut):
    be(aliceCLI)
    do("load {invite}", expect=loadInviteOut, mapper=acmeMap)


@pytest.fixture(scope="module")
def attrAddedOut():
    return ["Attribute added for nym {target}"]


@pytest.fixture(scope="module")
def nymAddedOut():
    return ["Nym {target} added"]


@pytest.fixture(scope="module")
def unSyncedEndpointOut():
    return ["Target endpoint: <unknown, waiting for sync>"]


@pytest.fixture(scope="module")
def showLinkOutWithoutEndpoint(showLinkOut, unSyncedEndpointOut):
    return showLinkOut + unSyncedEndpointOut


@pytest.fixture(scope="module")
def endpointReceived():
    return ["Endpoint received:"]


@pytest.fixture(scope="module")
def endpointNotAvailable():
    return ["Endpoint not available"]


@pytest.fixture(scope="module")
def syncLinkOutEndsWith():
    return ["Link {inviter} synced"]


@pytest.fixture(scope="module")
def syncLinkOutStartsWith():
    return ["Synchronizing..."]


@pytest.fixture(scope="module")
def syncLinkOutWithEndpoint(syncLinkOutStartsWith,
                            syncLinkOutEndsWith):
    return syncLinkOutStartsWith + syncLinkOutEndsWith


@pytest.fixture(scope="module")
def syncLinkOutWithoutEndpoint(syncLinkOutStartsWith):
    return syncLinkOutStartsWith


@pytest.fixture(scope="module")
def showSyncedLinkWithEndpointOut(acceptedLinkHeading, showLinkOut):
    return acceptedLinkHeading + showLinkOut + \
        ["Last synced: "]


@pytest.fixture(scope="module")
def showSyncedLinkWithoutEndpointOut(showLinkOut):
    return showLinkOut


@pytest.fixture(scope="module")
def linkNotYetSynced():
    return ["    Last synced: <this link has not yet been synchronized>"]


@pytest.fixture(scope="module")
def acceptedLinkHeading():
    return ["Link"]


@pytest.fixture(scope="module")
def unAcceptedLinkHeading():
    return ["Link (not yet accepted)"]


@pytest.fixture(scope="module")
def showUnSyncedLinkOut(unAcceptedLinkHeading, showLinkOut):
    return unAcceptedLinkHeading + showLinkOut


@pytest.fixture(scope="module")
def showClaimNotFoundOut():
    return ["No matching Claims found in any links in current keyring"]


@pytest.fixture(scope="module")
def transcriptClaimAttrValueMap():
    return {
        "attr-student_name": "Alice Garcia",
        "attr-ssn": "123-45-6789",
        "attr-degree": "Bachelor of Science, Marketing",
        "attr-year": "2015",
        "attr-status": "graduated"
    }


@pytest.fixture(scope="module")
def transcriptClaimValueMap(transcriptClaimAttrValueMap):
    basic = {
        'inviter': 'Faber College',
        'name': 'Transcript',
        "version": "1.2",
        'status': "available (not yet issued)"
    }
    basic.update(transcriptClaimAttrValueMap)
    return basic

@pytest.fixture(scope="module")
def bankingRelationshipClaimAttrValueMap():
    return {
        "attr-title": "Mrs.",
        "attr-first_name": "Alicia",
        "attr-last_name": "Garcia",
        "attr-address_1": "H-301",
        "attr-address_2": "Street 1",
        "attr-address_3": "UK",
        "attr-postcode_zip": "G61 3NR",
        "attr-date_of_birth": "December 28, 1990",
        "attr-account_type": "savings",
        "attr-year_opened": "2000",
        "attr-account_status": "active"
    }


@pytest.fixture(scope="module")
def transcriptClaimMap():
    return {
        'inviter': 'Faber College',
        'name': 'Transcript',
        'status': "available (not yet issued)",
        "version": "1.2",
        "attr-student_name": "string",
        "attr-ssn": "string",
        "attr-degree": "string",
        "attr-year": "string",
        "attr-status": "string"
    }


@pytest.fixture(scope="module")
def jobCertClaimAttrValueMap():
    return {
        "attr-first_name": "Alice",
        "attr-last_name": "Garcia",
        "attr-employee_status": "Permanent",
        "attr-experience": "3 years",
        "attr-salary_bracket": "between $50,000 to $100,000"
    }


@pytest.fixture(scope="module")
def jobCertificateClaimValueMap(jobCertClaimAttrValueMap):
    basic = {
        'inviter': 'Acme Corp',
        'name': 'Job-Certificate',
        'status': "available (not yet issued)",
        "version": "0.2"
    }
    basic.update(jobCertClaimAttrValueMap)
    return basic


@pytest.fixture(scope="module")
def jobCertificateClaimMap():
    return {
        'inviter': 'Acme Corp',
        'name': 'Job-Certificate',
        'status': "available (not yet issued)",
        "version": "0.2",
        "attr-first_name": "string",
        "attr-last_name": "string",
        "attr-employee_status": "string",
        "attr-experience": "string",
        "attr-salary_bracket": "string"
    }


@pytest.fixture(scope="module")
def reqClaimOut():
    return ["Found claim {name} in link {inviter}",
            "Requesting claim {name} from {inviter}..."]


# TODO Change name
@pytest.fixture(scope="module")
def reqClaimOut1():
    return ["Found claim {name} in link {inviter}",
            "Requesting claim {name} from {inviter}...",
            "Signature accepted.",
            'Received claim "{name}".']


@pytest.fixture(scope="module")
def rcvdTranscriptClaimOut():
    return ["Found claim {name} in link {inviter}",
            "Name: {name}",
            "Status: ",
            "Version: {version}",
            "Attributes:",
            "student_name: {attr-student_name}",
            "ssn: {attr-ssn}",
            "degree: {attr-degree}",
            "year: {attr-year}",
            "status: {attr-status}"
    ]


@pytest.fixture(scope="module")
def rcvdBankingRelationshipClaimOut():
    return ["Found claim {name} in link {inviter}",
            "Name: {name}",
            "Status: ",
            "Version: {version}",
            "Attributes:",
            "title: {attr-title}",
            "first_name: {attr-first_name}",
            "last_name: {attr-last_name}",
            "address_1: {attr-address_1}",
            "address_2: {attr-address_2}",
            "address_3: {attr-address_3}",
            "postcode_zip: {attr-postcode_zip}",
            "date_of_birth: {attr-date_of_birth}",
            "year_opened: {attr-year_opened}",
            "account_status: {attr-account_status}"
            ]


@pytest.fixture(scope="module")
def rcvdJobCertClaimOut():
    return ["Found claim {name} in link {inviter}",
            "Name: {name}",
            "Status: ",
            "Version: {version}",
            "Attributes:",
            "first_name: {attr-first_name}",
            "last_name: {attr-last_name}",
            "employee_status: {attr-employee_status}",
            "experience: {attr-experience}",
            "salary_bracket: {attr-salary_bracket}"
    ]


@pytest.fixture(scope="module")
def showTranscriptClaimOut(nextCommandsToTryUsageLine):
    return ["Found claim {name} in link {inviter}",
            "Name: {name}",
            "Status: {status}",
            "Version: {version}",
            "Attributes:",
            "student_name",
            "ssn",
            "degree",
            "year",
            "status"
            ] + nextCommandsToTryUsageLine + \
           ['request claim "{name}"']


@pytest.fixture(scope="module")
def showJobCertClaimOut(nextCommandsToTryUsageLine):
    return ["Found claim {name} in link {inviter}",
            "Name: {name}",
            "Status: {status}",
            "Version: {version}",
            "Attributes:",
            "first_name",
            "last_name",
            "employee_status",
            "experience",
            "salary_bracket"
            ] + nextCommandsToTryUsageLine + \
           ['request claim "{name}"']


@pytest.fixture(scope="module")
def showBankingRelationshipClaimOut(nextCommandsToTryUsageLine):
    return ["Found claim {name} in link {inviter}",
            "Name: {name}",
            "Status: {status}",
            "Version: {version}",
            "Attributes:",
            "title",
            "first_name",
            "last_name",
            "address_1",
            "address_2",
            "address_3",
            "postcode_zip",
            "date_of_birth",
            "account_type",
            "year_opened",
            "account_status"
            ] + nextCommandsToTryUsageLine + \
           ['request claim "{name}"']


@pytest.fixture(scope="module")
def showLinkWithProofRequestsOut():
    return ["Proof Request(s): {proof-requests}"]


@pytest.fixture(scope="module")
def showLinkWithAvailableClaimsOut():
    return ["Available Claim(s): {claims}"]


@pytest.fixture(scope="module")
def showAcceptedLinkWithClaimReqsOut(showAcceptedLinkOut,
                                     showLinkWithProofRequestsOut,
                                     showLinkWithAvailableClaimsOut,
                                     showLinkSuggestion):
    return showAcceptedLinkOut + showLinkWithProofRequestsOut + \
           showLinkWithAvailableClaimsOut + \
           showLinkSuggestion


@pytest.fixture(scope="module")
def showAcceptedLinkWithoutAvailableClaimsOut(showAcceptedLinkOut,
                                        showLinkWithProofRequestsOut):
    return showAcceptedLinkOut + showLinkWithProofRequestsOut


@pytest.fixture(scope="module")
def showAcceptedLinkWithAvailableClaimsOut(showAcceptedLinkOut,
                                           showLinkWithProofRequestsOut,
                                           showLinkWithAvailableClaimsOut):
    return showAcceptedLinkOut + showLinkWithProofRequestsOut + \
           showLinkWithAvailableClaimsOut


@pytest.fixture(scope="module")
def showLinkSuggestion(nextCommandsToTryUsageLine):
    return nextCommandsToTryUsageLine + \
    ['show claim "{claims}"',
     'request claim "{claims}"']


@pytest.fixture(scope="module")
def showAcceptedLinkOut():
    return [
            "Link",
            "Name: {inviter}",
            "Target: {target}",
            "Target Verification key: <same as target>",
            "Trust anchor: {inviter} (confirmed)",
            "Invitation nonce: {nonce}",
            "Invitation status: Accepted"]


@pytest.fixture(scope="module")
def showLinkOut(nextCommandsToTryUsageLine, linkNotYetSynced):
    return [
            "    Name: {inviter}",
            "    Identifier: not yet assigned",
            "    Trust anchor: {inviter} (not yet written to Sovrin)",
            "    Verification key: <same as local identifier>",
            "    Signing key: <hidden>",
            "    Target: {target}",
            "    Target Verification key: <unknown, waiting for sync>",
            "    Target endpoint: {endpoint}",
            "    Invitation nonce: {nonce}",
            "    Invitation status: not verified, target verkey unknown",
            "    Last synced: {last_synced}"] + \
           [""] + \
           nextCommandsToTryUsageLine + \
           ['    sync "{inviter}"',
            '    accept invitation from "{inviter}"',
            '',
            '']


@pytest.fixture(scope="module")
def showAcceptedSyncedLinkOut(nextCommandsToTryUsageLine):
    return [
            "Link",
            "Name: {inviter}",
            "Trust anchor: {inviter} (confirmed)",
            "Verification key: <same as local identifier>",
            "Signing key: <hidden>",
            "Target: {target}",
            "Target Verification key: <same as target>",
            "Invitation nonce: {nonce}",
            "Invitation status: Accepted",
            "Proof Request(s): {proof-requests}",
            "Available Claim(s): {claims}"] + \
           nextCommandsToTryUsageLine + \
           ['show claim "{claim-to-show}"',
            'send proof "{proof-requests}"']


@pytest.yield_fixture(scope="module")
def poolCLI_baby(CliBuilder):
    yield from CliBuilder("pool")


@pytest.yield_fixture(scope="module")
def aliceCLI(CliBuilder):
    yield from CliBuilder("alice")


@pytest.yield_fixture(scope="module")
def earlCLI(CliBuilder):
    yield from CliBuilder("earl")


@pytest.yield_fixture(scope="module")
def susanCLI(CliBuilder):
    yield from CliBuilder("susan")


@pytest.yield_fixture(scope="module")
def philCLI(CliBuilder):
    yield from CliBuilder("phil")


@pytest.fixture(scope="module")
def poolCLI(poolCLI_baby, poolTxnData, poolTxnNodeNames):
    seeds = poolTxnData["seeds"]
    for nName in poolTxnNodeNames:
        initLocalKeep(nName,
                      poolCLI_baby.basedirpath,
                      seeds[nName],
                      override=True)
    return poolCLI_baby


@pytest.fixture(scope="module")
def poolNodesCreated(poolCLI, poolTxnNodeNames):
    ensureNodesCreated(poolCLI, poolTxnNodeNames)
    return poolCLI


class TestMultiNode:
    def __init__(self, name, poolTxnNodeNames, tdir, tconf,
                 poolTxnData, tdirWithPoolTxns, tdirWithDomainTxns, poolCli):
        self.name = name
        self.poolTxnNodeNames = poolTxnNodeNames
        self.tdir = tdir
        self.tconf = tconf
        self.poolTxnData = poolTxnData
        self.tdirWithPoolTxns = tdirWithPoolTxns
        self.tdirWithDomainTxns = tdirWithDomainTxns
        self.poolCli = poolCli


@pytest.yield_fixture(scope="module")
def multiPoolNodesCreated(request, tconf, looper, tdir, nodeAndClientInfoFilePath,
                          cliTempLogger, namesOfPools=("pool1", "pool2")):
    oldENVS = tconf.ENVS
    oldPoolTxnFile = tconf.poolTransactionsFile
    oldDomainTxnFile = tconf.domainTransactionsFile

    multiNodes=[]
    for poolName in namesOfPools:
        newPoolTxnNodeNames = [poolName + n for n
                               in ("Alpha", "Beta", "Gamma", "Delta")]
        newTdir = os.path.join(tdir, poolName + "basedir")
        newPoolTxnData = getPoolTxnData(
            nodeAndClientInfoFilePath, poolName, newPoolTxnNodeNames)
        newTdirWithPoolTxns = tdirWithPoolTxns(newPoolTxnData, newTdir, tconf)
        newTdirWithDomainTxns = tdirWithDomainTxns(
            newPoolTxnData, newTdir, tconf, domainTxnOrderedFields())
        testPoolNode = TestMultiNode(
            poolName, newPoolTxnNodeNames, newTdir, tconf,
            newPoolTxnData, newTdirWithPoolTxns, newTdirWithDomainTxns, None)

        poolCLIBabyGen = CliBuilder(newTdir, newTdirWithPoolTxns,
                                    newTdirWithDomainTxns, tconf,
                                    cliTempLogger)
        poolCLIBaby = next(poolCLIBabyGen(poolName, looper))
        poolCli = poolCLI(poolCLIBaby, newPoolTxnData, newPoolTxnNodeNames)
        testPoolNode.poolCli = poolCli
        multiNodes.append(testPoolNode)
        ensureNodesCreated(poolCli, newPoolTxnNodeNames)

    def reset():
        tconf.ENVS = oldENVS
        tconf.poolTransactionsFile = oldPoolTxnFile
        tconf.domainTransactionsFile = oldDomainTxnFile

    request.addfinalizer(reset)
    return multiNodes


@pytest.fixture("module")
def ctx():
    """
    Provides a simple container for test context. Assists with 'be' and 'do'.
    """
    return {}


@pytest.fixture("module")
def be(ctx):
    """
    Fixture that is a 'be' function that closes over the test context.
    'be' allows to change the current cli in the context.
    """
    def _(cli):
        ctx['current_cli'] = cli
    return _


@pytest.fixture("module")
def do(ctx):
    """
    Fixture that is a 'do' function that closes over the test context
    'do' allows to call the do method of the current cli from the context.
    """
    return doByCtx(ctx)


@pytest.fixture(scope="module")
def dump(ctx):

    def _dump():
        logger = getlogger()

        cli = ctx['current_cli']
        nocli = {"cli": False}
        wrts = ''.join(cli.cli.output.writes)
        logger.info('=========================================', extra=nocli)
        logger.info('|             OUTPUT DUMP               |', extra=nocli)
        logger.info('-----------------------------------------', extra=nocli)
        for w in wrts.splitlines():
            logger.info('> ' + w, extra=nocli)
        logger.info('=========================================', extra=nocli)
    return _dump


@pytest.fixture(scope="module")
def bookmark(ctx):
    BM = '~bookmarks~'
    if BM not in ctx:
        ctx[BM] = {}
    return ctx[BM]


@pytest.fixture(scope="module")
def current_cli(ctx):
    def _():
        return ctx['current_cli']
    return _


@pytest.fixture(scope="module")
def get_bookmark(bookmark, current_cli):
    def _():
        return bookmark.get(current_cli(), 0)
    return _


@pytest.fixture(scope="module")
def set_bookmark(bookmark, current_cli):
    def _(val):
        bookmark[current_cli()] = val
    return _


@pytest.fixture(scope="module")
def inc_bookmark(get_bookmark, set_bookmark):
    def _(inc):
        val = get_bookmark()
        set_bookmark(val + inc)
    return _


@pytest.fixture(scope="module")
def expect(current_cli, get_bookmark, inc_bookmark):

    def _expect(expected, mapper=None, line_no=None, within=None, ignore_extra_lines=None):
        cur_cli = current_cli()

        def _():
            expected_ = expected if not mapper \
                else [s.format(**mapper) for s in expected]
            assert isinstance(expected_, List)
            bm = get_bookmark()
            actual = ''.join(cur_cli.cli.output.writes).splitlines()[bm:]
            assert isinstance(actual, List)
            explanation = ''
            expected_index = 0
            for i in range(min(len(expected_), len(actual))):
                e = expected_[expected_index]
                assert isinstance(e, str)
                a = actual[i]
                assert isinstance(a, str)
                is_p = type(e) == P
                if (not is_p and a != e) or (is_p and not e.match(a)):
                    if ignore_extra_lines:
                        continue
                    explanation += "line {} doesn't match\n"\
                                   "  expected: {}\n"\
                                   "    actual: {}\n".format(i, e, a)
                expected_index += 1

            if len(expected_) > len(actual):
                for e in expected_:
                    try:
                        p = re.compile(e) if type(e) == P else None
                    except Exception as err:
                        explanation += "ERROR COMPILING REGEX for {}: {}\n".\
                            format(e, err)
                    for a in actual:
                        if (p and p.fullmatch(a)) or a == e:
                            break
                    else:
                        explanation += "missing: {}\n".format(e)

            if len(expected_) < len(actual) and ignore_extra_lines is None:
                for a in actual:
                    for e in expected_:
                        p = re.compile(e) if type(e) == P else None
                        if (p and p.fullmatch(a)) or a == e:
                            break
                    else:
                        explanation += "extra: {}\n".format(a)

            if explanation:
                explanation += "\nexpected:\n"
                for x in expected_:
                    explanation += "  > {}\n".format(x)
                explanation += "\nactual:\n"
                for x in actual:
                    explanation += "  > {}\n".format(x)
                if line_no:
                    explanation += "section ends line number: {}\n".format(line_no)
                pytest.fail(''.join(explanation))
            else:
                inc_bookmark(len(actual))
        if within:
            cur_cli.looper.run(eventually(_, timeout=within))
        else:
            _()

    return _expect


@pytest.fixture(scope="module")
def steward(poolNodesCreated, looper, tdir, stewardWallet):
    return buildStewardClient(looper, tdir, stewardWallet)


@pytest.fixture(scope="module")
def faberAdded(poolNodesCreated,
             looper,
             aliceCLI,
             faberInviteLoaded,
             aliceConnected,
            steward, stewardWallet):
    li = getLinkInvitation("Faber", aliceCLI.activeWallet)
    createNym(looper, li.remoteIdentifier, steward, stewardWallet,
              role=SPONSOR)


@pytest.fixture(scope="module")
def faberIsRunningWithoutNymAdded(emptyLooper, tdirWithPoolTxns, faberWallet,
                                  faberAgent):
    faber, faberWallet = runningFaber(emptyLooper, tdirWithPoolTxns,
                                      faberWallet, faberAgent, None)
    return faber, faberWallet


@pytest.fixture(scope="module")
def faberIsRunning(emptyLooper, tdirWithPoolTxns, faberWallet,
                   faberAddedByPhil, faberAgent):
    faber, faberWallet = runningFaber(emptyLooper, tdirWithPoolTxns,
                                      faberWallet, faberAgent, faberAddedByPhil)
    return faber, faberWallet


@pytest.fixture(scope="module")
def acmeIsRunning(emptyLooper, tdirWithPoolTxns, acmeWallet,
                   acmeAddedByPhil, acmeAgent):
    acme, acmeWallet = runningAcme(emptyLooper, tdirWithPoolTxns,
                                   acmeWallet, acmeAgent, acmeAddedByPhil)

    return acme, acmeWallet


@pytest.fixture(scope="module")
def thriftIsRunning(emptyLooper, tdirWithPoolTxns, thriftWallet,
                    thriftAddedByPhil, thriftAgent):
    thrift, thriftWallet = runningThrift(emptyLooper, tdirWithPoolTxns,
                                         thriftWallet, thriftAgent,
                                         thriftAddedByPhil)

    return thrift, thriftWallet


@pytest.fixture(scope="module")
def schemaAdded():
    return ["credential definition is published"]


@pytest.fixture(scope="module")
def issuerKeyAdded():
    return ["issuer key is published"]


@pytest.fixture(scope='module')
def savedKeyringRestored():
    return ['Saved keyring {keyring-name} restored']


# TODO: Need to refactor following three fixture to reuse code
@pytest.yield_fixture(scope="module")
def cliForMultiNodePools(request, multiPoolNodesCreated, tdir,
                         tdirWithPoolTxns, tdirWithDomainTxns, tconf,
                         cliTempLogger):
    oldENVS = tconf.ENVS
    oldPoolTxnFile = tconf.poolTransactionsFile
    oldDomainTxnFile = tconf.domainTransactionsFile

    yield from getCliBuilder(tdir, tconf, tdirWithPoolTxns, tdirWithDomainTxns,
                             cliTempLogger, multiPoolNodesCreated)("susan")

    def reset():
        tconf.ENVS = oldENVS
        tconf.poolTransactionsFile = oldPoolTxnFile
        tconf.domainTransactionsFile = oldDomainTxnFile

    request.addfinalizer(reset)


@pytest.yield_fixture(scope="module")
def aliceMultiNodePools(request, multiPoolNodesCreated, tdir,
                        tdirWithPoolTxns, tdirWithDomainTxns, tconf,
                        cliTempLogger):
    oldENVS = tconf.ENVS
    oldPoolTxnFile = tconf.poolTransactionsFile
    oldDomainTxnFile = tconf.domainTransactionsFile

    yield from getCliBuilder(tdir, tconf, tdirWithPoolTxns, tdirWithDomainTxns,
                             cliTempLogger, multiPoolNodesCreated)("alice")

    def reset():
        tconf.ENVS = oldENVS
        tconf.poolTransactionsFile = oldPoolTxnFile
        tconf.domainTransactionsFile = oldDomainTxnFile

    request.addfinalizer(reset)


@pytest.yield_fixture(scope="module")
def earlMultiNodePools(request, multiPoolNodesCreated, tdir,
                       tdirWithPoolTxns, tdirWithDomainTxns, tconf,
                       cliTempLogger):
    oldENVS = tconf.ENVS
    oldPoolTxnFile = tconf.poolTransactionsFile
    oldDomainTxnFile = tconf.domainTransactionsFile

    yield from getCliBuilder(tdir, tconf, tdirWithPoolTxns, tdirWithDomainTxns,
                             cliTempLogger, multiPoolNodesCreated)("earl")

    def reset():
        tconf.ENVS = oldENVS
        tconf.poolTransactionsFile = oldPoolTxnFile
        tconf.domainTransactionsFile = oldDomainTxnFile

    request.addfinalizer(reset)


@pytest.yield_fixture(scope="module")
def trusteeCLI(CliBuilder):
    yield from CliBuilder("newTrustee")


@pytest.fixture(scope="module")
def trusteeMap(trusteeWallet):
    return {
        'trusteeSeed': bytes(trusteeWallet._signerById(
            trusteeWallet.defaultId).sk).decode(),
        'trusteeIdr': trusteeWallet.defaultId,
    }


@pytest.fixture(scope="module")
def trusteeCli(be, do, trusteeMap, poolNodesStarted,
               connectedToTest, nymAddedOut, trusteeCLI):
    be(trusteeCLI)
    do('new key with seed {trusteeSeed}', expect=[
        'Identifier for key is {trusteeIdr}',
        'Current identifier set to {trusteeIdr}'],
       mapper=trusteeMap)

    if not trusteeCLI._isConnectedToAnyEnv():
        do('connect test', within=3,
           expect=connectedToTest)

    return trusteeCLI


@pytest.fixture(scope="module")
def poolNodesStarted(be, do, poolCLI):
    be(poolCLI)

    connectedExpect=[
        'Alpha now connected to Beta',
        'Alpha now connected to Gamma',
        'Alpha now connected to Delta',
        'Beta now connected to Alpha',
        'Beta now connected to Gamma',
        'Beta now connected to Delta',
        'Gamma now connected to Alpha',
        'Gamma now connected to Beta',
        'Gamma now connected to Delta',
        'Delta now connected to Alpha',
        'Delta now connected to Beta',
        'Delta now connected to Gamma']

    primarySelectedExpect = [
        'Alpha:0 selected primary',
        'Alpha:1 selected primary',
        'Beta:0 selected primary',
        'Beta:1 selected primary',
        'Gamma:0 selected primary',
        'Gamma:1 selected primary',
        'Delta:0 selected primary',
        'Delta:1 selected primary',
        ]

    do('new node all', within=6, expect = connectedExpect)
    # do(None, within=4, expect=primarySelectedExpect)
    return poolCLI
