objects = main.o mt19937.o system_def.o stoc_evo.o
dep_objects = mt19937.o system_def.o stoc_evo.o
mods = mtmod.mod ssa.mod system_parameters.mod
compiler=gfortran
#opt= -ffpe-trap=invalid -g -O -Wall -fcheck=all -fbacktrace -fbounds-check
opt = -fbounds-check

main.x : $(objects)
	$(compiler) -o main.x $(opt) $(objects)

$(mods) : $(dep_objects)

mt19937.o : mt19937.f90
	$(compiler) -c $(opt) mt19937.f90
	
system_def.o : system_def.f90
	$(compiler) -c $(opt) system_def.f90

stoc_evo.o : stoc_evo.f90 system_def.o mt19937.o
	$(compiler) -c $(opt) stoc_evo.f90

main.o : main.f90 $(mods)
	$(compiler) -c $(opt) main.f90

.PHONY: clean
clean :
	rm -f $(objects)
	rm -f $(mods)
	
.PHONY: clean_res
clean_res:
	rm -f time_evo_csv.tar.gz
	rm -rf time_evo_csv
	rm -f stationary_results.csv
