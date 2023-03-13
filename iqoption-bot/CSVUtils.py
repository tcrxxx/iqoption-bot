import csv
import time

header = ['last_close', 'last_bollinger_up', 'last_bollinger_down', 'max_close_candle','min_close_candle']


def writeOnCSV(row):
    # open the file in the write mode
    f = open('./output/' + str(time.time()) + '-losses-log' , 'w')

    # create the csv writer
    #data = ['Afghanistan', 652090, 'AF', 'AFG']
    writer = csv.writer(f)

    # write a row to the csv file
    writer.writerow(row)

    # close the file
    f.close()