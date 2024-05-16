from subprocess import call

ci_kwargs = [0, ]
ci_kwargs_chainExec = ','.join([str(cikw) for cikw in ci_kwargs])

l, Nrea = 0.1, 900
call(f'python cost_function.py -pis 0.1,0.1 -qs 9.0,10.0 -lci 1.0 -N 1000 -ic N -maxTime 100.0 -Nrea {Nrea} -l {l} -ci_kwargs {ci_kwargs_chainExec}', shell=True)

l, Nrea = 0.2, 900
call(f'python cost_function.py -pis 0.1,0.1 -qs 9.0,10.0 -lci 1.0 -N 1000 -ic N -maxTime 100.0 -Nrea {Nrea} -l {l} -ci_kwargs {ci_kwargs_chainExec}', shell=True)

l, Nrea = 0.3, 900
call(f'python cost_function.py -pis 0.1,0.1 -qs 9.0,10.0 -lci 1.0 -N 1000 -ic N -maxTime 100.0 -Nrea {Nrea} -l {l} -ci_kwargs {ci_kwargs_chainExec}', shell=True)

l, Nrea = 0.45, 900
call(f'python cost_function.py -pis 0.1,0.1 -qs 9.0,10.0 -lci 1.0 -N 1000 -ic N -maxTime 100.0 -Nrea {Nrea} -l {l} -ci_kwargs {ci_kwargs_chainExec}', shell=True)

l, Nrea = 0.6, 900
call(f'python cost_function.py -pis 0.1,0.1 -qs 9.0,10.0 -lci 1.0 -N 1000 -ic N -maxTime 100.0 -Nrea {Nrea} -l {l} -ci_kwargs {ci_kwargs_chainExec}', shell=True)

l, Nrea = 0.75, 1000
call(f'python cost_function.py -pis 0.1,0.1 -qs 9.0,10.0 -lci 1.0 -N 1000 -ic N -maxTime 100.0 -Nrea {Nrea} -l {l} -ci_kwargs {ci_kwargs_chainExec}', shell=True)

l, Nrea = 0.9, 900
call(f'python cost_function.py -pis 0.1,0.1 -qs 9.0,10.0 -lci 1.0 -N 1000 -ic N -maxTime 100.0 -Nrea {Nrea} -l {l} -ci_kwargs {ci_kwargs_chainExec}', shell=True)