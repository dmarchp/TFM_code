
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
    character(5) :: file_id, config_file_id, Nstr, arstr, irstr, erstr
    character(15) :: push_folder_str
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
    open(unit=10, file="input_template_fp.txt")
    call init_system_cts(10)
    call init_system_arrays(10)
    call init_arena(10)
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
    write(Nstr, '(I5)') N_bots
    call radius_to_string(exclusion_r,erstr)
    call radius_to_string(interac_r,irstr)
    call radius_to_string(arena_r,arstr)
    !print*, push
    if(push.eqv..true.) then
        push_folder_str = "configs_w_push"
    else
        push_folder_str = "configs_wo_push"
    endif
    ! https://stackoverflow.com/questions/53447665/save-command-line-output-to-variable-in-fortran
    inquire(exist=foo_exists, file='foo')
    if (.not. foo_exists) then
        call execute_command_line ("mkfifo foo")
    end if
    call execute_command_line ("ls positions_and_contacts/"//trim(adjustl(Nstr))//"_bots/"//trim(adjustl(push_folder_str))//"/"&
    //"bots_xy_positions_*_ar_"//trim(adjustl(arstr))//"_er_"//trim(adjustl(erstr))//".txt | wc -l > foo&")
    open(100, file='foo', action='read')
    read(100, *) stored_configurations
    close(100)
    !write(*, *) 'Managed to read the value ', stored_configurations
    allocate(used_configurations(N_rea))
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
        !write(file_id, '(i0)') i
        ! integer to string:
        write(file_id, '(I4.3)') i
        open(11, file="time_evo_rea_"//trim(adjustl(file_id))//".csv")
!        write(11,'(A13)') "iter,f0,f1,f2"
        write(11,'(A)') trim(header)
        call init_system_state()
        !call generate_frozen_positions(file_id)
        config_chosen = .false.
        do while(config_chosen.eqv..false.)
            config_int = nint(grnd()*(stored_configurations-1)+1)
            config_chosen = .true.
            do j=1,N_rea-1
                if(used_configurations(j).eq.config_int) config_chosen = .false.
            enddo
        enddo
        used_configurations(i) = config_int
        !print*, config_int
        write(config_file_id, '(I4.3)') config_int
        call read_frozen_positions(Nstr,push_folder_str,arstr,erstr,config_file_id)
        call get_contact_list(arstr,erstr,irstr,config_file_id)
        !call write_bot_degrees(config_file_id) ! em serveix per fer histogrames sense haver de tornar a llegir la contact list amb un .py
        call compute_probs()
        j=0
        !write(11,'(I7,3(",",F14.10))') j,pop_fraction(:)
        call compute_kparam(pop_fraction,pop_fraction_k)
        write(11,format_traj) j,pop_fraction(:),pop_fraction_k(:)
        do j=1,max_time
            call update_system_galla()
            !call update_system()
            call compute_kparam(pop_fraction,pop_fraction_k)
            write(11,format_traj) j,pop_fraction(:),pop_fraction_k(:)
        enddo
        close(11)
        deallocate(neighbors)
    enddo
    !close(111)
    !close(112)
    ! END SIMULATE DIFFERENT TRAJECTORIES ***************************

    ! group output files in a folder
    call execute_command_line('mkdir -p time_evo_csv')
    call execute_command_line('mv time_evo_rea_*.csv time_evo_csv/')
    
 ! triem aixo enrere que fa pal truncar linies   
 call execute_command_line('mkdir -p positions_and_contacts/'//trim(adjustl(Nstr))//'_bots/'//trim(adjustl(push_folder_str))//'/')
 call execute_command_line('mv contact_list_*.txt positions_and_contacts/'//trim(adjustl(Nstr))//'_bots/'//&
 trim(adjustl(push_folder_str))//'/')
 !call execute_command_line('mv bot_degree_*.csv positions_and_contacts/'//trim(adjustl(Nstr))//'_bots/')
    
    ! get the stationary results before creating the compressed file:
    call execute_command_line("python stationary_results.py F")
    
    ! compress output folder:
    ! tar.gz, add -v for verbose
    call execute_command_line('tar -czf time_evo_csv.tar.gz time_evo_csv')
    ! uncompress with 'tar -xzvf time_evo.tar.gz'
    !call execute_command_line('tar -czf positions_and_contacts.tar.gz positions_and_contacts')

    ! zip
    ! call execute_command_line('zip -r time_evo_csv.zip time_evo_csv')
    ! uncompress with 'unzip time_evo_csv.zip'

    ! delete the folder:
    call execute_command_line('rm -r time_evo_csv')
    !call execute_command_line('rm -r positions_and_contacts')
    call execute_command_line('rm foo')

end program

    subroutine radius_to_string(radius,radstr)
        real(8), intent(in) :: radius
        character(5), intent(inout) :: radstr
        select case(floor(radius))
            case( : 9)
                write(radstr, '(F3.1)') radius
            case(10 : 99)
                write(radstr, '(F4.1)') radius
            case(100: 999)
                write(radstr, '(F5.1)') radius
        end select
    end subroutine radius_to_string
