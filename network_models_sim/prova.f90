module prova
    implicit none
    integer N_bots,i,file_index
    integer, dimension(:), allocatable :: bot_degree, p_ini, p_fin, neighbors

    ! allocate(bot_degree(N_bots))
    ! allocate(p_ini(N_bots))
    ! allocate(p_fin(N_bots))

    ! file_index = 100
    ! open(unit=file_index, file='nwk_ks.txt')
    ! do i=1,N_bots
    !     read(100,*) bot_degree(i)
    !     print*, i, bot_degree(i)
    ! enddo
    ! print*, sum(bot_degree)
    
    contains
    
    subroutine get_contact_list()
        implicit none
        ! character(5), intent(in) :: file_id
        integer :: i, j, sum_degree, read_stat
        if (allocated(bot_degree)) then
            continue
        else
            allocate(bot_degree(N_bots))
        endif
        !open(100, file="contact_list_"//trim(adjustl(file_id))//"_ar_"//trim(adjustl(arstr))//"_er_"//trim(adjustl(erstr))//&
        !"_ir_"//trim(adjustl(irstr))//".txt")
        open(100, file='nwk.txt')
        open(101, file='nwk_ks.txt')
        ! get the degree of each bot based on the distance
        bot_degree = 0
        do i=1,N_bots
          read(101,*) bot_degree(i)
          if (bot_degree(i).ne.0) print*, bot_degree(i)
        enddo
        sum_degree = sum(bot_degree)
        print*, sum_degree
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
        do while(1.eq.1)
            read(100,*,iostat=read_stat) i, j
            ! add 1 as networkx labels starting from 0, and here we label starting from 1
            i = i+1
            j = j+1
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
        close(101)
        print*, neighbors

    end subroutine get_contact_list

end module prova

program main
    use prova
    N_bots = 35
    call get_contact_list()
end program main


