#!/usr/bin/env python3

"""
Test performing the following scenarios on behalf of multiple users in parallel:
- some users cyclically update their own verkeys,
- other users cyclically read verkeys of the former users.

To run the test execute this python script providing the following parameters:
-w <NUMBER_OF_USERS_UPDATING_VERKEYS> or --writers <NUMBER_OF_USERS_UPDATING_VERKEYS>
-r <NUMBER_OF_USERS_READING_VERKEYS> or --readers <NUMBER_OF_USERS_READING_VERKEYS>
-i <NUMBER_OF_ITERATIONS> or --iterations <NUMBER_OF_ITERATIONS>
-t <TIMEOUT_IN_SECONDS> or --timeout <TIMEOUT_IN_SECONDS> (optional parameter)

Examples:

test_some_write_keys_others_read_them -w 2 -r 8 -i 10 -t 30

test_some_write_keys_others_read_them --writers 4 --readers 20 --iteration 50
"""

import argparse
import os
from concurrent import futures
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

from stp_core.common.log import getlogger

from sovrin_client.utils.user_scenarios import generateNymsData, \
    NymsCreationScenario, KeyRotationScenario, ForeignKeysReadScenario

STEWARD1_SEED = b"000000000000000000000000Steward1"

logger = getlogger()


def parseArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument("-w", "--writers",
                        type=int,
                        required=True,
                        dest="writers",
                        help="number of writers")

    parser.add_argument("-r", "--readers",
                        type=int,
                        required=True,
                        dest="readers",
                        help="number of readers")

    parser.add_argument("-i", "--iterations",
                        type=int,
                        required=True,
                        dest="iterations",
                        help="number of iterations")

    parser.add_argument("-t", "--timeout",
                        type=int,
                        dest="timeout",
                        help="timeout in seconds")

    return parser.parse_args()


def main(args):
    numOfWriters = args.writers
    numOfReaders = args.readers
    numOfIterations = args.iterations
    timeout = args.timeout

    writers = generateNymsData(numOfWriters)
    readers = generateNymsData(numOfReaders)

    logDir = os.path.join(os.getcwd(), "test-logs-{}".format(
        datetime.now().strftime("%Y-%m-%dT%H-%M-%S")))

    with ProcessPoolExecutor(numOfWriters + numOfReaders) as executor:
        usersIdsAndVerkeys = [(user.identifier, user.verkey)
                              for user in writers + readers]

        nymsCreationScenarioFuture = \
            executor.submit(NymsCreationScenario.runInstance,
                            seed=STEWARD1_SEED,
                            nymsIdsAndVerkeys=usersIdsAndVerkeys,
                            logFileName = os.path.join(
                                logDir,
                                "nyms-creator-{}".format(
                                    STEWARD1_SEED.decode())))

        nymsCreationScenarioFuture.result(timeout=timeout)
        logger.info("Created {} nyms".format(numOfWriters + numOfReaders))

        keyRotationScenariosFutures = \
            [executor.submit(KeyRotationScenario.runInstance,
                             seed=writer.seed,
                             iterations=numOfIterations,
                             logFileName=os.path.join(
                                 logDir,
                                 "writer-{}".format(writer.seed.decode())))
             for writer in writers]

        writersIds = [writer.identifier for writer in writers]

        foreignKeysReadScenariosFutures = \
            [executor.submit(ForeignKeysReadScenario.runInstance,
                             seed=reader.seed,
                             nymsIds=writersIds,
                             iterations=numOfIterations,
                             logFileName=os.path.join(
                                 logDir,
                                 "reader-{}".format(reader.seed.decode())))
             for reader in readers]

        futures.wait(keyRotationScenariosFutures +
                     foreignKeysReadScenariosFutures,
                     timeout=timeout)

        failed = False
        for future in keyRotationScenariosFutures + \
                foreignKeysReadScenariosFutures:
            ex = future.exception(timeout=0)
            if ex:
                failed = True
                logger.exception(ex)

        if failed:
            logger.error("Scenarios of some writers or readers failed")
        else:
            logger.info("Scenarios of all writers and readers "
                        "finished successfully")

    logger.info("Logs of worker processes were also written to {}"
                .format(logDir))


if __name__ == "__main__":
    main(parseArgs())
