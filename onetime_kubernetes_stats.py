
import os
import glob

from config import DESKTOP_BASE_DIR
from kubernetes_pods_base import CYBORG_JOB_TYPES

concurrent_running = 33

second = 1
minute = second * 60
hour = minute * 60
day = hour * 24

for job_type in CYBORG_JOB_TYPES:
    pattern = '{}*.yaml'.format(job_type)
    matches = glob.glob(os.path.join(DESKTOP_BASE_DIR, 'bins', '**', '**', 'pov', pattern))

    estimated_seconds = int((30 * minute * len(matches)) / concurrent_running)

    estimated_time = "{} days, {} hours, {} minutes, {} seconds".format(int(estimated_seconds / day),
                                                                        int((estimated_seconds % day) / hour),
                                                                        int((estimated_seconds % hour) / minute),
                                                                        int((estimated_seconds % minute) / second))
    print "{}: {} jobs, estimated time: {}".format(job_type, len(matches), estimated_time)


