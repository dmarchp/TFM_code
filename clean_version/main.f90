
program main
    use system_parameters
    use mtmod
    use SSA
    implicit none
    character(20) :: seed_input, N_rea_input
    integer :: seed, N_rea
    integer :: i, j
    character(5) :: file_id
    character(2) :: auxi
    character(100) :: header, format_traj

    ! INITIALIZATION ************************************************
    ! Get seed, num realizations from input:
    ! First, make sure the right number of inputs have been provided:
    if(command_argument_count().ne.2) then
        write(*,*) "Execution error. Please execute as follows >> ./main.x SEED NUM_REALIZATIONS"
        stop
    endif
    ! Convert input into integer:
    call get_command_argument(1, seed_input)
    call get_command_argument(2, N_rea_input)
    read(seed_input,*) seed
    read(N_rea_input,*) N_rea
    ! Initialize random numbers: better do it inside de realizations loop, one seed for every realization
    ! call sgrnd(seed)
    ! Initialize system variables from input file:
    open(unit=10, file="input_template.txt")
    call init_system_cts(10)
    call init_system_arrays(10)
    close(10)
    ! header for csv files:
    open(10, file="header_aux.txt")
    write(10,fmt='(A)',advance="no") "iter"
    do i=0,N_sites
        write(auxi,'(I2)') i
        write(10,fmt='(A)',advance="no") ",f"//trim(adjustl(auxi))
    enddo
    do i=0,N_sites
        write(auxi,'(I2)') i
        write(10,fmt='(A)',advance="no") ",k"//trim(adjustl(auxi))
    enddo
    rewind(10)
    read(10,fmt="(A)") header
    close(10)
    call execute_command_line('rm header_aux.txt')
    ! format for the output trajectories:
    write(auxi, '(I2)') 2*(N_sites+1)
    format_traj = "(I7,"//trim(adjustl(auxi))//'(",",F16.10))'
    ! END INITIALIZATION ********************************************


    ! SIMULATE DIFFERENT TRAJECTORIES *******************************
       ! files for checking the duration of dance times when using galla update
    !open(111, file='durations_site_1.dat')
    !open(112, file='durations_site_2.dat')
    do i=1,N_rea
        call sgrnd(seed+(i-1))
        !write(file_id, '(i0)') i
        write(file_id, '(I4.3)') i
        open(11, file="time_evo_rea_"//trim(adjustl(file_id))//".csv")
        !write(11,'(A13)') "iter,f0,f1,f2"
        write(11,'(A)') trim(header)
        call init_system_state() !trim set the system to all uncomitted at every rea
        call compute_probs()
        call compute_kparam(pop_fraction,pop_fraction_k)
        j=0
        write(11,format_traj) j,pop_fraction(:),pop_fraction_k(:)
        do j=1,max_time
            call update_system_galla()
            !call update_system()
            call compute_kparam(pop_fraction,pop_fraction_k)
            write(11,format_traj) j,pop_fraction(:),pop_fraction_k(:)
        enddo
        close(11)
    enddo
    !close(111)
    !close(112)
    ! END SIMULATE DIFFERENT TRAJECTORIES ***************************

    ! group output files in a folder
    call execute_command_line('mkdir -p time_evo_csv')
    call execute_command_line('mv time_evo_rea_*.csv time_evo_csv/')
    
    ! get the stationary results before creating the compressed file:
    call execute_command_line('python stationary_results.py F')
    !call execute_command_line('python stationary_results_old.py F')
    
    ! compress output folder:
    ! tar.gz, add -v for verbose
    call execute_command_line('tar -czf time_evo_csv.tar.gz time_evo_csv')
    ! uncompress with 'tar -xzvf time_evo.tar.gz'

    ! zip
    ! call execute_command_line('zip -r time_evo_csv.zip time_evo_csv')
    ! uncompress with 'unzip time_evo_csv.zip'

    ! delete the folder:
    call execute_command_line('rm -r time_evo_csv')

end program
