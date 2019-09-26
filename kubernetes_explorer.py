import os
import random
import sys
import time

import shutil
import tempfile

import gc
from collections import defaultdict

import psutil


class TemporaryDirectory(object):
    """
    Context manager for tempfile.mkdtemp().

    This class is available in python +v3.2.

    """
    def __enter__(self):
        self.dir_name = tempfile.mkdtemp()
        return self.dir_name

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.dir_name)


TemporaryDirectory = getattr(tempfile, 'TemporaryDirectory',
                             TemporaryDirectory)

class KubernetesExplorer:
    def __init__(self, path_group, output_path_prefix, timeout_in_seconds):
        self.timeout_in_seconds = timeout_in_seconds
        self.pg = path_group
        self.output_path_prefix = output_path_prefix
        self.found_inputs_list = defaultdict(list)

    def dump(self, s):
        print s
        sys.stdout.flush()

    def dump_inputs(self):
        i = 0
        with TemporaryDirectory() as td:
            self.dump("Dumping results to {}".format(td))
            for stash in self.found_inputs_list:
                stash_results_dir = os.path.join(td, stash)
                self.dump('Dumping stash {} to ...'.format(stash, stash_results_dir))

                os.mkdir(stash_results_dir)
                for i, input_string in enumerate(self.found_inputs_list[stash]):
                    result_file_name = os.path.join(stash_results_dir, '{}.seed'.format(i))
                    self.dump('Dumping input {} to {} ...'.format(repr(input_string), result_file_name))
                    with open(result_file_name, 'w') as outf:
                        outf.write(input_string)

            file_suffix = '.tar.gz'
            with tempfile.NamedTemporaryFile(suffix=file_suffix, delete=False) as temp_out_file:
                self.dump("Compressing to {}".format(temp_out_file.name))
                shutil.make_archive(temp_out_file.name[:-len(file_suffix)], 'gztar', td, td)

                tar_out_file = self.output_path_prefix + file_suffix
                self.dump("Moving tar file from {} to {}".format(temp_out_file.name, tar_out_file))
                shutil.copy(temp_out_file.name, tar_out_file)

    def add_path_input(self, stash, path):
        try:
            input_text = path.state.posix.dumps(0)
            self.found_inputs_list[stash].append(input_text)
        except Exception as ex:
            self.dump("Exception occurred during output path dumping: " + str(ex))
            pass

    def run(self, is_excessive=lambda pg: len(pg.active) > 2000, get_live_paths=lambda pg: random.sample(pg.active, 200)):
        self.dump("Starting exploration with timeout of {} seconds ... ".format(self.timeout_in_seconds))
        before_time = time.time()
        i = 0

        target_num_paths = None
        while True:
            if len(self.pg.active) == 0:
                self.dump("[Worker] Ran out of active paths!")
                break

            if is_excessive(self.pg):
                if target_num_paths is None:
                    target_num_paths = max(len(self.pg.active) * 3 / 4, 1) # let's try to get it back to reasonable levels

                live_paths = get_live_paths(self.pg, target_num_paths)
                live_paths_set = set(live_paths)

                self.pg.stash(filter_func=lambda p: p not in live_paths_set, from_stash='active', to_stash='go_die')
                for p in self.pg.go_die:
                    self.add_path_input('excessive_pruned', p)

                new_stashes = {stash: list(self.pg.stashes[stash]) for stash in self.pg.stashes if stash != 'go_die'}
                self.pg._successor(new_stashes)

                gc.collect()

            else:
                # we seem to have gone back to normal level, let's go!
                target_num_paths = None


            time_diff = time.time() - before_time
            if time_diff > self.timeout_in_seconds:
                self.dump("[Worker] Job execution timeout!")
                break

            self.dump("Step {}: {} seconds elapsed, {} paths active".format(i, time_diff, len(self.pg.active)))
            self.pg.step()
            i += 1

        for stash, paths in self.pg.stashes.iteritems():
            for p in paths:
                self.add_path_input(stash, p)

        self.dump("COMPLETE, finished in {} seconds".format(time.time() - before_time))
        before_time = time.time()
        self.dump("Dumping explored inputs ... ")
        self.dump_inputs()
        self.dump("DONE!!!!! Dumping explored inputs took {} seconds.".format(time.time() - before_time))







