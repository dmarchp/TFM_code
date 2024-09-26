    program UCM_writing

	use mtmod
    implicit none
    character(20) :: seed_input, start_idx_input
    integer, parameter :: NN = 500, min_deg = 3
    double precision, parameter :: gam = 2.5d0
    integer deg(0:NN), place(0:NN + 1)
    integer, allocatable :: net(:)
    integer i, j, max_deg, k, seed, start_idx
    character(len=100) num, name
    character(5) :: minDeg_str, gamma_str, Nstr

    write(minDeg_str, "(I5)") min_deg
    write(gamma_str, "(F3.1)") gam
    write(Nstr, "(I5)") NN

    call get_command_argument(1, seed_input)
    call get_command_argument(2, start_idx_input)
    read(seed_input,*) seed
    read(start_idx_input,*) start_idx

    call sgrnd(seed + 1)


    ! Generació degrees
    if ((gam - 3.d0) .gt. (1.d-6)) then
        max_deg = min_deg*int(dble(NN)**(1.d0/(gam - 1.d0)))
    else
        max_deg = min_deg*int(dsqrt(dble(NN)))
    endif

    ! Main loop
    do k = start_idx,100

        call deg_SF(NN, gam, min_deg, max_deg, deg)
        ! deg = 5
        ! deg(0) = 0

        ! Construcció random network
        allocate(net(sum(deg)))
        call UCM(NN, sum(deg), deg, place, net)

        ! Network writing
        write(num,"(I3)") k
        name = "N"//trim(adjustl(Nstr))//"_g"//trim(adjustl(gamma_str))//"_min"//trim(adjustl(minDeg_str))//"_"//trim(adjustl(num))//".dat"
        open(10, file=name)
        do i = 1,NN
            do j = place(i), place(i + 1) - 1
                ! write(10,*) i, net(j)
                write(10,*) i-1, net(j)-1 ! David: mod to comply with my other programs...
            enddo
        enddo
        close(10)

        deallocate(net)

    enddo


    end program UCM_writing


    ! Vector amb degrees segons scale-free
    subroutine deg_SF(NN, gam, min_deg, max_deg, deg)
    use mtmod
    implicit none
    integer NN, min_deg, max_deg
    integer i, flag, deg(0:NN)
    double precision gam
        flag = 1
        do while (flag .eq. 1)
            i = 1
            deg = 0
            do while (i .le. NN)
                deg(i) = nint((min_deg - 0.5d0)*(grnd())**(1.d0/(1.d0 - gam)))
                if (deg(i) .le. max_deg) then
                    i = i + 1
                else
                    cycle
                endif
            enddo
            if (mod(sum(deg), 2) .eq. 0) flag = 0
        enddo
    return
    end subroutine deg_SF


    ! Connexions de la xarxa (UCM)
    subroutine UCM(NN, con, deg, place, net)
    use mtmod
    implicit none
    integer i, j, k, NN, con, con_inst, flag, cnt, con_lim
    integer deg(0:NN), place(0:NN + 1), net(con), node(con), ind(2), link(NN)
    ! integer(4) :: time_start, time_current
        ! Llista de nodes i veïnatge
        place = 1
        node = 0
        cnt = 1
        do i = 1,NN
            place(i) = place(i - 1) + deg(i - 1)
            do j = cnt, cnt + deg(i) - 1
                node(j) = i
            enddo
            cnt = cnt + deg(i)
        enddo
        place(NN + 1) = place(NN) + deg(NN)

        net = 0
        link = 0
        i = 0
        con_lim = int(real(con)/1.5)
        ! con_lim = con
        ! print*, con_lim
        ! read(*,*)
        con_inst = con
        cnt = 0
        flag = 0
        ! call cpu_time(time_start)
        ! print*, time_start
        do while (i .lt. con)
            ind(1) = mod(int(grnd()*con_inst), con_inst) + 1
            ind(2) = mod(int(grnd()*con_inst), con_inst) + 1
            ! Self-connections
            if (node(ind(1)) .eq. node(ind(2))) then
                cnt = cnt + 1
                if (cnt .gt. con_lim) then
                    flag = 2
                    ! exit
                    stop
                endif
                cycle
            endif
            ! Multi-connections
            do j = place(node(ind(1))), place(node(ind(1)) + 1) - 1
                if (net(j) .eq. node(ind(2))) flag = 1
            enddo
            ! Definim interacció
            if (flag .eq. 0) then
                net(place(node(ind(1))) + link(node(ind(1)))) = node(ind(2))
                net(place(node(ind(2))) + link(node(ind(2)))) = node(ind(1))
            else
                flag = 0
                cnt = cnt + 1
                cycle
            endif
            ! Actualitzem
            i = i + 2
            link(node(ind(:))) = link(node(ind(:))) + 1
            if (ind(1) .gt. ind(2)) then
                do j = 1,2
                    do k = ind(j) + 1, con_inst
                        node(k - 1) = node(k)
                    enddo
                    con_inst = con_inst - 1
                enddo
            else
                do j = 2,1,-1
                    do k = ind(j) + 1, con_inst
                        node(k - 1) = node(k)
                    enddo
                    con_inst = con_inst - 1
                enddo
            endif
            cnt = cnt + 1
            ! print*, cnt
            ! call cpu_time(time_current)
            ! if (cnt .gt. 3*con) then
            if (cnt .gt. con_lim) then
                flag = 2
                ! exit
                stop
            endif
            ! print*, (time_current)
            ! read(*,*)
            ! if (time_current-time_start.gt.5d0) then
            !     flag = 2
            !     exit
            !     print *, 'exitiiiing'
            ! endif
        enddo
    return
    end subroutine UCM
