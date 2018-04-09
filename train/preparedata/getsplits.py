CUHK03MAT = '/home/ckp/caffe/data/cuhk-03.mat'
import h5py
import re, os, os.path,shutil
import glob
import numpy as np


dataset = h5py.File(CUHK03MAT) 
imagedataset=glob.glob(r'labeled/*/*.png')
for num_split in range(1,6):
    #filename="split_person_id"+'%d' %num_split+".txt"
    #f=open(filename,'a+')
    #f.truncate
    personid=[]
    for j in xrange(dataset[dataset['testsets'][0][num_split-1]].shape[1]) :
        person_id = np.int(dataset[dataset['testsets'][0][num_split-1]][0][j] * 1000 + dataset[dataset['testsets'][0][num_split-1]][1][j])
        #print np.int(dataset[dataset['testsets'][0][num_split-1]][0][j])
        ss='%d' %person_id
	personid.append(ss)
		
        #f.writelines(ss)
        #print np.int(dataset[dataset['testsets'][0][num_split-1]][1][j])
        #test_set.add(person_id)
    
    trainname="split"+'%d' %num_split+"_train.txt"
    with open(trainname, 'w+') as f1:
      for filename in imagedataset:
        if filename[20:24] not in personid:
          f1.write('/home/ckp/caffe/validation/' + filename + ' '+filename[20:24]+'\n')    
    
    valname="split"+'%d' %num_split+"_val.txt"
    with open(valname, 'w+') as f2:
      for filename in imagedataset:
        if filename[20:24] in personid:
          f2.write('/home/ckp/caffe/validation/' + filename + ' '+filename[20:24]+'\n')    
