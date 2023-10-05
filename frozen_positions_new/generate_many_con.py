from subprocess import call
import sys
sys.path.append('../')
from frozen_positions_network.filesHandling_quenched import availableIrs


N, arena_r = 95, 20.0
exclusion_r = 1.5

# irs = availableIrs(N, arena_r, exclusion_r, push=False)

irs = [3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.6, 3.7, 3.8, 3.9, 4.0]
for ir in irs:
    call(f'python generate_contact_list.py {N} {arena_r} {ir} {exclusion_r} 1', shell=True)



