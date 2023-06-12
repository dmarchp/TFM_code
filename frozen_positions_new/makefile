objects = main_fp.o mt19937.o system_def_fp.o stoc_evo_fp.o
dep_objects = mt19937.o system_def_fp.o stoc_evo_fp.o
mods = mtmod.mod ssa.mod system_parameters.mod
compiler=gfortran
#opt= -ffpe-trap=invalid -g -O -Wall -fcheck=all -fbacktrace -fbounds-check
opt = -fbounds-check

main.x : $(objects)
	$(compiler) -o main.x $(opt) $(objects)

$(mods) : $(dep_objects)

mt19937.o : mt19937.f90
	$(compiler) -c $(opt) mt19937.f90
	
system_def_fp.o : system_def_fp.f90
	$(compiler) -c $(opt) system_def_fp.f90

stoc_evo_fp.o : stoc_evo_fp.f90 system_def_fp.o mt19937.o
	$(compiler) -c $(opt) stoc_evo_fp.f90

main_fp.o : main_fp.f90 $(mods)
	$(compiler) -c $(opt) main_fp.f90

.PHONY: clean
clean :
	rm -f $(objects)
	rm -f $(mods)
	
.PHONY: clean_res
clean_res:
	rm -f time_evo_csv.tar.gz
	rm -f positions_and_contacts.tar.gz
	rm -rf positions_and_contacts
	rm -rf time_evo_csv
	rm -f stationary_results.csv
