import re

import resource
import shellphish_qemu
import os
import glob
import subprocess
import json

import sys

from config import *

byte = 1
kilobyte = 1024 * byte
megabyte = 1024 * kilobyte
gigabyte = 1024 * megabyte

4
CHALLENGE_BLACKLIST = [ ('finals', 'KPRCA_00064', 'pov_0'),
                        ('finals', 'KPRCA_00064', 'pov_4'),
                        ('qualifiers', 'KPRCA_00034', 'pov_0'),
                        ('qualifiers', 'KPRCA_00034', 'pov_1'),
                        ('qualifiers', 'KPRCA_00038', 'pov_4'),
                        ('qualifiers', 'KPRCA_00044', 'pov_0'),
                        ('qualifiers', 'KPRCA_00047', 'pov_0'),
                        ('qualifiers', 'KPRCA_00047', 'pov_1'),
                       ]

qemu_path = shellphish_qemu.qemu_path('cgc-tracer')



base_dir = DESKTOP_BASE_DIR

for event in EVENTS:
    results_dir = get_results_dir(base_dir, event)

    challenges = os.listdir(results_dir)
    for i, challenge_name in enumerate(challenges):

        print "Progress: {}/{}".format(i, len(challenges))

        binary_path         = os.path.join(results_dir, challenge_name, 'bin', challenge_name)
        pov_results_dir_path = os.path.join(results_dir, challenge_name, 'pov')

        for pov_input_name in glob.glob(os.path.join(pov_results_dir_path, '*.input')):
            pov_name = os.path.basename(pov_input_name[:-len('.input')])

            if (event, challenge_name, pov_name) in CHALLENGE_BLACKLIST:
                print "Skipping {} - {} - {}, blacklisted".format(event, challenge_name, pov_name)
                continue
            # if os.path.isfile(os.path.join(pov_results_dir_path, '{}.crash_info'.format(pov_name))):
            #    print "Skipping {} - {} - {}, already present".format(event, challenge_name, pov_name)
            #    continue

            info_string = "{} - {} - {}: ".format(event, challenge_name, pov_name)
            sys.stdout.write(info_string)
            sys.stdout.flush()

            input_file_path = os.path.join(pov_results_dir_path, pov_input_name)
            out_crash_info_path = os.path.join(pov_results_dir_path, '{}.crash_info'.format(pov_name))


            args = 'cat {input} | {qemu} -d exec {binary} 2>&1 1>/dev/null | tail -n 10'.format(input=input_file_path, qemu=qemu_path, binary=binary_path)
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = p.communicate()
            info_string += "Exitcode {}, ".format(p.poll())
            sys.stdout.write(info_string)
            sys.stdout.flush()

            crash_trace_line = ''
            for line in reversed(stdout.split('\n')):
                if re.match(r'Trace 0x[0-9a-fA-F]* \[[0-9a-fA-F]*\]', line):
                    crash_trace_line = line
                    break

            print "Writing crash info to {}".format(out_crash_info_path)
            if len(stderr) > 0:
                print stderr

            with open(out_crash_info_path, 'w') as crash_file:
                crash_info = {
                    'command': args,
                    'exit_code': p.poll(),
                    'crash_trace': crash_trace_line
                }
                s = json.dumps(crash_info, indent=2)
                crash_file.write(s)


print 'DONE'
