program prova
    implicit none
    integer N_bots,i,file_index
    character(2) :: auxi

    file_index = 100
    open(unit=file_index, file='prova.dat')

    N_bots = 10
    do i=1,N_bots-1
        write(auxi, '(I2)') i
        !write(file_index, '(I2,A)', advance='no') i,","
        write(file_index, '(A)', advance='no') trim(adjustl(auxi))//','
    enddo
    write(auxi,'(I2)') N_bots
    write(file_index, '(A)') trim(adjustl(auxi))

    do i=N_bots,2,-1
        write(auxi, '(I2)') i
        !write(file_index, '(I2,A)', advance='no') i,","
        write(file_index, '(A)', advance='no') trim(adjustl(auxi))//','
    enddo
    i=1
    write(auxi,'(I2)') i
    write(file_index, '(A)') trim(adjustl(auxi))
    
end program