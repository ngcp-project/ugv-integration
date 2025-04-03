import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import re



def update_data(i):
    longitude = []
    latitude = []

    pattern = r'Longitude:\s*(-?\d+\.\d+),\s*Latitude:\s*(-?\d+\.\d+)'

    with open ('ugv_logger.txt') as f:
        lines = f.readlines()

        for line in lines:
            match = re.search(pattern, line)
            
            if match:
                longitudetemp = float(match.group(1))
                latitudetemp = float(match.group(2))

                longitude.append(longitudetemp)
                latitude.append(latitudetemp)


    plt.cla()
    plt.title('GPS from Xsens logger file')
    plt.xlabel('longitude')
    plt.ylabel('latitude')
    plt.tight_layout()
    plt.plot(longitude,latitude)

anim = FuncAnimation(plt.gcf(), update_data, interval = 1000), 


plt.show()
