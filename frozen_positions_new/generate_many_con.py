from subprocess import call
import sys
sys.path.append('../')
from frozen_positions_network.filesHandling_quenched import availableIrs


N, arena_r = 2240, 160.0
exclusion_r = 1.5

# irs = availableIrs(N, arena_r, exclusion_r, push=False)

irs = [6.7, 6.8, 6.9, 7.0]
for ir in irs:
    call(f'python generate_contact_list.py {N} {arena_r} {ir} {exclusion_r} 0', shell=True)



