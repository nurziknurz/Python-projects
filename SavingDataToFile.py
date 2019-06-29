#This is programm to save data to a file to manage data in Excel

import datetime

now_time = datetime.datetime.now()


#Creating new file
new_file = open('datafile' + '_' + str(now_time.day) + '_' + str(now_time.month) + '_' + str(now_time.hour) + '_' + str(now_time.minute) + '.txt', 'w')


new_file.write(str(10) + ':' + str(12))
new_file.write(';')
new_file.write(str(555.666))          
new_file.write('\n')
new_file.write(str(11) + ':' + str(22))
new_file.write(';')
new_file.write(str(666.555))




#Closing the newly created file
new_file.close()
