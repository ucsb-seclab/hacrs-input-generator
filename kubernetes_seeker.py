import glob
import json
import re
import angr
import simuvex
import sys

from angr.exploration_techniques import ExecuteAddressGoal

from config import *

from config import KUBERNETES_BASE_DIR, get_results_dir
from kubernetes_explorer import KubernetesExplorer

base_dir = KUBERNETES_BASE_DIR

def read_crash_addr(crash_info_path):
    with open(crash_info_path) as f:
        crash_info = json.load(f)
        trace_line = crash_info['crash_trace']
        match = re.match(r'Trace 0x[0-9a-fA-F]* \[([0-9a-fA-F]*)\]', trace_line)
        addr_hex = match.group(1)
        crash_addr = int(addr_hex, base=16)
        return crash_addr

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print "Usage: {} <event_name> <challenge_name> <pov_name> <timeout_in_secs>".format(sys.argv[0])
        sys.exit(1)

    event = sys.argv[1]
    challenge = sys.argv[2]
    pov_name = sys.argv[3]
    timeout_in_seconds = int(sys.argv[4], base=0)

    if not os.path.isfile('/results/bins/{}'.format(challenge)):
        print "SKIPPING {chall}-{pov}!!! /results/bins/{chall} not found!".format(chall=challenge, pov=pov_name)
        sys.exit(0)

    previous_results = glob.glob('/results/{}/automated_seekers/seeds_{}.tar.gz'.format(challenge, pov_name))
    if len(previous_results) > 0:
        print "SKIPPING {chall}-{pov}!!! previous results found: {prev}".format(chall=challenge, pov=pov_name, prev=previous_results)
        sys.exit(0)

    directory = os.path.join(get_results_dir(base_dir, event), challenge)
    assert os.path.isdir(directory)

    crash_addr = read_crash_addr(os.path.join(directory, 'pov', pov_name + '.crash_info'))

    proj = angr.Project(os.path.join(directory, 'bin', challenge), load_options={'auto_load_libs': False})

    remove_options = {simuvex.o.LAZY_SOLVES}
    remove_options |= {simuvex.o.SUPPORT_FLOATING_POINT}
    remove_options |= simuvex.o.refs

    state = proj.factory.full_init_state(add_options=simuvex.o.unicorn, remove_options=remove_options)
    pg = proj.factory.path_group(state)

    execute_crash_addr_goal = ExecuteAddressGoal(crash_addr)
    director_explorer = angr.exploration_techniques.Director(goals=[execute_crash_addr_goal])
    pg.use_technique(director_explorer)
    pg.use_technique(angr.exploration_techniques.Oppologist())

    try:
        explorer = KubernetesExplorer(pg, '/results/{}/automated_seekers/seeds_{}'.format(challenge, pov_name), timeout_in_seconds)
        explorer.run()
        print "Trying to exit with exit code 0 ... "
        sys.exit(0)
    except Exception as ex:
        print ex
