module system_parameters
    ! To read from input constants
    integer :: N_bots, N_sites, max_time
    real(8) :: lambda, q0, lambda_ci
    ! To allocate & read from input arrays
    real(8), dimension(:), allocatable :: bots_per_site
    real(8), dimension(:), allocatable :: pi, q, r
    character(5) :: random_bots_per_site
    ! To allocate & init once inputs are known
    integer, dimension(:,:), allocatable :: system_state  ! (site, dance_time) for each bee
    real(8), dimension(:), allocatable :: pop_fraction, pop_fraction_k, pop_fraction_l0, pop_fraction_l1
      ! Probabilities and tower sampling variables:
    real(8), dimension(:), allocatable :: probs, tower_sample, probs_ci

    contains

    subroutine init_system_cts(input_unit)
      implicit none
      integer, intent(in) :: input_unit
      integer :: errstat
      namelist /input_cts/ N_bots, N_sites, max_time, lambda, q0, lambda_ci
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
        integer :: errstat,i
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
        allocate(probs(N_sites))
        allocate(probs_ci(N_sites))
        allocate(tower_sample(N_sites))
        ! Compute the population fractions at limits lambda 0 and lambda 1
        pop_fraction_l0 = fs_exact_l0()
        pop_fraction_l1 = fs_approx_l1()
        !print*, "exact at l0: ", pop_fraction_l0
        !print*, "approx at l1: ", pop_fraction_l1
        !if(pop_fraction_l1(0).eq.pop_fraction_l0(0)) then
        !    print*, "hola"
        !endif
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
      call compute_kparam(pop_fraction,pop_fraction_k)
    end subroutine init_system_state

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
        integer :: i, qmax_i, Nqmax_i
        integer, dimension(N_sites) :: qmax_i_vector
        real(8), dimension(0:N_sites) :: fs_approx_l1
        qmax_i_vector = 0
        qmax_i = maxloc(q, dim=1)
        qmax_i_vector(qmax_i) = 1
        ! check if there are other sites of the same quality
        if(qmax_i<N_sites) then
            do i=qmax_i+1,N_sites
                if(q(i).eq.q(qmax_i)) then
                    qmax_i_vector(i) = 1
                endif
            enddo
        endif
        Nqmax_i = sum(qmax_i_vector)
        !fs_approx_l1 = 0d0
        fs_approx_l1(0) = 1d0/q(qmax_i)
        do i=1,N_sites
            if(qmax_i_vector(i).eq.0) fs_approx_l1(i) = 0d0
            if(qmax_i_vector(i).eq.1) fs_approx_l1(i) = (1d0-1d0/q(qmax_i))/Nqmax_i
        enddo
        !fs_approx_l1(qmax_i) = 1d0-1d0/q(qmax_i)
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
