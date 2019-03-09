from datetime import datetime, timedelta
from matplotlib import pyplot as plt
from scipy import signal as sig
import numpy as np
import pytz
import h5py
import csv
import os

def set_name():
    for file in os.listdir("."):
        if file.endswith(".h5"):
            return file

#optional
#file = "1541962108935000000_167_838.h5"

time_unix_nano = int(set_name().split('.')[0].split('_')[0])
timezone_sec = pytz.timezone('Europe/Zurich')

time_utc = datetime.utcfromtimestamp(time_unix_nano / 1e9)
time_cern = time_utc.replace(tzinfo=pytz.utc).astimezone(timezone_sec)

file = set_name()

def visit_and_seg(f, groups=[], datasets=[]):
    all_h5_objs = []
    f.visit(all_h5_objs.append)

    for obj in all_h5_objs:
        if isinstance(f[obj], h5py.Group):
            groups.append(obj)
        elif isinstance(f[obj], h5py.Dataset):
            datasets.append(obj)
        else:
            continue
    return groups, datasets

with h5py.File(file, mode="r") as f:
    with open('awake_csv.csv', mode='w') as cs:
        fieldnames = ['Group', 'Subgroup', 'Name', 'Shape', 'Type', 'Size']
        writer = csv.DictWriter(cs, fieldnames=fieldnames)
        writer.writeheader()
        all_h5_objs = []
        groups = list(f.items())
        subgroups, datasets = visit_and_seg(f)

        for dataset in datasets:
            #print(dataset)
            data = f.get(dataset)
            group = dataset.split('/')[0]
            subgroup = '/'.join(dataset.split('/')[0:-1])
            name = dataset.split('/')[-1]
            shape = data.shape
            try:
                dtype = data.dtype
            except Exception as ex:
                dtype = '{0}'.format(ex.args).split(' ')[-2]
            size = data.size
            writer.writerow({'Group': group, 'Subgroup': subgroup, 'Name': name,
                   'Shape': shape, 'Type': dtype, 'Size': size})

    data1 = f.get("AwakeEventData/XMPP-STREAK/StreakImage/streakImageData")
    height = f.get("AwakeEventData/XMPP-STREAK/StreakImage/streakImageHeight")[0]
    width = f.get("AwakeEventData/XMPP-STREAK/StreakImage/streakImageWidth")[0]
    data_filt = sig.medfilt(np.reshape(data1, (height, width)))
    cs.close()
    cs.close()
f.close()

plt.imshow(data_filt, interpolation='nearest', aspect='auto')
plt.savefig('awakefig.png')
