import os

from config import *

base_dir = DESKTOP_BASE_DIR

def iterate_through_challenges(callback):

    for event in EVENTS:
        event_dir = get_challenges_dir(base_dir, event)

        challenges = os.listdir(event_dir)
        for challenge_name in challenges:
            challenge_dir = os.path.join(event_dir, challenge_name)
            if not os.path.isdir(challenge_dir):
                print "Skipping {} - {}, not a challenge".format(event, challenge_name)
                continue

            callback(event, event_dir, challenge_name, challenge_dir)
