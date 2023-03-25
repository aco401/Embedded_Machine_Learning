import sys
import numpy as np
import matplotlib.pyplot as plt
from time import strftime,gmtime

def main(argv):
    if len(argv) > 0:
        log_to_graph(argv[0])
    else:
        print("Wrong parameters")
        exit()

#np.array(['crooked', 'drinking', 'noperson', 'phone', 'straight'])
def log_to_info(logdir):
    amount = np.array([0, 0, 0, 0, 0])
    file = open(logdir, 'r')
    saved_index = -1
    saved_timestamp = 0
    for line in file:
        list = line.split(", ", 1)
        if not(saved_index == -1) and not(saved_timestamp == 0):
            amount[saved_index] += int(float(list[0]) - float(saved_timestamp))
            saved_index = -1
            saved_timestamp = 0

        if "crooked\n" == list[1]:
            saved_index = 0
            saved_timestamp = list[0]

        if "drinking\n" == list[1]:
            saved_index = 1
            saved_timestamp = list[0]

        if "noperson\n" == list[1]:
            saved_index = 2
            saved_timestamp = list[0]

        if "phone\n" == list[1]:
            saved_index = 3
            saved_timestamp = list[0]

        if "straight\n" == list[1]:
            saved_index = 4
            saved_timestamp = list[0]
    return amount

def log_to_graph(logdir):
    """ file = open(logdir, 'r+')
    lines = [line.split(',', 1) for line in file.readlines()]
    for indice in lines:
        indice[0] = int(float(indice[0]))
        indice[1] = (indice[1].replace("\n", "")).replace(" ", "")
    arr = np.array(lines)
    plt.plot(arr[::1, 0],arr[::1, 1])
    plt.show()
    plt.savefig(logdir + ".png") """
    amount = log_to_info(logdir)

    # Pie chart, where the slices will be ordered and plotted counter-clockwise:
    labels = ['crooked', 'drinking', 'noperson', 'phone', 'straight']

    fig, ax = plt.subplots()
    ax.pie(amount, labels=labels, autopct='%1.1f%%')
    ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
    ax.set_title('Working behavior')

    plt.show()
    filename = strftime("%Y-%m-%d_%H:%M:%S", gmtime())
    plt.savefig(filename + ".png")

    
    #print(arr[::1, 1])
    

        

if __name__ == '__main__':
    main(sys.argv[1:])