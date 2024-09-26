from datetime import datetime
import glob
import time
from subprocess import call

N, gamma, m = 500, 2.5, 3
files = glob.glob(f'N{N}_g{gamma}_min{m}_*.dat')
num_files = len(files)

def get_max_idx(files):
    if num_files > 0:
        idxs = [int(file.split('_')[3].replace('.dat', '')) for file in files]
        idxs = sorted(idxs)
        max_idx = idxs[-1]
    else:
        max_idx = 0
    return max_idx

max_idx = get_max_idx(files)
first_max_idx = max_idx
execCount = 1
print(f'maxIndex = {max_idx}, numFiles = {num_files}')
print(f'Generate {100-first_max_idx} files')
while(num_files < 100):
    timeStart = time.time()
    seed = int(datetime.now().timestamp())
    print(f'Initiate execution {execCount}')
    call(f'./UCM_writing.x {seed} {max_idx+1}', shell=True)
    files = glob.glob(f'N{N}_g{gamma}_min{m}_*.dat')
    num_files, max_idx = len(files), get_max_idx(files)
    execCount += 1