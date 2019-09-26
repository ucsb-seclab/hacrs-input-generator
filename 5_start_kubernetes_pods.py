import glob
import sys

from config import *
from kubernetes_pods_base import CYBORG_JOB_TYPES

base_dir = DESKTOP_BASE_DIR

def start_challenge_pods(pattern, max_num_pods=-1):
    i = 0
    for event in EVENTS:
        event_results_dir = get_results_dir(base_dir, event)

        for challenge in os.listdir(event_results_dir):
            challenge_results_dir = os.path.join(event_results_dir, challenge)
            if not os.path.isdir(challenge_results_dir):
                continue

            pov_dir = os.path.join(challenge_results_dir, 'pov')
            assert os.path.isdir(pov_dir)

            for pod_file_path in glob.glob(os.path.join(pov_dir, pattern)):
                os.system('/usr/local/bin/kubectl create -f {}'.format(pod_file_path))

                i += 1
                print i
                if 0 <= max_num_pods <= i:
                    return

if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in CYBORG_JOB_TYPES:
        print 'Usage: {} <{}>'.format(sys.argv[0], '|'.join(CYBORG_JOB_TYPES))
        sys.exit(1)

    max_num_pods = -1
    if len(sys.argv) >= 3:
        max_num_pods = int(sys.argv[2])

    start_challenge_pods('{}*.yaml'.format(sys.argv[1]), max_num_pods=max_num_pods)

