# For archival purposes only, not maintained

## HaCRS input generator

A component to produce baselines, seeds and other artifacts for the evaluation and seeding for the HaCRS system.

## Paper

The corresponding paper can be found here: https://acmccs.github.io/papers/p347-shoshitaishviliA.pdf

### Use

To make it work:

```
git clone hacrs-input-generator
cd hacrs-input-generator
```

First take a look at config.py and adjust it to your system. This should only 
require you to change DESKTOP_BASE_DIR to the directory where you cloned the repo.

Then run the Vagrant virtual machine.
```
vagrant up
vagrant ssh
```

Then inside the vagrant machine:

```
cd /vagrant
python 0_build_binaries.py
python onetime_fixup_challenges.py
python 1_extract_pcap.py
python 2_extract_interaction.py
python 3_extract_trace.py
```

This should generate all the important information in a subfolder `bins/` 
accessible on both the Vagrant machine and on your computer.

You can use the 5_info.py script to get information about each challenge and 
about which steps worked and also overall statistics.


TODO
1. Rework it to do all the povs as well as all the pollers.
2. Rework 4_copy_out_relevant_results.py or throw it out

