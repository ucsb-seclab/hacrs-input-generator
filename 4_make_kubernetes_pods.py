import glob

from config import *
from kubernetes_pods_base import CYBORG_JOB_SEEDER, make_cyborg_seeder_pod_file_content, \
    make_cyborg_seeker_pod_file_content, CYBORG_JOB_SEEKER

second = 1
minute = 60 * second

TIMEOUT_IN_SECS = 60 * minute
MEM_LIMIT_POD_IN_GB = 10
MEM_LIMIT_PROCESS_IN_GB = 6

base_dir = DESKTOP_BASE_DIR

for event in EVENTS:
    event_results_dir = get_results_dir(base_dir, event)

    for challenge in os.listdir(event_results_dir):
        challenge_results_dir = os.path.join(event_results_dir, challenge)
        if not os.path.isdir(challenge_results_dir):
            continue

        pov_dir = os.path.join(challenge_results_dir, 'pov')
        assert os.path.isdir(pov_dir)

        with open(os.path.join(pov_dir, '{}.yaml'.format(CYBORG_JOB_SEEDER)), 'w') as pod_file:
            pod_file_content = make_cyborg_seeder_pod_file_content(event, challenge,
                                                                   TIMEOUT_IN_SECS,
                                                                   MEM_LIMIT_POD_IN_GB, MEM_LIMIT_PROCESS_IN_GB)
            pod_file.write(pod_file_content)

        for crash_info_path in glob.glob(os.path.join(pov_dir, '*.crash_info')):
            pov_name = os.path.basename(crash_info_path)[:-len('.crash_info')]

            with open(os.path.join(pov_dir, '{}_{}.yaml'.format(CYBORG_JOB_SEEKER, pov_name)), 'w') as pod_file:
                pod_file_content = make_cyborg_seeker_pod_file_content(event, challenge, pov_name,
                                                                       TIMEOUT_IN_SECS,
                                                                       MEM_LIMIT_POD_IN_GB)
                pod_file.write(pod_file_content)

