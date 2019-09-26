import glob
import os
import shutil


def run_cmd(cmd):
    print cmd
    os.system(cmd)

def make_salls_file(seed_glob, output_file_path_base):
    tmp_path = '/tmp/afl_sync/fuzzer-master/queue/'
    run_cmd('rm -rf {}'.format(tmp_path))
    run_cmd('mkdir -p {}'.format(tmp_path))
    for seed in glob.iglob(seed_glob):
        input_name = os.path.basename(seed)
        run_cmd('cp {} {}'.format(seed, tmp_path + 'id:' + input_name))

    shutil.make_archive(output_file_path_base, 'gztar', tmp_path, tmp_path)

binaries = []
for bin_path in glob.iglob('/results/bins/?????_?????'):
    binaries.append(os.path.basename(bin_path))

for binary in binaries:
    seed_glob = '/home/angr/cyborg-generator/bins/challenges_*/{}/poller/poller_*.input'.format(binary)
    output_path_base = '/results/{}/testcase_input_seeds'.format(binary)
    make_salls_file(seed_glob, output_path_base)


