import shutil
import os

from config import *
from onetime_fixing_base import iterate_through_challenges


def rename_challenge_dir_to_identifier(event_name, event_dir, challenge_name, challenge_dir):
    binary_dir = os.path.join(challenge_dir, 'bin')
    assert os.path.isdir(binary_dir)

    binaries = [path for path in os.listdir(binary_dir) if not '_patched' in path]
    if len(binaries) != 1:
        return

    main_binary_name = binaries[0]

    if main_binary_name != challenge_name:
        print "{} - {}: [Name is not equal to identifier] => mv {} {} ".format(event_name, challenge_name, challenge_dir, os.path.join(event_dir, main_binary_name))
        shutil.move(challenge_dir, os.path.join(event_dir, main_binary_name))


def assert_binaries_available(event_name, event_dir, challenge_name, challenge_dir):
    binary_dir = os.path.join(challenge_dir, 'bin')
    assert os.path.isdir(binary_dir)


def filter_no_binaries_available(event_name, event_dir, challenge_name, challenge_dir):
    binary_dir = os.path.join(challenge_dir, 'bin')
    if not os.path.isdir(binary_dir):
        print "{} - {}: rm -rf {} [No binary directory found]".format(event_name, challenge_name, challenge_dir)
        shutil.rmtree(challenge_dir, ignore_errors=True)


def remove_unnecessary_binary_files(event_name, event_dir, challenge_name, challenge_dir):
    binary_dir = os.path.join(challenge_dir, 'bin')
    unnecessary_binaries = [path for path in os.listdir(binary_dir) if '_patched' in path]
    print "{} - {}: Removing unnecessary binary files {}".format(event_name, challenge_name, unnecessary_binaries)
    for bin in unnecessary_binaries:
        os.remove(os.path.join(binary_dir, bin))


def filter_out_multi_bin_challenges(event_name, event_dir, challenge_name, challenge_dir):
    binary_dir = os.path.join(challenge_dir, 'bin')
    executables = [path for path in os.listdir(binary_dir) if not '_patched' in path]
    assert len(executables) >= 1
    if len(executables) > 1:
        print "{} - {}: [Multiple binaries] => rm -rf {}".format(event_name, challenge_name, challenge_dir)
        shutil.rmtree(challenge_dir)


def filter_out_blacklisted_challenges(event_name, event_dir, challenge_name, challenge_dir):
    CHALLENGE_BLACKLIST = {
        EVENT_QUALIFIER: ['KPRCA_00002', 'CROMU_00016', 'NRFIN_00007'],
        EVENT_EXAMPLES: [],
        EVENT_FINALS: [],
    }
    if challenge_name in CHALLENGE_BLACKLIST[event_name]:
        print "{} - {}: [Blacklisted challenge] => rm -rf {}".format(event_name, challenge_name, challenge_dir)
        shutil.rmtree(challenge_dir)


if __name__ == '__main__':
    print "Checking that all builds were successful ... "
    iterate_through_challenges(assert_binaries_available)
    print "Removing unnecessary binary files ..."
    iterate_through_challenges(remove_unnecessary_binary_files)
    print "Filtering out challenges with multiple binaries ..."
    iterate_through_challenges(filter_out_multi_bin_challenges)

    print "Renaming challenge directories to match the identifiers ... "
    iterate_through_challenges(rename_challenge_dir_to_identifier)
    print "Filtering out blacklisted challenges ..."
    iterate_through_challenges(filter_out_blacklisted_challenges)

