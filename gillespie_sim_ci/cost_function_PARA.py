import multiprocessing as mp
from subprocess import call

def exec_cost_function(pis, qs, l, lci, ci_kwargs, N, maxTime, Nrea, ic):
    pichainExec = ','.join([str(pi) for pi in pis]) 
    qchainExec = ','.join([str(q) for q in qs])
    ci_kwargs_chainExec = ','.join([str(cikw) for cikw in ci_kwargs])
    print(f'exec cost func {l}, {ci_kwargs}')
    simCall = f'python cost_function.py -pis {pichainExec} -qs {qchainExec} -l {l} -lci {lci} -ci_kwargs {ci_kwargs_chainExec} '
    simCall += f'-N {N} -maxTime {maxTime} -Nrea {Nrea} -ic {ic}'
    call(simCall, shell=True)
    return 1


execParams = [
    # [(0.2, 0.2), (9.0, 10.0), 0.1, 1.0, (2, 0.3, 500.0), 1000, 100.0, 100, 'N'],

    [(0.4, 0.4), (9.0, 10.0), 0.6, 1.0, (2, 0.3, 10.0), 1000, 100.0, 100, 'N'],
    [(0.4, 0.4), (9.0, 10.0), 0.6, 1.0, (1, 0.3, 500.0), 1000, 100.0, 100, 'N'],
    [(0.4, 0.4), (9.0, 10.0), 0.6, 1.0, (2, 0.3, 500.0), 1000, 100.0, 100, 'N'],

    
]

if __name__ == '__main__':
    pool = mp.Pool(int(mp.cpu_count()/2))
    res_async = [pool.apply_async(exec_cost_function, args = paramComb) for i,paramComb in enumerate(execParams)]
    res = [r.get() for r in res_async]