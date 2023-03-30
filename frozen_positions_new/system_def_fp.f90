module system_parameters
    ! To read from input constants
    integer :: N_bots, N_sites, max_time
    real(8) :: lambda, q0
    ! To allocate & read from input arrays
    integer, dimension(:), allocatable :: bots_per_site
    real(8), dimension(:), allocatable :: pi, q, r
    character(1) :: random_bots_per_site
    ! To allocate & init once inputs are known
    integer, dimension(:,:), allocatable :: system_state  ! (site, dance_time) for each bee
    real(8), dimension(:), allocatable :: pop_fraction, pop_fraction_k, pop_fraction_l0, pop_fraction_l1
      ! Probabilities and tower sampling variables:
    real(8), dimension(:,:), allocatable :: probs, tower_sample ! each bot has its probabilities to transition
    ! Bots physical positions:
    real(8) :: arena_r, arena_x, arena_y, interac_r, exclusion_r
    real(8), dimension(:,:), allocatable :: bots_xy
    integer, dimension(:), allocatable :: bot_degree, p_ini, p_fin, neighbors
    logical :: push
   

    contains

    subroutine init_system_cts(input_unit)
      implicit none
      integer, intent(in) :: input_unit
      integer :: errstat
      namelist /input_cts/ N_bots, N_sites, max_time, lambda, q0
      ! Read inputs:
      read(unit=input_unit, nml=input_cts, iostat=errstat)
      if (errstat > 0) then
          print *, "ERROR reading namelist cts from input file (code", errstat, ")"
          stop
      end if
    end subroutine init_system_cts
    
    subroutine init_system_arrays(input_unit)
        implicit none
        integer, intent(in) :: input_unit
        integer :: i,errstat
        namelist /input_arrays/ pi, q, random_bots_per_site, bots_per_site
        ! Allocate and read inputs:
        allocate(bots_per_site(0:N_sites))
        allocate(pi(N_sites))
        allocate(q(N_sites))
        allocate(r(N_sites))
        ! Read inputs:
        read(unit=input_unit, nml=input_arrays, iostat=errstat)
        if (errstat > 0) then
            print *, "ERROR reading namelist arr from input file (code", errstat, ")"
            stop
        end if
        do i=1,N_sites
          r(i) = q0/q(i)
        enddo
        ! Allocate other arrays: system_states, discovery prob, qualities
        allocate(system_state(N_bots,N_sites))
        allocate(pop_fraction(0:N_sites))
        allocate(pop_fraction_k(0:N_sites))
        allocate(pop_fraction_l0(0:N_sites))
        allocate(pop_fraction_l1(0:N_sites))
        allocate(probs(N_bots,N_sites))
        allocate(tower_sample(N_bots,N_sites))
        ! Compute the population fractions at limits lambda 0 and lambda 1
        pop_fraction_l0 = fs_exact_l0()
        pop_fraction_l1 = fs_approx_l1()
        !print*, pop_fraction_l0
        !print*, pop_fraction_l1
        !read(*,*)
    end subroutine init_system_arrays

    subroutine init_system_state()
      use mtmod
      implicit none
      integer i,j,bots_to_assign
      real(8) alea,tower
      ! For the moment, this subroutine is invoked to only to set all bots undecided
      !system_state = 0
      !pop_fraction(0) = 1d0
      !pop_fraction(1:2) = 0d0
      ! Assing the system state acording to what has been red in init_arrays:
      ! First, if uniform or total random, overwrite the input "bots_per_site":
      if(random_bots_per_site.eq.("U")) then
        bots_per_site = 0
        tower = 1d0/dble(N_sites+1)
        do i = 1,N_bots
          alea = grnd()
          do j = 0,N_sites
            if(alea.lt.(tower+j*tower)) then
              bots_per_site(j) = bots_per_site(j) + 1
              exit
            endif
          enddo
        enddo
        !print*, bots_per_site
      else if(random_bots_per_site.eq.("Y")) then
        bots_per_site(0) = nint(N_bots * grnd())
        do i = 1,N_sites-1
          bots_per_site(i) = nint((N_bots-sum(bots_per_site(0:i-1))) * grnd())
        enddo
        bots_per_site(N_sites) = N_bots - sum(bots_per_site(0:N_sites-1))
      else if(random_bots_per_site.eq.("P")) then
        bots_per_site = 0
        do i=1,N_bots
          alea = grnd()
          do j=1,N_sites
            if(alea.lt.sum(pi(1:j))) then
              bots_per_site(j) = bots_per_site(j) + 1
              exit
            else if(j.eq.(N_sites)) then
              bots_per_site(0) = bots_per_site(0) + 1
            endif
          enddo
        enddo
        !print*, bots_per_site(:)
      else if(random_bots_per_site.eq.('Phard')) then
        bots_per_site = 0
        do i=1,N_sites
          bots_per_site(i) = nint(N_bots*pi(i))
        enddo
        bots_per_site(0) = N_bots - sum(bots_per_site(1:N_sites))
        !print*, bots_per_site(:)
      endif
      ! Finally, make the initial state according to what is stored in "bots_per_site"
      j=1
      do i=0,N_sites
        bots_to_assign = bots_per_site(i)
        do while(bots_to_assign.gt.0)
          if(i.eq.0) then
            system_state(j,1) = 0
            system_state(j,2) = 0
          else if(i.gt.0) then
            system_state(j,1) = i
            system_state(j,2) = int(q(i))
          endif
          j = j + 1
          bots_to_assign = bots_to_assign - 1
        enddo
      enddo
      ! Finally, convert the values in pop fractions into actual fractions:
      pop_fraction = dble(bots_per_site)/dble(N_bots)
    end subroutine init_system_state
    
    
    subroutine init_arena(input_unit)
        implicit none
        integer, intent(in) :: input_unit
        integer :: errstat
        namelist /input_arena/ arena_r,arena_x,arena_y,interac_r,exclusion_r,push
        read(unit=input_unit, nml=input_arena, iostat=errstat)
        if (errstat > 0) then
            print *, "ERROR reading namelist arena from input file (code", errstat, ")"
            stop
        end if
    end subroutine init_arena
    
    subroutine generate_frozen_positions(file_id)
        use mtmod
        implicit none
        character(5), intent(in) :: file_id
        integer :: i
        real(8) :: pi, alpha, radius, x, y
        pi = 4d0*datan(1d0)
        if(allocated(bots_xy)) then
            continue
        else
            allocate(bots_xy(N_bots,2))
        endif
        open(100, file='bots_xy_positions_'//trim(adjustl(file_id))//'.txt')
        do i=1,N_bots
            alpha = 2d0*pi*grnd()
            radius = arena_r * dsqrt(grnd())
            x = radius * dcos(alpha) + arena_x
            y = radius * dsin(alpha) + arena_y
            bots_xy(i,:) = [x, y]
            write(100,*) i, x, y
        enddo
        close(100)
    end subroutine generate_frozen_positions
    
    subroutine read_frozen_positions(Nstr,push_folder_str,arstr,erstr,file_id)
        implicit none
        character(5), intent(in) :: file_id, Nstr, arstr, erstr
        character(15), intent(in) :: push_folder_str
        character(39) :: path
        integer :: i, read_stat
        real(8) :: x, y
        logical :: file_exists
        if(allocated(bots_xy)) then
            continue
        else
            allocate(bots_xy(N_bots,2))
        endif
        !path = 'positions_and_contacts/'
        path = '/media/david/KINGSTON/quenched_configs/'
        !inquire(file=trim(adjustl(path))//trim(adjustl(Nstr))//'_bots/'//trim(adjustl(push_folder_str))//&
        !'/bots_xy_positions_'//trim(adjustl(file_id))//'_ar_'//trim(adjustl(arstr))//'_er_'//trim(adjustl(erstr))//'.txt',&
        !exist=file_exists)
        !print*, file_exists
        !read(*,*)
        open(100, file=trim(adjustl(path))//trim(adjustl(Nstr))//'_bots/'//trim(adjustl(push_folder_str))//&
        '/bots_xy_positions_'//trim(adjustl(file_id))//'_ar_'//trim(adjustl(arstr))//'_er_'//trim(adjustl(erstr))//'.txt')
        do while(1.eq.1)
            read(100,*,iostat=read_stat) i, x, y
            if(IS_IOSTAT_END(read_stat))then
                exit
            else
                bots_xy(i,:) = [x, y]
            endif
        enddo
        close(100)
    end subroutine read_frozen_positions

    subroutine get_contact_list(arstr,erstr,irstr,file_id)
        implicit none
        character(5), intent(in) :: file_id, arstr, erstr, irstr
        integer :: i, j, sum_degree, read_stat
        real(8) :: dist
        if (allocated(bot_degree)) then
            continue
        else
            allocate(bot_degree(N_bots))
        endif
        open(100, file="contact_list_"//trim(adjustl(file_id))//"_ar_"//trim(adjustl(arstr))//"_er_"//trim(adjustl(erstr))//&
        "_ir_"//trim(adjustl(irstr))//".txt")
        ! get the degree of each bot based on the distance
        bot_degree = 0
        do i=1,N_bots-1
            do j=i+1,N_bots
                dist = sqrt((bots_xy(i,1)-bots_xy(j,1))**2+(bots_xy(i,2)-bots_xy(j,2))**2)
                if(dist.le.interac_r) then
                    bot_degree(i) = bot_degree(i) + 1
                    bot_degree(j) = bot_degree(j) + 1
                    write(100,*) i, j
                endif
            enddo
        enddo
        sum_degree = sum(bot_degree)
        ! get the initial position of the contact list (neighbors) for each bot, based on its degree
        if(allocated(p_ini)) then
            continue
        else
            allocate(p_ini(N_bots))
            allocate(p_fin(N_bots))
        endif
        allocate(neighbors(sum_degree)) ! neighbors has to be reallocated at each sim, as sum_degree may change from one another
        p_ini(1) = 1
        do i=2,N_bots
            p_ini(i) = bot_degree(i-1) + p_ini(i-1)
            p_fin(i-1) = p_ini(i-1) - 1
        enddo
        p_fin(N_bots) = p_ini(N_bots) - 1
        ! fill in the contact list for each bot, moving the final position each time a link is established:
        rewind(100)
        do while(1.eq.1)
            read(100,*,iostat=read_stat) i, j
            if(IS_IOSTAT_END(read_stat)) then
                exit
            else
                p_fin(i) = p_fin(i) + 1
                p_fin(j) = p_fin(j) + 1
                neighbors(p_fin(i)) = j
                neighbors(p_fin(j)) = i
            endif
        enddo
        close(100)
        !do i=1,N_bots
        !    print*, p_ini(i), p_fin(i)
        !    print*, neighbors(p_ini(i):p_fin(i))
        !    read(*,*)
        !enddo
    end subroutine get_contact_list
    

    subroutine get_contact_list_file(Nstr,arstr,erstr,irstr,file_id,push_folder_str)
    ! Looks if file already exists. If not, uses read_frozen_positions + get_contact_list to generate the the contact list.
    ! The idea is that position must have been generated previously to execution, but contacts may not.
        implicit none
        character(5), intent(in) :: file_id, Nstr, arstr, erstr, irstr
        character(15), intent(in) :: push_folder_str
        character(200) :: path1, filename, fullname
        logical :: file_exists
        path1 = 'media/david/KINGSTON/quenched_configs/'//trim(adjustl(Nstr))//'_bots/'//trim(adjustl(push_folder_str))//'/'
        filename = "contact_list_"//trim(adjustl(file_id))//"_ar_"//trim(adjustl(arstr))//"_er_"//trim(adjustl(erstr))//&
        "_ir_"//trim(adjustl(irstr))//".txt"
        fullname = trim(adjustl(path1))//trim(adjustl(filename))
        inquire(file=fullname, exist=file_exists)
        if (file_exists.eqv..true.) then
            ! read it and fill in the the neighbors, p_ini, p_fin vectors. S'ha de pensar bé com fer això, ja que no ser el degree de cada bot per preparar el p_ini...
        else
            ! read positions, generate contact list
        endif
    end subroutine
            
    
    subroutine write_bot_degrees(file_id)
        implicit none
        character(5), intent(in) :: file_id
        integer :: i
        open(100, file="bot_degree_"//trim(adjustl(file_id))//".csv")
        write(100,'(A)') 'bot_id,degree'
        do i=1,N_bots
            write(100,'(I3,",",I3)') i,bot_degree(i)
        enddo
        close(100)
    end subroutine write_bot_degrees

    real(8) function consensus()
      implicit none
      consensus = 1d0 - 2d0*pop_fraction(1)/pop_fraction(2)
    end function consensus

    real(8) function consensus2()
      ! Second definition of the consensus
      implicit none
      consensus2 = pop_fraction(2) - 2d0*pop_fraction(1)
    end function consensus2

    real(8) function consensus2_simple()
      ! Second definition of the consensus, but with simple majory
      consensus2_simple = pop_fraction(2) - pop_fraction(1)
    end function consensus2_simple
    
    function fs_exact_l0()
        implicit none
        integer :: i
        real(8), dimension(0:N_sites) :: fs_exact_l0
        real(8) :: lambda0
        lambda0 = 0d0
        fs_exact_l0(0) = 1d0/(1d0 + sum(pi*q))
        do i=1,N_sites
            fs_exact_l0(i) = (1d0 - lambda0)*pi(i)/((r(i)/fs_exact_l0(0))-lambda0)
        enddo
    end function fs_exact_l0
    
    function fs_approx_l1()
        implicit none
        integer :: qmax_i
        real(8), dimension(0:N_sites) :: fs_approx_l1
        qmax_i = maxloc(q, dim=1)
        fs_approx_l1 = 0d0
        fs_approx_l1(0) = 1d0/q(qmax_i)
        fs_approx_l1(qmax_i) = 1d0-1d0/q(qmax_i)
    end function fs_approx_l1
    
    subroutine compute_kparam(pop_fraction, pop_fraction_k)
        implicit none
        integer :: i
        real(8), dimension(0:N_sites) :: pop_fraction, pop_fraction_k
        do i=0,N_sites
            if(pop_fraction_l1(i).eq.pop_fraction_l0(i)) then
                pop_fraction_k(i) = 0d0
            else
                pop_fraction_k(i) = dabs((pop_fraction(i) - pop_fraction_l0(i))/(pop_fraction_l1(i) - pop_fraction_l0(i)))
            endif
        enddo
        !pop_fraction_k = dabs((pop_fraction - pop_fraction_l0)/(pop_fraction_l1 - pop_fraction_l0))
    end subroutine compute_kparam


end module system_parameters
