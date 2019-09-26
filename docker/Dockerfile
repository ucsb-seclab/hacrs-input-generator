# -*- mode: conf -*-
# Angr image for gitlab-ci-multi-runner
# Adapted to work with the Angr container by Francesco Disperati


# -*- mode: conf -*-
FROM zardus/research:cyborg
MAINTAINER Nobody

User root

RUN su - angr -c "source /etc/bash_completion.d/virtualenvwrapper && workon angr"

ARG CACHEBUST=

RUN su - angr -c "cd angr-dev && ./git_all.sh pull"
RUN su - angr -c "git clone --depth 1 git@git.seclab.cs.ucsb.edu:ldresel/cyborg-generator /home/angr/cyborg-generator"
RUN su - angr -c "git clone --depth 1 git@git.seclab.cs.ucsb.edu:ldresel/afl_exploration /home/angr/afl_exploration"

RUN su - angr -c "source /etc/bash_completion.d/virtualenvwrapper && workon angr && pip install -e /home/angr/afl_exploration"

WORKDIR /home/angr

# set up the angr user
USER angr
ENV HOME /home/angr
COPY bash_script /home/angr/.bash_script
ENV BASH_ENV /home/angr/.bash_script

RUN echo "workon angr" >> /home/angr/.bashrc

ENTRYPOINT []
CMD ["bash", "-i"]
