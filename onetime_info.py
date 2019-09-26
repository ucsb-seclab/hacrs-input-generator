
import os
import glob

from config import *

base_dir = DESKTOP_BASE_DIR

total_valid = 0
total_challenges = 0
for event in EVENTS:
    results_dir = get_results_dir(base_dir, event)

    challenges = os.listdir(results_dir)
    valid_per_event = 0
    for i, challenge_name in enumerate(challenges):
        print "Progress: {}/{}".format(i, len(challenges))

        challenge_results_dir = os.path.join(results_dir, challenge_name)

        valid = True
        s = '{} - {}: '.format(event, challenge_name)
        if len(glob.glob(os.path.join(challenge_results_dir, '*.pcap'))) == 0:
            s += 'no pcap, '
            valid = False
        if len(glob.glob(os.path.join(challenge_results_dir, '*.input'))) == 0:
            s += 'no input file, '
            valid = False
        if len(glob.glob(os.path.join(challenge_results_dir, '*.output'))) == 0:
            s += 'no output file, '
            valid = False
        if len(glob.glob(os.path.join(challenge_results_dir, '*.input.json'))) == 0:
            s += 'no input json, '
            valid = False
        if len(glob.glob(os.path.join(challenge_results_dir, '*.output.json'))) == 0:
            s += 'no output json, '
            valid = False
        if len(glob.glob(os.path.join(challenge_results_dir, '*.crash_info'))) == 0:
            s += 'no crash trace, '
            valid = False

        if valid:
            s += 'VALID, '
            valid_per_event += 1

        print s[:-2]

    print "Event {}: {}/{} valid".format(event, valid_per_event, len(challenges))
    total_valid += valid_per_event
    total_challenges += len(challenges)

print "Total: {}/{} valid".format(total_valid, total_challenges)
