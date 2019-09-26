import glob
import os
import json
import dpkt
from os.path import join
from config import *


def extract_and_dump_pcap(dir, pcap_file_name):
    assert pcap_file_name.lower().endswith('.pcap')
    assert os.path.isfile(os.path.join(dir, pcap_file_name))

    pcap_path = os.path.join(dir, pcap_file_name)
    output_name_base = pcap_file_name[:-len('.pcap')]

    output_path_json_input = join(dir, output_name_base + '.input.json')
    output_path_json_output = join(dir, output_name_base + '.output.json')
    output_path_input = join(dir, output_name_base + '.input')
    output_path_stdout = join(dir, output_name_base + '.output')

    stdout = ''
    stdin = ''
    with open(pcap_path) as f:
        pcap = dpkt.pcap.Reader(f)

        for ts, buf in pcap:
            eth = dpkt.ethernet.Ethernet(buf)
            ip = eth.data
            tcp = ip.data

            # Hacky, are we the client?
            if ip.src == '\x7f\x00\x00\x01':
                stdin += tcp.data
            else:
                stdout += tcp.data
    try:
        #json_output = json.dumps(stdout.split('\n'))
        #json_input = json.dumps(stdin.split('\n'))

        #with open(output_path_json_input, 'w') as f:
        #    f.write(json_input)
        #with open(output_path_json_output, 'w') as f:
        #    f.write(json_output)
        with open(output_path_stdout, 'w') as f:
            f.write(stdout)
        with open(output_path_input, 'w') as f:
            f.write(stdin)
    except:
        # Avoid files with binary input or output, super hacky!
        pass


if __name__ == '__main__':
    base_dir = DESKTOP_BASE_DIR

    for event in EVENTS:
        results_dir = get_results_dir(DESKTOP_BASE_DIR, event)

        for challenge_name in os.listdir(results_dir):
            result_dir = join(results_dir, challenge_name)

            print "Parsing and dumping stdin and stdout from pov pcaps ..."
            pov_results_dir = join(result_dir, 'pov')
            for pov_pcap_path in glob.glob(join(pov_results_dir, '*.pcap')):
                print pov_pcap_path
                extract_and_dump_pcap(pov_results_dir, os.path.basename(pov_pcap_path))

            poller_results_dir = join(result_dir, 'poller')
            print "Parsing and dumping stdin and stdout from poller pcaps ..."
            for poller_pcap_path in glob.glob(join(poller_results_dir, '*.pcap')):
                print poller_pcap_path
                extract_and_dump_pcap(poller_results_dir, os.path.basename(poller_pcap_path))


