import pandas as pd

# VARIANT RI
df = pd.read_csv('Galla/35_bots/sim_fp_results_er_1.5.csv')
df.drop(['m','sdm','k0','k1','k2','sdk0','sdk1','sdk2'], axis=1, inplace=True)
df = df.loc[(df['pi1']==0.3) & (df['pi2']==0.3)]
df = df.reset_index(drop=True)
df.to_csv('quenched_res_varying_ri_N_35.csv', index=False)

# VARIANT N

Ns = [5, 10, 20, 30, 35, 40, 50, 60, 70, 80, 90]
df_out = pd.DataFrame(columns=['N','arena_r','interac_r','pi1','pi2','q1','q2','lambda','f0','f1','f2','sdf0','sdf1','sdf2','Q','sdQ'])
for N in Ns:
    df = pd.read_csv(f'Galla/{N}_bots/sim_fp_results_er_1.5.csv')
    df.drop(['m','sdm','k0','k1','k2','sdk0','sdk1','sdk2'], axis=1, inplace=True)
    df = df.reset_index(drop=True)
    df = df.loc[(df['pi1']==0.3) & (df['pi2']==0.3)].copy(deep=True)
    df.insert(0, 'N', N)
    df_out = pd.concat([df_out,df])
df_out.to_csv('quenched_res_varying_N_ri_7.0.csv', index=False)
