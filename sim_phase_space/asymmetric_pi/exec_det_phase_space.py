from sys import argv
import subprocess
import os
import pandas as pd
from tqdm import tqdm

if len(argv)==1:
    q1 = int(input("Enter the quality for site 1: "))
    q2 = int(input("Enter the quality for site 2: "))
    l = float(input("Enter the interdependence: "))
elif len(argv)==4:
    q1 = int(argv[1])
    q2 = int(argv[2])
    l = float(argv[3])
else:
    print("Input parameter error. Execute as *.py q1 q2 seed model ic l or as *.py")
    exit()
    
# working directory:
wd = os.getcwd()

# input to Fortran code route:
froute = "/home/david/Desktop/Uni_code/TFM_code/deterministic_solutions/"
froute2 = "../../deterministic_solutions/"
fin_file = 'input_template_f0.txt'
fex_file = 'main.x'
f_file = 'main_det.f90'
subprocess.call(f"sed -i '30s/.*/q(:) = {q1} {q2}/' "+froute+fin_file, shell=True)
subprocess.call(f"sed -i '17s/.*/lambda = {l}/' "+froute+fin_file, shell=True)
    
lstr = str(l)
lstr = lstr[2:]
if (l*100)%10 == 0:
    lstr = lstr+'0'

print("Simulating phase space (pi1, pi2) with the following parameters: ")
print(f"Site 1 quality: {q1}")
print(f"Site 2 quality: {q2}")
print(f"Interdependence: {l}")

# output file (phase space):
of_name = f'DET_q1_{q1}_q2_{q2}_l_{lstr}_phase_space.csv'
of_write = open(of_name, 'w')

df_phase_space = pd.DataFrame(columns=['pi1','pi2','f0','f1','f2','Q','Qs'])

for pi1_100 in tqdm(range(1,51,2)):
    pi1=pi1_100/100
    for pi2_100 in range(1,51,2):
        pi2=pi2_100/100
        # Set the discovery probabilities (pi1, pi2), in the input template for execution:
        subprocess.call(f"sed -i '27s/.*/pi(:) = {pi1} {pi2}/' "+froute+fin_file, shell=True)
        # Change to the Fortran code directory and execute
        os.chdir(froute)
        subprocess.call("./"+fex_file, shell=True)
        os.chdir(wd)
        # Get the average values from the execution:
        df = pd.read_csv(froute+'roots.csv')
        df.drop(columns='niter')
        df = df.iloc[[0]].copy(deep=True)
        df['Q'] = df['f2'] - 2*df['f1']
        df['Qs'] = df['f2'] - df['f1']
        df.insert(0,'pi2',pi2)
        df.insert(0,'pi1',pi1)
        df_phase_space = pd.concat([df_phase_space,df])

of_write.write(df_phase_space.to_csv(index=False))
of_write.close()

subprocess.call(f"mkdir -p results/lambda_{lstr}/", shell=True)
subprocess.call(f"mv {of_name} results/lambda_{lstr}/", shell=True)
