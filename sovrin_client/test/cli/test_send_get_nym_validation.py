from binascii import hexlify

from plenum.common.util import friendlyToRaw

from sovrin_client.test.cli.constants import INVALID_SYNTAX
from sovrin_client.test.cli.helper import createUuidIdentifier, addNym, \
    createHalfKeyIdentifierAndAbbrevVerkey, createCryptonym

CURRENT_VERKEY_FOR_NYM = 'Current verkey for NYM {dest} is {verkey}'
CURRENT_VERKEY_IS_SAME_AS_IDENTIFIER = \
    'Current verkey is same as identifier {dest}'
NYM_NOT_FOUND = 'NYM {dest} not found'


def testSendGetNymSucceedsForExistingUuidDest(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()
    addNym(be, do, trusteeCli, idr=uuidIdentifier, verkey=abbrevVerkey)

    parameters = {
        'dest': uuidIdentifier,
        'verkey': abbrevVerkey
    }

    be(trusteeCli)
    do('send GET_NYM dest={dest}',
       mapper=parameters, expect=CURRENT_VERKEY_FOR_NYM, within=2)


def testSendGetNymFailsForNotExistingUuidDest(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()

    parameters = {
        'dest': uuidIdentifier
    }

    be(trusteeCli)
    do('send GET_NYM dest={dest}',
       mapper=parameters, expect=NYM_NOT_FOUND, within=2)


def testSendGetNymSucceedsForExistingCryptonymDest(
        be, do, poolNodesStarted, trusteeCli):

    cryptonym = createCryptonym()
    addNym(be, do, trusteeCli, idr=cryptonym)

    parameters = {
        'dest': cryptonym
    }

    be(trusteeCli)
    do('send GET_NYM dest={dest}',
       mapper=parameters, expect=CURRENT_VERKEY_IS_SAME_AS_IDENTIFIER, within=2)


def testSendGetNymFailsForNotExistingCryptonymDest(
        be, do, poolNodesStarted, trusteeCli):

    cryptonym = createCryptonym()

    parameters = {
        'dest': cryptonym
    }

    be(trusteeCli)
    do('send GET_NYM dest={dest}',
       mapper=parameters, expect=NYM_NOT_FOUND, within=2)


def testSendGetNymFailsIfDestIsPassedInHexFormat(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()
    addNym(be, do, trusteeCli, idr=uuidIdentifier, verkey=abbrevVerkey)

    hexEncodedUuidIdentifier = hexlify(friendlyToRaw(uuidIdentifier)).decode()

    parameters = {
        'dest': hexEncodedUuidIdentifier
    }

    be(trusteeCli)
    do('send GET_NYM dest={dest}',
       mapper=parameters, expect=NYM_NOT_FOUND, within=2)


def testSendGetNymFailsIfDestIsInvalid(
        be, do, poolNodesStarted, trusteeCli):

    cryptonym = createCryptonym()
    invalidIdentifier = cryptonym[:-4]

    parameters = {
        'dest': invalidIdentifier
    }

    be(trusteeCli)
    do('send GET_NYM dest={dest}',
       mapper=parameters, expect=NYM_NOT_FOUND, within=2)


def testSendGetNymHasInvalidSyntaxIfDestIsEmpty(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': ''
    }

    be(trusteeCli)
    do('send GET_NYM dest={dest}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendGetNymHasInvalidSyntaxIfDestIsOmitted(
        be, do, poolNodesStarted, trusteeCli):

    be(trusteeCli)
    do('send GET_NYM', expect=INVALID_SYNTAX, within=2)


def testSendGetNymHasInvalidSyntaxIfUnknownParameterIsPassed(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()
    addNym(be, do, trusteeCli, idr=uuidIdentifier, verkey=abbrevVerkey)

    parameters = {
        'dest': uuidIdentifier,
        'extra': 42
    }

    be(trusteeCli)
    do('send GET_NYM dest={dest} extra={extra}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)
