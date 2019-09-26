import glob
import sys
import subprocess

from config import *
from kubernetes_pods_base import CYBORG_JOB_TYPES

base_dir = DESKTOP_BASE_DIR

def prune_skipped_pods(pattern):
    for event in EVENTS:
        event_results_dir = get_results_dir(base_dir, event)

        for challenge in os.listdir(event_results_dir):
            challenge_results_dir = os.path.join(event_results_dir, challenge)
            if not os.path.isdir(challenge_results_dir):
                continue

            pov_dir = os.path.join(challenge_results_dir, 'pov')
            assert os.path.isdir(pov_dir)

            for pod_file_path in glob.glob(os.path.join(pov_dir, pattern)):
                with open(pod_file_path, 'r') as f:
                    yaml_content = f.read()
                    name_start = yaml_content[yaml_content.index('name: ') + 6:]
                    pod_name = name_start[:name_start.index('\n')]

                cmd = 'kubectl logs {}'.format(pod_name)
                p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                stdout, _ = p.communicate()

                if p.returncode != 0:
                    print "Pod {}: Could not retrieve logs, '{}' failed".format(pod_name, cmd)
                else:

                    if 'SKIPPING' in stdout and 'not found' in stdout:
                        print "$" * 80
                        print "Pod {}: Deleting, was skipped.".format(pod_name)
                        print stdout
                        print "$" * 80
                        del_cmd = 'kubectl delete pod {}'.format(pod_name)
                        #print del_cmd
                        subprocess.check_call(del_cmd, shell=True)
                    else:
                        print stdout.split('\n')[-10:]


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in CYBORG_JOB_TYPES:
        print 'Usage: {} <{}>'.format(sys.argv[0], '|'.join(CYBORG_JOB_TYPES))
        sys.exit(1)

    prune_skipped_pods('{}*.yaml'.format(sys.argv[1]))


