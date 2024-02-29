from subprocess import call
import numpy as np

N = 10
q1s = np.around(np.arange(8.0, 8.7, 0.1), 1)

for q1 in q1s:
    callstr = f'python get_stat_states.py -pis 0.1,0.1 -qs {q1},10.0 -ls 0.6,0.6 0.1 {N} N 2000 500'
    print(callstr)
    call(callstr, shell=True)