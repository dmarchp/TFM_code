
program main
    use system_parameters
    use mtmod
    use SSA
    implicit none
    character(20) :: seed_input, N_rea_input
    integer :: seed, N_rea, stored_configurations, configuration
    integer, dimension(:), allocatable :: used_configurations
    integer :: i, j, config_int
    logical :: config_chosen, foo_exists
    character(5) :: file_id, config_file_id, Nstr
    character(15) :: push_folder_str
    !character(39) :: path
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
    ! Initialize random numbers
    call sgrnd(seed)
    ! Initialize system variables from input file:
    open(unit=10, file="input_template_nwk.txt")
    call init_system_cts(10)
    call init_system_arrays(10)
    call init_network(10)
    close(10)
    ! header for csv files:
    open(10, file="header_aux.txt")
    write(10,fmt='(A)',advance="no") "iter"
    do i=0,N_sites
        write(auxi,'(I2)') i
        write(10,fmt='(A)',advance="no") ",f"//trim(adjustl(auxi))
    enddo
    rewind(10)
    read(10,fmt="(A)") header
    close(10)
    call execute_command_line('rm header_aux.txt')
    ! format for the output trajectories:
    ! https://stackoverflow.com/questions/53447665/save-command-line-output-to-variable-in-fortran
    write(auxi, '(I2)') 2*(N_sites+1)
    format_traj = "(I7,"//trim(adjustl(auxi))//'(",",F16.10))'
    write(Nstr, '(I5)') N_bots
    inquire(exist=foo_exists, file='foo')
    if (.not. foo_exists) then
        call execute_command_line ("mkfifo foo")
    end if
    !path = 'positions_and_contacts/'
    !path = '/media/david/KINGSTON/quenched_configs/'
    ! call init_path()
    ! call execute_command_line ("ls "//trim(adjustl(path))//trim(adjustl(Nstr))//"_bots/"//trim(adjustl(push_folder_str))//"/"&
    ! //"bots_xy_positions_*_ar_"//trim(adjustl(arstr))//"_er_"//trim(adjustl(erstr))//".txt | wc -l > foo&")
    ! open(100, file='foo', action='read')
    ! read(100, *) stored_configurations
    ! close(100)
    !write(*, *) 'Managed to read the value ', stored_configurations
    ! allocate(used_configurations(N_rea))
    ! END INITIALIZATION ********************************************
    
    ! una petita comprovacio
    !print*, push_folder_str
    !call execute_command_line("touch prova.txt")
    !call execute_command_line("cat positions_and_contacts/"//trim(adjustl(Nstr))//'_bots/'//trim(adjustl(push_folder_str))//&
    !    '/bots_xy_positions_001_ar_'//trim(adjustl(arstr))//'_er_'//trim(adjustl(erstr))//'.txt > prova.txt')
    !read(*,*)


    ! SIMULATE DIFFERENT TRAJECTORIES *******************************
       ! files for checking the duration of dance times when using galla update
    !open(111, file='durations_site_1.dat')
    !open(112, file='durations_site_2.dat')
    do i=1,N_rea
        ! integer to string:
        write(file_id, '(I4.3)') i
        open(11, file="time_evo_rea_"//trim(adjustl(file_id))//".csv")
        write(11,'(A)') trim(header)
        call init_system_state()
        ! config_chosen = .false.
        ! do while(config_chosen.eqv..false.)
        !     config_int = nint(grnd()*(stored_configurations-1)+1)
        !     config_chosen = .true.
        !     do j=1,N_rea-1
        !         if(used_configurations(j).eq.config_int) config_chosen = .false.
        !     enddo
        ! enddo
        ! used_configurations(i) = config_int
        config_int = i
        write(config_file_id, '(I4.3)') config_int
        open(12, file="time_evo_rea_"//trim(adjustl(file_id))//"_config_"//trim(adjustl(config_file_id))//"_indv_states.csv")
        call generate_network()
        call get_contact_list()
        call compute_probs()
        j=0
        write(11,format_traj) j,pop_fraction(:)
        call output_individual_state(12,j)
        do j=1,max_time
            call update_system_galla()
            !call update_system()
            write(11,format_traj) j,pop_fraction(:)
            call output_individual_state(12,j)
        enddo
        close(11)
        deallocate(neighbors)
    enddo
    !close(111)
    !close(112)
    ! END SIMULATE DIFFERENT TRAJECTORIES ***************************

    ! group output files in a folder
    call execute_command_line('mkdir -p time_evo_indv_states')
    call execute_command_line('mv time_evo_rea_*_indv_states.csv time_evo_indv_states/')
    call execute_command_line('mkdir -p time_evo_csv')
    call execute_command_line('mv time_evo_rea_*.csv time_evo_csv/')

    
 ! tirem aixo enrere que fa pal truncar linies   
!  call execute_command_line('mkdir -p positions_and_contacts/'//trim(adjustl(Nstr))//'_bots/'//trim(adjustl(push_folder_str))//'/')
!  call execute_command_line('mv contact_list_*.txt positions_and_contacts/'//trim(adjustl(Nstr))//'_bots/'//&
!  trim(adjustl(push_folder_str))//'/')
 !call execute_command_line('mv bot_degree_*.csv positions_and_contacts/'//trim(adjustl(Nstr))//'_bots/')
    
    ! get the stationary results before creating the compressed file:
    call execute_command_line("python stationary_results.py F")
    
    ! compress output folder:
    ! tar.gz, add -v for verbose
    call execute_command_line('tar -czf time_evo_csv.tar.gz time_evo_csv')
    call execute_command_line('tar -czf time_evo_indv_states.tar.gz time_evo_indv_states')
    ! uncompress with 'tar -xzvf time_evo.tar.gz'
    !call execute_command_line('tar -czf positions_and_contacts.tar.gz positions_and_contacts')

    ! zip
    ! call execute_command_line('zip -r time_evo_csv.zip time_evo_csv')
    ! uncompress with 'unzip time_evo_csv.zip'

    ! delete the folder:
    call execute_command_line('rm -r time_evo_csv')
    call execute_command_line('rm -r time_evo_indv_states')
    !call execute_command_line('rm -r positions_and_contacts')
    call execute_command_line('rm foo')

end program
