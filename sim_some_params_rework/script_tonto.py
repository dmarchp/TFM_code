from subprocess import call
import numpy as np

l = 0.6
N = 1000
q2 = 20.0
Nrea = 500
simTime = 3000

# q1s = np.around(np.arange(35.8, 36.3, 0.1), 1)

q1s = np.around(np.arange(18.21, 18.25, 0.01), 2)

for q1 in q1s:
    callstr = f'python get_stat_states.py -pis 0.1,0.1 -qs {q1},{q2} -ls {l},{l} 0.1 {N} N {simTime} {Nrea}'
    print(callstr)
    call(callstr, shell=True)


# more things to do:
# l, Nrea = 0.6, 500
# Ns = [100, 500]
# # q2s = [20.0, 30.0, 40.0]
# q2_q1s = {20.0:np.around(np.arange(17.8,18.5,0.1), 1), 30.0:np.around(np.arange(27.0,27.7,0.1), 1), 40.0:np.around(np.arange(35.8,36.6,0.1), 1) }
# for N in Ns:
#     for q2,q1s in q2_q1s.items():
#         for q1 in q1s:
#             callstr = f'python get_stat_states.py -pis 0.1,0.1 -qs {q1},{q2} -ls {l},{l} 0.1 {N} N 3000 {Nrea}'
#             call(callstr, shell=True)