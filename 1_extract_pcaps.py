import shutil
import os

import subprocess

from config import *

max_num_povs = 10
max_num_poller_testcases = 10

exec_format = '/usr/bin/cb-test --port 10000 --cb {chall_name} --xml {input} --directory {bin_dir} --pcap {pcap}'

def find_next_numeric_file_name_index(dir, name_format_string):
    index = 0
    while os.path.isfile(os.path.join(dir, name_format_string.format(index))):
        index += 1
    return index

def find_next_numeric_dir_name_index(dir, name_format_string):
    index = 0
    while os.path.isdir(os.path.join(dir, name_format_string.format(index))):
        index += 1
    return index


def run_povs(challenge_source_dir, challenge_results_dir):
    challenge_results_pov_dir = os.path.join(challenge_results_dir, 'pov')
    os.mkdir(challenge_results_pov_dir)

    pov_files = os.listdir(os.path.join(challenge_source_dir, 'pov'))
    possible_povs = [p for p in pov_files if not p.endswith('.povxml')]


    list_of_weird_cases = []
    for i, pov_name in enumerate(possible_povs[:max_num_povs]):
        pov_file_path = os.path.join(challenge_source_dir, 'pov', pov_name)
        bin_dir_path = os.path.join(challenge_source_dir, 'bin')

        pcap_target_file_path = os.path.join(challenge_results_pov_dir, 'pov_{}.pcap'.format(i))

        exec_string = exec_format.format(chall_name=challenge_name, input=pov_file_path,
                                         bin_dir=bin_dir_path, pcap=pcap_target_file_path)
        # print exec_string

        process = subprocess.Popen(exec_string, shell=True, stdout=subprocess.PIPE)

        stdout, stderr = process.communicate()
        retval = process.poll()
        print "Event: {}, Challenge: {}, Exit code: {}".format(event, challenge_name, retval)
        if retval != 255:
            print "Did not exit with the expected exit code of 255, details:"
            print "Stdout: "
            print stdout
            print "Stderr: "
            print stderr
            print "$" * 60
            list_of_weird_cases.append((event, exec_string))
            continue

    return list_of_weird_cases


def run_poller_testcases(challenge_source_dir, challenge_results_dir):
    challenge_results_poller_dir = os.path.join(challenge_results_dir, 'poller')
    os.mkdir(challenge_results_poller_dir)

    list_of_weird_cases = []
    poller_source_dir = os.path.join(challenge_source_dir, 'poller')
    for poller_type in os.listdir(poller_source_dir):
        poller_type_source_dir = os.path.join(poller_source_dir, poller_type)
        poller_type_output_dir = os.path.join(challenge_results_dir, 'poller', )

        poller_input_files = os.listdir(poller_type_source_dir)
        possible_poller_input_files = [p for p in poller_input_files if p.lower().endswith('.xml')]
        for i, poller_input_name in enumerate(possible_poller_input_files[:max_num_poller_testcases]):

            input_file_path = os.path.join(poller_type_source_dir, poller_input_name)
            bin_dir_path = os.path.join(challenge_source_dir, 'bin')

            pcap_target_file_path = os.path.join(poller_type_output_dir, 'poller_{}.pcap'.format(i))

            exec_string = exec_format.format(chall_name=challenge_name, input=input_file_path,
                                             bin_dir=bin_dir_path, pcap=pcap_target_file_path)
            # print exec_string

            process = subprocess.Popen(exec_string, shell=True, stdout=subprocess.PIPE)

            stdout, stderr = process.communicate()
            retval = process.poll()
            print "Event: {}, Challenge: {}, Poller: {}-{}, Exit code: {}".format(event, challenge_name, poller_type, poller_input_name, retval)
            if retval != 0:
                print "Did not exit with the expected exit code of 0, details:"
                print "Stdout: "
                print stdout
                print "Stderr: "
                print stderr
                print "$" * 60
                list_of_weird_cases.append((event, exec_string))
                continue

    return list_of_weird_cases

base_dir = VAGRANT_BASE_DIR

list_of_weird_pov_cases = []
list_of_weird_poller_cases = []

for event in EVENTS:
    results_dir = get_results_dir(base_dir, event)
    challenges_dir = get_challenges_dir(base_dir, event)

    shutil.rmtree(results_dir, ignore_errors=True)
    os.makedirs(results_dir)

    for challenge_name in os.listdir(challenges_dir):
        challenge_source_dir = os.path.join(challenges_dir, challenge_name)
        if not os.path.isdir(challenge_source_dir):
            continue

        challenge_results_dir = os.path.join(results_dir, challenge_name)
        os.mkdir(challenge_results_dir)

        print "{} - {}: Running povs to produce pcaps ...".format(event, challenge_name)
        new_weird_pov_cases = run_povs(challenge_source_dir, challenge_results_dir)
        list_of_weird_pov_cases += new_weird_pov_cases
        if len(new_weird_pov_cases) > 0:
            # We have found a non-working pov binary, skip the rest, the results dir was deleted
            print "{}-{}: Removing results_dir [rm -rf {}], not working povs: {}".format(event, challenge_name, challenge_results_dir, list_of_weird_pov_cases)
            shutil.rmtree(challenge_results_dir)
            continue

        print "{} - {}: Running poller testcases to produce pcaps ...".format(event, challenge_name)
        list_of_weird_poller_cases += run_poller_testcases(challenge_source_dir, challenge_results_dir)

        # Store the binary directory for future reference
        shutil.copytree(os.path.join(challenge_source_dir, 'bin'), os.path.join(challenge_results_dir, 'bin'))

print
print "The following povs did not segfault?"
for elem in list_of_weird_pov_cases:
    print elem

print "The following poller testcases behaved weirdly."
for elem in list_of_weird_poller_cases:
    print elem