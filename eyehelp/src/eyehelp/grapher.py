'''
Graph blinks as a function of time
'''
# import packages
from matplotlib import pyplot as plt 
import os
import sys

def start_graphing():
    # initialize data file to read from
    ospath = os.path.dirname(sys.argv[0])
    EAR_DATA_FILE = ospath + '\\ear_data'
    ear_data = open(EAR_DATA_FILE, 'r')

    # read data file into an array
    array = [int(float(i)*100) for i in ear_data.readlines()] 
    # plot the array
    plt.xlabel('Frames')
    plt.ylabel('Eye Aspect Ratio (%)')
    plt.title('EAR per frame graph')
    plt.plot(array)
    plt.show()

if __name__=='__main__':
    start_graphing()