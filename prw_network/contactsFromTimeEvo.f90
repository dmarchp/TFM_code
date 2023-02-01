program main
 implicit none
 integer :: loops = 800, ticksPerSecond = 31, N = 35, speed = 9, speedVar = 2
 double precision :: timeStep = 0.0103d0, ticksPerLoop, 
 character :: configs_path = 'raw_json_files/RWDIS_mod/configs/'
 character :: configFileName  = 'PRW_nBots_35_ar_20.0_speed_9_speedVar_2_001.csv'
 character :: contactsFileName = 'PRW_nBots_35_ar_20.0_speed_9_speedVar_2_001_contacts.csv'
 
 
 
