import os

EVENT_QUALIFIER = 'qualifiers'
EVENT_EXAMPLES = 'examples'
EVENT_FINALS = 'finals'
EVENTS = [EVENT_QUALIFIER, EVENT_EXAMPLES, EVENT_FINALS]

DESKTOP_BASE_DIR = os.path.dirname(__file__)
VAGRANT_BASE_DIR = os.path.join('/', 'vagrant')
KUBERNETES_BASE_DIR = os.path.join(os.path.expanduser('~'), 'cyborg-generator')


def get_results_dir(base, event):
    return os.path.join(base, 'bins', 'challenges_{}'.format(event))


def get_challenges_dir(base, event):
    return os.path.join(base, 'samples', 'challenges_{}'.format(event))
