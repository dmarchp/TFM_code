import matplotlib.pyplot as plt
import pandas as pd
import argparse
from f0poly_sols_clean import f0_lambda_neq_0
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('l', type=float, help='interdependence (lambda)')
parser.add_argument('q2', type=int, help='site 2 quality')
parser.add_argument('x', type=float, help='factor between f1 and f2, f2 = x*f1')
args = parser.parse_args()

l, q2, x = args.l, args.q2, args.x

q1s = [1,2,3,4,5,6,7,8,9]
colors = plt.cm.cool(np.linspace(0,1,len(q1s)))

fig, ax = plt.subplots(figsize=(4.8,4.8)) # 
ax.set(xlabel=r'$\pi_1$', ylabel=r'$\pi_2$', xlim=(0,1), ylim=(0,1))
for i,q1 in enumerate(q1s):
    tline = pd.read_csv(f'res_files/Tline_asym_pis_q1_{q1}_q2_{q2}_l_{l}_f2_{int(x)}f1.csv')
    ax.plot(tline['pi1'], tline['pi2'], lw=0.8, color=colors[i], label=f'{q1}')
fig.legend(title=r'$q_1$', fontsize=8, loc=(0.2, 0.35))
ax.set_aspect(1.0)
fig.text(0.4, 0.96, rf'$\lambda = {l}, q_2 = {q2}$')
fig.tight_layout()
fig.savefig(f'Tlines_asym_l_{l}_q2_{q2}_f2_{int(x)}f1.png')
plt.close(fig)
