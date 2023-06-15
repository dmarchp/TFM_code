from sys import argv
import subprocess
import os
import pandas as pd
from random import seed, randint
from tqdm import tqdm

num_rea = 50

if len(argv)==1:
    #pi = float(input("Enter the site discovery probability (pi): "))
    q1 = int(input("Enter the quality for site 1: "))
    q2 = int(input("Enter the quality for site 2: "))
    inSeed = int(input("Enter a seed: "))
    #model = str(input("Which model do you want to simulate? (List/Galla) "))
    ic = str(input("Which initial conditions? (no (uncomitted), pi, pi hard) (N/P/Phard) "))
    N = int(input("Number of bots to simulate: "))
elif len(argv)==6:
    #pi = float(argv[1])
    q1 = int(argv[1])
    q2 = int(argv[2])
    inSeed = int(argv[3])
    #model = str(argv[4])
    #ic = str(argv[5])
    #N = int(argv[6])
    ic = str(argv[4])
    N = int(argv[5])
else:
    print("Input parameter error. Execute as *.py q1 q2 seed model ic or as *.py")
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
# Naaaa, simulate always galla
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

print("Simulating phase space with the following parameters: ")
#print(f"Site 1,2 discovery probability: {pi}")
print(f"Site 1 quality: {q1}")
print(f"Site 2 quality: {q2}")
print(f"Model: {model}")
print(f"Initial conditions: {ic}")

# output file (phase space):
of_name = f'q1_{q1}_q2_{q2}_phase_space_{model}_ic_{ic}_Nbots_{N}.csv'
of_write = open(of_name, 'w')

df_phase_space = pd.DataFrame(columns=['pi','lambda','f0','f1','f2','sdf0','sdf1','sdf2','Q','sdQ','m','sdm','k2','sdk2'])


for p100 in tqdm(range(5,55,5)):
#for p100 in range(1,51):
    pi=p100/100
    for l100 in range(5,100,5):
        l=l100/100
        # Set the discovery probability (pi), interdependence (lambda) in the input template for execution:
        subprocess.call("sed -i '17s/.*/lambda = "+str(l)+"/' "+froute+fin_file, shell=True)
        subprocess.call(f"sed -i '27s/.*/pi(:) = {pi} {pi}/' "+froute+fin_file, shell=True)
        # Change to the Fortran code directory and execute
        os.chdir(froute)
        subprocess.call("./"+fex_file+f" {randint(0,100000000)} {num_rea}", shell=True)
        os.chdir(wd)
        # Get the average values from the execution:
        df = pd.read_csv(froute+'stationary_results.csv')
        df.insert(0,'lambda',l)
        df.insert(0,'pi',pi)
        df_phase_space = pd.concat([df_phase_space,df])

of_write.write(df_phase_space.to_csv(index=False))
of_write.close()

subprocess.call(f"mkdir -p results/", shell=True)
subprocess.call(f"mv {of_name} results/", shell=True)

