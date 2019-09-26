CYBORG_JOB_SEEKER = 'cyborg-seeker'
CYBORG_JOB_SEEDER = 'cyborg-seeder'
CYBORG_JOB_TYPES = [CYBORG_JOB_SEEDER, CYBORG_JOB_SEEKER]

POD_BASE_FORMAT = """apiVersion: v1
kind: Pod
metadata:
  name: {pod_id}
  labels:
    type: {type}
spec:  # specification of the pod's contents
  restartPolicy: Never #OnFailure

  imagePullSecrets:
  - name: ucsbseclab-dockerhub

  volumes:
  - name: cyborg-results
    persistentVolumeClaim:
      claimName: cyborg-results

  containers:
  - name: {pod_id}

    stdin: true
    tty: true

    image: "zardus/research:cyborg-generator"
    command: ["/bin/bash", "-c", "{command}"]

    imagePullPolicy: Always

    volumeMounts:
     - name: cyborg-results
       mountPath: "/results"

    resources:
      limits:
        cpu: 1
        memory: {mem_limit_pod:d}Gi
      requests:
        cpu: 1
        memory: {mem_limit_pod:d}Gi
"""


def get_pod_id(*args):
    return '-'.join([strip_for_kubernetes_yaml(s) for s in args])


def strip_for_kubernetes_yaml(s):
    return s.replace('_', '').lower()


def make_cyborg_seeker_pod_file_content(event, challenge, pov, timeout_in_secs, mem_limit_pod):
    cmd_fmt = 'python /home/angr/cyborg-generator/kubernetes_seeker.py {event} {challenge} {pov} {timeout}'
    command = cmd_fmt.format(event=event, challenge=challenge, pov=pov,
                             timeout=timeout_in_secs)
    timeout_command = "timeout {} {}".format(timeout_in_secs + 600, command)

    return POD_BASE_FORMAT.format(pod_id=get_pod_id(CYBORG_JOB_SEEKER, event, challenge, pov),
                                  type=CYBORG_JOB_SEEKER,
                                  command=command,
                                  mem_limit_pod=mem_limit_pod)


def make_cyborg_seeder_pod_file_content(event, challenge, timeout_in_secs, mem_limit_pod, mem_limit_process):
    cmd_fmt = 'python /home/angr/cyborg-generator/kubernetes_seeder.py {event} {challenge} {timeout} {mem_limit}'
    command = cmd_fmt.format(event=event, challenge=challenge, timeout=timeout_in_secs, mem_limit=mem_limit_process)
    timeout_command = "timeout {} {}".format(timeout_in_secs + 600, command)

    return POD_BASE_FORMAT.format(pod_id=get_pod_id(CYBORG_JOB_SEEDER, event, challenge),
                                  type=CYBORG_JOB_SEEDER,
                                  command=command,
                                  mem_limit_pod=mem_limit_pod)
