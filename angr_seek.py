import json
import re
import sys
import angr
import IPython
import os
import logging
import time
import simuvex

import select

from angr.exploration_techniques import ExecuteAddressGoal

from config import *

#base_dir = KUBERNETES_BASE_DIR
base_dir = DESKTOP_BASE_DIR

def heardEnter():
    i,o,e = select.select([sys.stdin],[],[], 0.0001)
    for s in i:
        if s == sys.stdin:
            input = sys.stdin.readline()
            return True
    return False

def read_crash_addr(crash_info_path):
    with open(crash_info_path) as f:
        crash_info = json.load(f)
        trace_line = crash_info['crash_trace']
        match = re.match(r'Trace 0x[0-9a-fA-F]* \[([0-9a-fA-F]*)\]', trace_line)
        addr_hex = match.group(1)
        crash_addr = int(addr_hex, base=16)
        return crash_addr

def replay_pov(event, challenge, pov_name):
    l = logging.getLogger(name="angr.analyses.cfg_accurate")
    #l.setLevel(logging.DEBUG)

    directory = os.path.join(get_results_dir(base_dir, event), challenge)
    assert os.path.isdir(directory)

    #crash_addr = read_crash_addr(os.path.join(directory, 'pov', pov_name + '.crash_info'))
    crash_addr = 0x080500ae

    proj = angr.Project(os.path.join(directory, 'bin', challenge), load_options={'auto_load_libs': False})

    state = proj.factory.full_init_state(add_options=simuvex.o.unicorn, remove_options={simuvex.o.LAZY_SOLVES})
    pg = proj.factory.path_group(state)

    execute_crash_addr_goal = ExecuteAddressGoal(crash_addr)
    director_explorer = angr.exploration_techniques.Director(goals=[execute_crash_addr_goal])
    pg.use_technique(director_explorer)

    while len(pg.active) > 0:

        print "step, {}".format({key: len(val) for key, val in pg.stashes.iteritems()})
        pg.step()

        reached_
        for stash in pg.stashes:
            for path in pg.stashes[stash]:
                if crash_addr in path.history._addr:
                    print "Path {} reached the target address".format(path)

        #if any([crash_addr in path.history._addr for path in pg.active] + [crash_add])
        if heardEnter() or len(c.crashes) != num_crashes:
            after_time = time.time()
            print "Finding a new crash took {} seconds".format(after_time - before_time)
            IPython.embed()
            before_time = time.time()
        num_crashes = len(c.crashes)

    after_time = time.time()
    print "Ran out of paths after {} seconds".format(after_time - before_time)
    IPython.embed()


if __name__ == '__main__':
    import sys
    import signal

    if len(sys.argv) < 4:
        print "Usage: {} <examples|finals|qualifiers> <challenge_name> <pov_name>".format(sys.argv[0])
        sys.exit(1)

    minute = 60
    hour = 60 * minute
    day = 24 * hour
    signal.alarm(10 * minute)
    
    replay_pov(sys.argv[1], sys.argv[2], sys.argv[3])
