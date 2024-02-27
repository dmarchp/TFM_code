from subprocess import Popen, PIPE, call
import numpy as np

pi = 0.05
Nsitess = [3,4,5,6,7,8,9,10]
qk = 10.0
qkmin1 = 9.0
dq = 1.0
# ls = np.arange(0.0, 1.0, 0.05)
ls_lims = [0.0, 0.95]
dl = 0.05
ic = 'N'

for Nsites in Nsitess:
    pis = [pi]*Nsites
    qs = [qkmin1-(Nsites-2-i)*dq for i in range(Nsites-1)]
    qs.append(qk)
    callstr = 'python get_det_sol_many_param.py '
    callstr += f"-pis {','.join([str(pi) for pi in pis])} -qs {','.join([str(q) for q in qs])} -ls {ls_lims[0]},{ls_lims[1]} {dl} {ic}"
    print(callstr)
    call(callstr, shell=True)

sumpi_const = 0.6
Nsitess = [6,7,8,9,10]
for Nsites in Nsitess:
    pis = [round(sumpi_const/Nsites,3)]*Nsites
    qs = [qkmin1-(Nsites-2-i)*dq for i in range(Nsites-1)]
    qs.append(qk)
    callstr = 'python get_det_sol_many_param.py '
    callstr += f"-pis {','.join([str(pi) for pi in pis])} -qs {','.join([str(q) for q in qs])} -ls {ls_lims[0]},{ls_lims[1]} {dl} {ic}"
    print(callstr)
    call(callstr, shell=True)