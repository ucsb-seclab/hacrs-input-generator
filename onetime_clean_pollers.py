import shutil
import os
import glob
import random
import IPython

from config import *
from onetime_fixing_base import iterate_through_challenges


"""
def remove_for_testing_pollers(event_name, event_dir, challenge_name, challenge_dir):
    poller_dir = os.path.join(challenge_dir, 'poller')
    if not os.path.isdir(poller_dir):
        print "Skipping {} - {}, poller directory not found or not a directory"

    for poller_type in os.listdir(poller_dir):
        if poller_type == 'for-testing':
            poller_sub_dir = os.path.join(poller_dir, poller_type)
            print "{} - {}: [Remove for-testing pollers] => rm -rf {}".format(event_name, challenge_name, poller_sub_dir)
            shutil.rmtree(poller_sub_dir)
        elif poller_type == 'for-release':
            pass
        else:
            print "{} - {}: Unknown poller type {}".format(event_name, challenge_name, poller_type)
            IPython.embed()
"""

num_testcases_to_keep = 20
def remove_too_many_pollers(event_name, event_dir, challenge_name, challenge_dir):
    poller_dir = os.path.join(challenge_dir, 'poller')
    for poller_type in os.listdir(poller_dir):
        print "{} - {}: Pruning {} pollers ... ".format(event_name, challenge_name, poller_type)

        poller_sub_dir = os.path.join(poller_dir, poller_type)

        testcases = sorted(glob.glob(os.path.join(poller_sub_dir, '*.xml')))

        kept_testcases = sorted(random.sample(testcases, min(num_testcases_to_keep, len(testcases))))
        removed_testcases = sorted([t for t in testcases if t not in kept_testcases])
        for t in removed_testcases:
            os.remove(t)


if __name__ == '__main__':
    print "Trimming down the number of pollers per binary ..."
    iterate_through_challenges(remove_too_many_pollers)




