import multiprocessing as mp
from subprocess import call

def exec_cost_function(qs, noiseType, noise, ci_kwargs, N, maxTime, Nrea, ic, ci_indep_q):
    qchainExec = ','.join([str(q) for q in qs])
    ci_kwargs_chainExec = ','.join([str(cikw) for cikw in ci_kwargs])
    ci_indep_q_exec = '--ci_indep_q' if ci_indep_q else ''
    simCall = f'python cost_function.py -qs {qchainExec} -noiseType {noiseType} -noise {noise} -ci_kwargs {ci_kwargs_chainExec} {ci_indep_q_exec}'
    simCall += f'-N {N} -maxTime {maxTime} -Nrea {Nrea} -ic {ic}'
    call(simCall, shell=True)
    return 1

def trial_func(qs, noiseType, noise, ci_kwargs, N, maxTime, Nrea, ic):
    qchainExec = ','.join([str(q) for q in qs])
    ci_kwargs_chainExec = ','.join([str(cikw) for cikw in ci_kwargs])
    simCall = f'python trial_exec.py -qs {qchainExec} -noiseType {noiseType} -noise {noise} -ci_kwargs {ci_kwargs_chainExec} '
    simCall += f'-N {N} -maxTime {maxTime} -Nrea {Nrea} -ic {ic}'
    call(simCall, shell=True)
    return 1

execParams = [
    [(1.0, 1.05), 1, 0.05, (1, 0.5, 10.0), 1000, 100.0, 100, 'N', False],
    [(1.0, 1.05), 1, 0.10, (1, 0.5, 10.0), 1000, 100.0, 100, 'N', False],
    [(1.0, 1.05), 1, 0.15, (1, 0.5, 10.0), 1000, 100.0, 100, 'N', False],
    [(1.0, 1.05), 1, 0.20, (1, 0.5, 10.0), 1000, 100.0, 100, 'N', False],
    [(1.0, 1.05), 1, 0.25, (1, 0.5, 10.0), 1000, 100.0, 100, 'N', False],
]

if __name__ == '__main__':
    pool = mp.Pool(int(mp.cpu_count()/2))
    res_async = [pool.apply_async(exec_cost_function, args = paramComb) for i,paramComb in enumerate(execParams)]
    res = [r.get() for r in res_async]
    # print(res)
