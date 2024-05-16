from subprocess import call

ci_kwargs = [2, 0.3, 500.0]
ci_kwargs_chainExec = ','.join([str(cikw) for cikw in ci_kwargs])

l, Nrea = 0.3, 500 # need to execute and analyze 500 more
call(f'python cost_function.py -pis 0.1,0.1 -qs 9.0,10.0 -lci 1.0 -N 1000 -ic N -maxTime 100.0 -Nrea {Nrea} -l {l} -ci_kwargs {ci_kwargs_chainExec}', shell=True)

l, Nrea = 0.45, 500 # only need to analyze 500 already executed
# call(f'python cost_function.py -pis 0.1,0.1 -qs 9.0,10.0 -lci 1.0 -N 1000 -ic N -maxTime 100.0 -Nrea {Nrea} -l {l} -ci_kwargs {ci_kwargs_chainExec}', shell=True)