import glob
import subprocess

import os
import sys

from config import DESKTOP_BASE_DIR, EVENTS, get_results_dir
from kubernetes_pods_base import get_pod_id, CYBORG_JOB_TYPES, CYBORG_JOB_SEEDER, CYBORG_JOB_SEEKER

base_dir = DESKTOP_BASE_DIR

def collect_pod_results():
    for event in EVENTS:
        event_results_dir = get_results_dir(base_dir, event)

        for challenge in os.listdir(event_results_dir):
            challenge_results_dir = os.path.join(event_results_dir, challenge)
            if not os.path.isdir(challenge_results_dir):
                continue

            print "{} {} - {} {}".format('#'*40, event, challenge, '#'*40)

            pov_dir = os.path.join(challenge_results_dir, 'pov')
            assert os.path.isdir(pov_dir)

            seeder_pod_id = get_pod_id(CYBORG_JOB_SEEDER, event, challenge)
            print seeder_pod_id
            if not os.path.isfile(os.path.join(pov_dir, '{}.logs'.format(CYBORG_JOB_SEEDER))):
                output = subprocess.check_output('/usr/local/bin/kubectl logs {}'.format(seeder_pod_id), shell=True)
                with open(os.path.join(pov_dir, '{}.logs'.format(CYBORG_JOB_SEEDER)), 'w') as f:
                    f.write(output)

            for crash_info_path in glob.glob(os.path.join(pov_dir, '*.crash_info')):
                pov_name = os.path.basename(crash_info_path)[:-len('.crash_info')]

                pod_id = get_pod_id(CYBORG_JOB_SEEKER, event, challenge, pov_name)
                print pod_id
                if not os.path.isfile(os.path.join(pov_dir, '{}_{}.logs'.format(pov_name, CYBORG_JOB_SEEKER))):
                    command = '/usr/local/bin/kubectl logs {}'.format(pod_id)
                    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate()
                    if len(stderr) > 0:
                        print stderr
                    if process.poll() != 0:
                        print "Command failed: {}".format(command)
                        continue

                    with open(os.path.join(pov_dir, '{}_{}.logs'.format(pov_name, CYBORG_JOB_SEEKER)), 'w') as f:
                        f.write(stdout)

if __name__ == '__main__':
    collect_pod_results()
