module SSA
    use system_parameters
    contains

    subroutine compute_probs()
        implicit none
        integer i
        do i=1,N_sites
            probs(i) = (1d0-lambda)*pi(i) + lambda*pop_fraction(i)
        enddo
        do i=1,N_sites
            tower_sample(i) = sum(probs(1:i))
        enddo

        !print*, "Prob for site 1", probs(1)
        !print*, "Prob for site 2", probs(2)
        !print*, "Tower for site 1", tower_sample(1)
        !print*, "Tower for site 2", tower_sample(2)
        !read(*,*)
    end subroutine compute_probs


    subroutine update_system()
        ! List2009 update
        use mtmod
        implicit none
        integer i,j
        real(8) alea, alea2

        call compute_probs()
        do i=1,N_bots
            if(system_state(i,2).eq.0) then ! not dancing, random update
                alea = grnd()
                search: do j=1,N_sites
                    if(alea.lt.tower_sample(j)) then
                        system_state(i,1) = j
                        !system_state(i,2) = int(dble(q(j))/q0)
                        !if(system_state(i,2).ne.15) print*, system_state(i,2)
                        if(mod(dble(q(j)),q0).eq.0) then
                            system_state(i,2) = int(dble(q(j))/q0)
                        else
                            alea2 = grnd()
                            if(alea2.gt.0.5d0) then
                                system_state(i,2) = int(dble(q(j))/q0) + 1
                                !print*, system_state(i,2)
                            else
                                system_state(i,2) = int(dble(q(j))/q0)
                                !print*, system_state(i,2)
                            endif
                        endif
                        system_state(i,2) = nint(dble(q(j))/q0) ! pq tot lo anterior si fas aixo?
                        pop_fraction(0) = pop_fraction(0) - 1d0/dble(N_bots)
                        pop_fraction(j) = pop_fraction(j) + 1d0/dble(N_bots)
                        exit search
                    endif ! else, it will keep being uncomitted
                enddo search
            else ! it was dancing, decrease dance time
                system_state(i,2) = system_state(i,2) - 1
                if(system_state(i,2).eq.0) then
                    pop_fraction(system_state(i,1)) = pop_fraction(system_state(i,1)) - 1/dble(N_bots)
                    pop_fraction(0) = pop_fraction(0) + 1d0/dble(N_bots)
                    system_state(i,1) = 0 ! stop dance, become uncomitted
                endif
            endif
        enddo
        ! Check for error such as pop_frac = -3E-18
        do i=0,N_sites
            if(pop_fraction(i).lt.0d0) then
                pop_fraction(i) = 0d0
            endif
        enddo
    end subroutine update_system

    subroutine update_system_galla() !(unit1, unit2)
        ! Galla2010 update
        use mtmod
        implicit none
        !integer, intent(in) :: unit1, unit2
        integer i,j
        real(8) alea, rate

        call compute_probs()
        do i=1,N_bots
            if(system_state(i,2).eq.0) then ! not dancing, random update
                alea = grnd()
                search: do j=1,N_sites
                    if(alea.lt.tower_sample(j)) then
                        system_state(i,1) = j
                        system_state(i,2) = 1
                        pop_fraction(0) = pop_fraction(0) - 1d0/dble(N_bots)
                        pop_fraction(j) = pop_fraction(j) + 1d0/dble(N_bots)
                        exit search
                    endif ! else, it will keep being uncomitted
                enddo search
            else ! it was dancing, stocastically abandon dance (rate q0/q)
                rate = q0/dble(q(system_state(i,1)))
                if(grnd().lt.rate) then
                    !print*, 'abandoning dance for site', system_state(i,1)
                    !if(system_state(i,1).eq.1) write(unit1,*) system_state(i,2)
                    !if(system_state(i,1).eq.2) write(unit2,*) system_state(i,2)
                    system_state(i,2) = 0
                else
                    system_state(i,2) = system_state(i,2)+1
                endif
                if(system_state(i,2).eq.0) then
                    pop_fraction(system_state(i,1)) = pop_fraction(system_state(i,1)) - 1/dble(N_bots)
                    pop_fraction(0) = pop_fraction(0) + 1d0/dble(N_bots)
                    system_state(i,1) = 0 ! stop dance, become uncomitted
                endif
            endif
        enddo
        ! Check for error such as pop_frac = -3E-18
        do i=0,N_sites
            if(pop_fraction(i).lt.0d0) then
                pop_fraction(i) = 0d0
            endif
        enddo
    end subroutine update_system_galla

    real(8) function rayleigh(alea,sigma)
        implicit none
        real(8), intent(in) :: alea,sigma
        rayleigh = dsqrt(-2d0 * sigma**2 * log(1d0 - alea))
    end function rayleigh

end module SSA
