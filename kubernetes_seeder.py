import glob
import random
import sys
import os

import functools
import psutil

import angr
import simuvex

from config import DESKTOP_BASE_DIR, KUBERNETES_BASE_DIR, get_results_dir
from kubernetes_explorer import KubernetesExplorer

results_dir = '/results'

base_dir = KUBERNETES_BASE_DIR

DEBUG = True if 'DEBUG_CYBORG' in os.environ else False
if DEBUG:
    results_dir = './results'
    base_dir = DESKTOP_BASE_DIR
    """
    import enaml
    from angrmanagement.data.instance import Instance
    from enaml.qt.qt_application import QtApplication

    with enaml.imports():
        from angrmanagement.ui.main import Main, initialize_instance
    app = QtApplication()

    def launch_gui():
        inst = Instance(proj=proj)
        initialize_instance(inst, {})
        inst.path_groups.add_path_group(pg)

        view = Main(inst=inst)
        view.show()

        app.start()
    """

    def debug():
        import IPython
        IPython.embed()

else:
    def debug():
        import IPython
        IPython.embed()

    def launch_gui():
        pass

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage: {} <event_name> <challenge_name> <timeout_in_secs> <prune_mem_limit_in_gb".format(sys.argv[0])
        sys.exit(1)

    event = sys.argv[1]
    challenge = sys.argv[2]
    timeout_in_seconds = int(sys.argv[3], base=0)
    mem_limit = int(sys.argv[4], base=0) * (1024 * 1024 * 1024)

    #import ipdb; ipdb.set_trace()

    bin_path = os.path.join(results_dir, 'bins', challenge)
    if not os.path.isfile(bin_path):
        print "SKIPPING {chall}!!! {bin_path} not found!".format(chall=challenge, bin_path=bin_path)
        sys.exit(0)

    previous_results = glob.glob(os.path.join(results_dir, challenge, 'automated_seeders', 'seeds_no_afl_{}.tar.gz'.format(challenge, timeout_in_seconds)))
    if len(previous_results) > 0:
        print "SKIPPING {chall}!!! previous results found: {prev}".format(chall=challenge,
                                                                          prev=previous_results)
        sys.exit(0)

    binary_path = os.path.join(get_results_dir(base_dir, event), challenge, 'bin', challenge)
    assert os.path.isfile(binary_path)

    proj = angr.Project(binary_path, auto_load_libs=False)

    remove_options = {simuvex.o.LAZY_SOLVES}
    remove_options |= {simuvex.o.SUPPORT_FLOATING_POINT}
    remove_options |= simuvex.o.refs

    add_options = simuvex.o.unicorn | {simuvex.o.CGC_NO_SYMBOLIC_RECEIVE_LENGTH}

    state = proj.factory.full_init_state(add_options=add_options, remove_options=remove_options)

    pg = proj.factory.path_group(state, hierarchy=False)

    #def reorder(pg, pl):
    #    return sorted(pl, key=lambda p: p.state.transition_tracker.local_transition_score_alternative, reverse=True)

    #afl_technique = angr.exploration_techniques.AFL2()
    #pg.use_technique(afl_technique)
    pg.use_technique(angr.exploration_techniques.Oppologist())

    try:
        cur_proc = psutil.Process(os.getpid())

        def should_prune(pg, process=None, mem_lim=None):
            mem = process.memory_info().rss
            sys.stdout.write("Currently used memory: {}\tMB =>".format(mem / (1024 * 1024)))
            sys.stdout.flush()
            return mem > mem_lim # we hit limit => prune

        def remaining_paths(pg, target_num_paths):
            num_result_paths = len(pg.active)
            if len(pg.active) > target_num_paths:
                num_result_paths /= 2
            return random.sample(pg.active, num_result_paths)

        out_schema = os.path.join(results_dir, challenge, 'automated_seeders', 'seeds_no_afl_{}_{}Gi'.format(timeout_in_seconds, mem_limit))
        explorer = KubernetesExplorer(pg, out_schema, timeout_in_seconds)
        explorer.run(is_excessive=functools.partial(should_prune, process=cur_proc, mem_lim=mem_limit),
                     get_live_paths=functools.partial(remaining_paths))

    except Exception as ex:
        print ex

