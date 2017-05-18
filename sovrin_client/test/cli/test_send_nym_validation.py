import pytest
from libnacl import randombytes

from plenum.common.signer_did import DidSigner
from plenum.common.signer_simple import SimpleSigner
from plenum.common.util import rawToFriendly, friendlyToHexStr
from sovrin_common.roles import Roles

NYM_ADDED_OUT = 'Nym {dest} added'
ERROR = 'Error:'
INVALID_SYNTAX = "Invalid syntax"


def createUuidIdentifier():
    return rawToFriendly(randombytes(16))


def createUuidIdentifierAndFullVerkey():
    didSigner = DidSigner(identifier=createUuidIdentifier())
    return didSigner.identifier, didSigner.verkey


def createHalfKeyIdentifierAndAbbrevVerkey():
    didSigner = DidSigner()
    return didSigner.identifier, didSigner.verkey


def createCryptonym():
    return SimpleSigner().identifier


def testSendNymSucceedsForUuidIdentifier(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': createUuidIdentifier(),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForUuidIdentifierAndFullVerkey(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier, fullVerkey = createUuidIdentifierAndFullVerkey()

    parameters = {
        'dest': uuidIdentifier,
        'verkey': fullVerkey,
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForHalfKeyIdentifierAndAbbrevVerkey(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForCryptonym(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': createCryptonym(),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForTrusteeRole(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': Roles.TRUSTEE.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForStewardRole(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': Roles.STEWARD.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForTgbRole(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': Roles.TGB.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsForTrustAnchorRole(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


def testSendNymSucceedsWhenRoleIsMissed(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey
    }

    be(trusteeCli)
    do('send NYM dest={dest} verkey={verkey}',
       mapper=parameters, expect=NYM_ADDED_OUT, within=2)


@pytest.mark.skip
def testSendNymFailsIfIdentifierSizeIs15Bytes(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': rawToFriendly(randombytes(15)),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfIdentifierSizeIs17Bytes(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': rawToFriendly(randombytes(17)),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfFullVerkeySizeIs31Bytes(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': rawToFriendly(randombytes(16)),
        'verkey': rawToFriendly(randombytes(31)),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfFullVerkeySizeIs33Bytes(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': rawToFriendly(randombytes(16)),
        'verkey': rawToFriendly(randombytes(33)),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfAbbrevVerkeySizeIs15Bytes(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': rawToFriendly(randombytes(16)),
        'verkey': '~' + rawToFriendly(randombytes(15)),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfAbbrevVerkeySizeIs17Bytes(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': rawToFriendly(randombytes(16)),
        'verkey': '~' + rawToFriendly(randombytes(17)),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfCryptonymSizeIs31Bytes(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': rawToFriendly(randombytes(31)),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfCryptonymSizeIs33Bytes(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': rawToFriendly(randombytes(33)),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfUuidIdentifierIsHexEncoded(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': friendlyToHexStr(createUuidIdentifier()),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfFullVerkeyIsHexEncoded(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier, fullVerkey = createUuidIdentifierAndFullVerkey()

    parameters = {
        'dest': uuidIdentifier,
        'verkey': friendlyToHexStr(fullVerkey),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfAbbrevVerkeyIsHexEncoded(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': '~' + friendlyToHexStr(abbrevVerkey.replace('~', '')),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfCryptonymIsHexEncoded(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': friendlyToHexStr(createCryptonym()),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfIdentifierContainsNonBase58Characters(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()

    parameters = {
        'dest': uuidIdentifier[:5] + '/' + uuidIdentifier[6:],
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfFullVerkeyContainsNonBase58Characters(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier, fullVerkey = createUuidIdentifierAndFullVerkey()

    parameters = {
        'dest': uuidIdentifier,
        'verkey': fullVerkey[:5] + '/' + fullVerkey[6:],
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfAbbrevVerkeyContainsNonBase58Characters(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey[:6] + '/' + abbrevVerkey[7:],
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfCryptonymContainsNonBase58Characters(
        be, do, poolNodesStarted, trusteeCli):

    cryptonym = createCryptonym()

    parameters = {
        'dest': cryptonym[:5] + '/' + cryptonym[6:],
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfFullVerkeyContainsTilde(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier, fullVerkey = createUuidIdentifierAndFullVerkey()

    parameters = {
        'dest': uuidIdentifier,
        'verkey': '~' + fullVerkey,
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfAbbrevVerkeyDoesNotContainTilde(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey.replace('~', ''),
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfRoleIsUnknown(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': 'SUPERVISOR'
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymFailsIfRoleIsSpecifiedUsingNumericCode(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': Roles.TRUST_ANCHOR
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=ERROR, within=2)


@pytest.mark.skip
def testSendNymHasInvalidSyntaxIfIdentifierIsEmpty(
        be, do, poolNodesStarted, trusteeCli):

    _, fullVerkey = createUuidIdentifierAndFullVerkey()

    parameters = {
        'dest': '',
        'verkey': fullVerkey,
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


@pytest.mark.skip
def testSendNymHasInvalidSyntaxIfIdentifierIsMissed(
        be, do, poolNodesStarted, trusteeCli):

    _, fullVerkey = createUuidIdentifierAndFullVerkey()

    parameters = {
        'verkey': fullVerkey,
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM role={role} verkey={verkey}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


@pytest.mark.skip
def testSendNymHasInvalidSyntaxIfVerkeyIsEmpty(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier, _ = createUuidIdentifierAndFullVerkey()

    parameters = {
        'dest': uuidIdentifier,
        'verkey': '',
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


@pytest.mark.skip
def testSendNymHasInvalidSyntaxIfIdentifierAndVerkeyAreMissed(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'role': Roles.TRUST_ANCHOR.name
    }

    be(trusteeCli)
    do('send NYM role={role}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


@pytest.mark.skip
def testSendNymHasInvalidSyntaxIfRoleIsEmpty(
        be, do, poolNodesStarted, trusteeCli):

    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()

    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': ''
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


@pytest.mark.skip
def testSendNymHasInvalidSyntaxIfUnknownParameterIsPassed(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier, fullVerkey = createUuidIdentifierAndFullVerkey()

    parameters = {
        'dest': uuidIdentifier,
        'verkey': fullVerkey,
        'role': Roles.TRUST_ANCHOR.name,
        'extra': 42
    }

    be(trusteeCli)
    do('send NYM dest={dest} role={role} verkey={verkey} extra={extra}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendNymHasInvalidSyntaxIfAllParametersAreMissed(
        be, do, poolNodesStarted, trusteeCli):

    be(trusteeCli)
    do('send NYM', expect=INVALID_SYNTAX, within=2)
