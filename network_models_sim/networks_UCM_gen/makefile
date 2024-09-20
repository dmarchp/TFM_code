objects = UCM_writing.o mtfort90_without_main.o
dep_objects = mtfort90_without_main.o
mods = mtmod.mod
compiler=gfortran

main.x : $(objects)
	$(compiler) -o UCM_writing.x $(objects)

$(mods) : $(dep_objects)

mtfort90_without_main.o : mtfort90_without_main.f90
	$(compiler) -c mtfort90_without_main.f90

UCM_writing.o : UCM_writing.f90 $(mods)
	$(compiler) -c UCM_writing.f90

.PHONY: clean
clean :
	rm -f $(objects)
	rm -f $(mods)