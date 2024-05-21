import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    h = 1.0
    parser.add_argument('-qs', help='qs, separated by comas', type=lambda s: [float(item) for item in s.split(',')])
    parser.add_argument('-noiseType', help='1 or 2 (no zealotry for the moment)', type=int)
    parser.add_argument('-noise', help='Noise strength, float', type=float)
    parser.add_argument('-ci_kwargs', help='(cimode; ci_x0, ci_a)', type=lambda s: [float(item) for item in s.split(',')], default=[0, ])
    parser.add_argument('-N', type=int, help='Number of agents')
    parser.add_argument('-maxTime', type=float, help='simulation time')
    parser.add_argument('-Nrea', type=int, help='Number of realizations')
    parser.add_argument('-ic', type=str, help="Initial conditions. N for all uncomitted; E for equipartition bt sites; E for equipartition bt sites and uncomitted;")
    args = parser.parse_args()
    qs, noiseType, noise, ci_kwargs, N, maxTime, Nrea, ic = args.qs, args.noiseType, args.noise, args.ci_kwargs, args.N, args.maxTime, args.Nrea, args.ic
    ci_kwargs[0] = int(ci_kwargs[0])
    ci_kwargs_chain = '_'.join([str(cikw) for cikw in ci_kwargs])
    filename = f'file_{noise}_{ci_kwargs_chain}.txt'
    print('hola')
    with open(filename, 'w') as file:
        file.write(f'{qs}, {noiseType}, {noise}, {ci_kwargs}, {N}, {maxTime}, {Nrea}, {ic}')