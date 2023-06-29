module SSA
    use system_parameters
    contains

    subroutine compute_probs()
        implicit none
        integer i,j,k,counter(N_sites)

        probs = 0d0
        do i=1,N_bots
            ! Go through contact list of bot i:
            counter = 0
            do j=p_ini(i),p_fin(i)
                do k=1,N_sites
                    if(system_state(neighbors(j),1).eq.k) then
                        !probs(i,k) = probs(i,k) + 1d0
                        counter(k) = counter(k) + 1
                    endif
                enddo
            enddo
            !probs(i,:) = probs(i,:)/dble(bot_degree(i))
            if(bot_degree(i).gt.0) then
                probs(i,:) = dble(counter(:))/dble(bot_degree(i))
            else
                probs(i,:) = 0d0
            endif
            probs(i,:) = probs(i,:)*lambda
            probs(i,:) = probs(i,:) + (1d0-lambda)*pi(:)
            do k=1,N_sites
                tower_sample(i,k) = sum(probs(i,1:k))
            enddo
        enddo

        !print*, "Prob for site 1", probs(1)
        !print*, "Prob for site 2", probs(2)
        !print*, "Tower for site 1", tower_sample(1)
        !print*, "Tower for site 2", tower_sample(2)
        !read(*,*)
    end subroutine compute_probs

    
    subroutine update_probs(comitUncomit, whichBot, whichSite)
        implicit none
        integer, intent(in) :: whichBot, whichSite
        character(1), intent(in) :: comitUncomit
        integer :: i,j
        
        select case(comitUncomit)
            case("C")
                do i=p_ini(whichBot),p_fin(whichBot)
                    probs(neighbors(i),whichSite) = probs(neighbors(i),whichSite) + lambda/dble(bot_degree(neighbors(i)))
                enddo
            case("U")
                do i=p_ini(whichBot),p_fin(whichBot)
                    probs(neighbors(i),whichSite) = probs(neighbors(i),whichSite) - lambda/dble(bot_degree(neighbors(i)))
                enddo
        end select
        do i=p_ini(whichBot),p_fin(whichBot)
            do j=1,N_sites
                tower_sample(neighbors(i),j) = sum(probs(neighbors(i),1:j))
            enddo
        enddo
    end subroutine update_probs


    subroutine update_system()
        ! List2009 update
        use mtmod
        implicit none
        integer i,j
        real(8) alea, alea2

        do i=1,N_bots
            if(system_state(i,2).eq.0) then ! not dancing, random update
                alea = grnd()
                search: do j=1,N_sites
                    if(alea.lt.tower_sample(i,j)) then
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
                        call update_probs("C",i,j)
                        exit search
                    endif ! else, it will keep being uncomitted
                enddo search
            else ! it was dancing, decrease dance time
                system_state(i,2) = system_state(i,2) - 1
                if(system_state(i,2).eq.0) then
                    pop_fraction(system_state(i,1)) = pop_fraction(system_state(i,1)) - 1/dble(N_bots)
                    pop_fraction(0) = pop_fraction(0) + 1d0/dble(N_bots)
                    call update_probs("U",i,system_state(i,1))
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
                !print*,probs(i,:)
                !print*,tower_sample(i,:)
                !read(*,*)
                alea = grnd()
                search: do j=1,N_sites
                    if(alea.lt.tower_sample(i,j)) then
                        system_state(i,1) = j
                        system_state(i,2) = 1
                        pop_fraction(0) = pop_fraction(0) - 1d0/dble(N_bots)
                        pop_fraction(j) = pop_fraction(j) + 1d0/dble(N_bots)
                        call update_probs("C",i,j)
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
                    call update_probs("U",i,system_state(i,1))
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

    subroutine output_individual_state(file_index,iter)
        implicit none
        integer :: i, file_index,iter
        character(2) :: auxi
        character(5) :: auxi2
        !write(file_index, '(A)', advance='no') trim(adjustl(auxi2))//','
        !write(auxi2, '(I5)') iter
        do i=1,N_bots-1
            write(auxi, '(I2)') system_state(i,1)
            write(file_index, '(A)', advance='no') trim(adjustl(auxi))//','
        enddo
        write(auxi, '(I2)') system_state(N_bots,1)
        write(file_index, '(A)') trim(adjustl(auxi))
    end subroutine output_individual_state

    real(8) function rayleigh(alea,sigma)
        implicit none
        real(8), intent(in) :: alea,sigma
        rayleigh = dsqrt(-2d0 * sigma**2 * log(1d0 - alea))
    end function rayleigh

end module SSA
