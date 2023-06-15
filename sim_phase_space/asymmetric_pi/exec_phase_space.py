from sys import argv
import subprocess
import os
import pandas as pd
from random import seed, randint
from tqdm import tqdm

# Aixo s'haura de revisar:
num_rea = 50
###

if len(argv)==1:
    #pi = float(input("Enter the site discovery probability (pi): "))
    q1 = int(input("Enter the quality for site 1: "))
    q2 = int(input("Enter the quality for site 2: "))
    l = float(input("Enter the interdependence: "))
    inSeed = int(input("Enter a seed: "))
    #model = str(input("Which model do you want to simulate? (List/Galla) "))
    ic = str(input("Which initial conditions? (no (uncomitted), pi, pi hard) (N/P/Phard) "))
    N = int(input("Number of bots: "))
elif len(argv)==7:
    #pi = float(argv[1])
    q1 = int(argv[1])
    q2 = int(argv[2])
    l = float(argv[3])
    inSeed = int(argv[4])
    #model = str(argv[5])
    #ic = str(argv[6])
    ic = str(argv[5])
    N = int(argv[6])
else:
    print("Input parameter error. Execute as *.py q1 q2 seed model ic l or as *.py")
    exit()
    
# working directory:
wd = os.getcwd()

# input to Fortran code route:
froute = "/home/david/Desktop/Uni_code/TFM_code/clean_version/"
froute2 = "../../clean_version/"
fin_file = 'input_template.txt'
fex_file = 'main.x'
f_file = 'main.f90'
subprocess.call(f"sed -i '30s/.*/q(:) = {q1} {q2}/' "+froute+fin_file, shell=True)
subprocess.call(f"sed -i '17s/.*/lambda = {l}/' "+froute+fin_file, shell=True)
subprocess.call(f"sed -i 's/^N_bots = .*/N_bots = {N}/' "+froute+fin_file, shell=True)
subprocess.call(f"sed -i 's/^bots_per_site = .*/bots_per_site = {N} 0 0/' "+froute+fin_file, shell=True)

# which model? change accordingly the fortran code
#if model in ["G", "Galla", "galla"]:
#    subprocess.call("sed -i '65s/.*/            call update_system_galla()/' "+froute+f_file, shell=True)
#    subprocess.call("sed -i '66s/.*/            !call update_system()/' "+froute+f_file, shell=True)
#    model = "Galla"
#elif model in ["L", "List", "list"]:
#    subprocess.call("sed -i '65s/.*/            !call update_system_galla()/' "+froute+f_file, shell=True)
#    subprocess.call("sed -i '66s/.*/            call update_system()/' "+froute+f_file, shell=True)
#    model = "List"
#else:
#    print("Incorrect model introduced, shuting down!")
#    exit()
model = "Galla"
    
# which initial condition?
if ic in ["N", "n", "uncomitted"]:
    ic = "N"
elif ic in ["P", "p", "pi"]:
    ic = "P"
elif ic in ["Phard", "phard", "p hard", "P hard", "Pi hard", "pi hard"]:
    ic = "Phard"
else:
    print("Incorrect initial condition, shuting down!")
    exit()
    
# change the initial condition in the simulation input file:
call = f"sed -i '34s/.*/random_bots_per_site = \"{ic}\"/' "+froute+fin_file
subprocess.call(call, shell=True)

# if both the fortran code and the initial condition are changed properly, compile the fortran code and carry on with the simulations
os.chdir(froute)
subprocess.call('make', shell=True)
os.chdir(wd)

seed(inSeed)
    
lstr = str(l)
lstr = lstr[2:]
if (l*100)%10 == 0:
    lstr = lstr+'0'

print("Simulating phase space (pi1, pi2) with the following parameters: ")
#print(f"Site 1,2 discovery probability: {pi}")
print(f"Site 1 quality: {q1}")
print(f"Site 2 quality: {q2}")
print(f"Interdependence: {l}")

# output file (phase space):
of_name = f'q1_{q1}_q2_{q2}_l_{lstr}_phase_space_{model}_ic_{ic}_Nbots_{N}.csv'
of_write = open(of_name, 'w')

df_phase_space = pd.DataFrame(columns=['pi1','pi2','f0','f1','f2','sdf0','sdf1','sdf2','Q','sdQ','m','sdm'])

for pi1_100 in tqdm(range(1,51,2)):
    pi1=pi1_100/100
    for pi2_100 in range(1,51,2):
        pi2=pi2_100/100
        # Set the discovery probabilities (pi1, pi2), in the input template for execution:
        subprocess.call(f"sed -i '27s/.*/pi(:) = {pi1} {pi2}/' "+froute+fin_file, shell=True)
        # Change to the Fortran code directory and execute
        os.chdir(froute)
        subprocess.call("./"+fex_file+f" {randint(0,100000000)} {num_rea}", shell=True)
        os.chdir(wd)
        # Get the average values from the execution:
        df = pd.read_csv(froute+'stationary_results.csv')
        df.insert(0,'pi2',pi2)
        df.insert(0,'pi1',pi1)
        df_phase_space = pd.concat([df_phase_space,df])

of_write.write(df_phase_space.to_csv(index=False))
of_write.close()

subprocess.call(f"mkdir -p results/lambda_{lstr}/", shell=True)
subprocess.call(f"mv {of_name} results/lambda_{lstr}/", shell=True)
