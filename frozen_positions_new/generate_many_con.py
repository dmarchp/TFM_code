from subprocess import call
import sys
sys.path.append('../')
from frozen_positions_network.filesHandling_quenched import availableIrs


N, arena_r = 709, 90.0
exclusion_r = 1.5

irs = availableIrs(N, arena_r, exclusion_r, push=False)

for ir in irs:
    call(f'python generate_contact_list.py {N} {arena_r} {ir} {exclusion_r} 0', shell=True)



