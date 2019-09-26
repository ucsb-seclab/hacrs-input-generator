from config import *

for event in EVENTS:
    challenges_dir = get_challenges_dir(VAGRANT_BASE_DIR, event)
    if not os.path.isdir(challenges_dir):
        continue

    for challenge_name in os.listdir(challenges_dir):
        challenge_dir = os.path.join(challenges_dir, challenge_name)
        if not os.path.isdir(challenge_dir):
            continue

        os.chdir(challenge_dir)
        os.system('make clean && make')
