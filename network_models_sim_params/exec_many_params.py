from subprocess import call

def exec_stat_states(pis, qs, ls, dl, N, nw_model, nw_param, ic, max_time, Nrea):
    pichainExec = ','.join([str(pi) for pi in pis]) 
    qchainExec = ','.join([str(q) for q in qs])
    lschainExec = ','.join([str(l) for l in ls])
    simCall = f'python get_stat_states_nwk.py -pis {pichainExec} -qs {qchainExec} -ls {lschainExec}'
    simCall += f' {dl} {N} {nw_model} {nw_param} {ic} {max_time} {Nrea}'
    call(simCall, shell=True)


execParams = [
    # [(0.1, 0.1), (7.0, 10.0), (0.3,0.9), 0.6, 500, 'ER', 0.02, 'N', 2000, 100],
    [(0.1, 0.1), (7.0, 10.0), (0.6,0.9), 0.3, 500, 'BA', 4, 'N', 2000, 100]

]

if __name__ == '__main__':
    for params in execParams:
        exec_stat_states(*params)