#! /usr/bin/env python
#-*- coding:utf-8 -*-
import sys
import glob
import random
import numpy as np
import string
import cv2
import caffe
from caffe.proto import caffe_pb2
import lmdb

#Size of images
IMAGE_WIDTH = 60
IMAGE_HEIGHT = 160
OVERLAP=10
STRIPES=3
# train_lmdb、validation_lmdb 路径

num_split=raw_input("enter the num_split by 1~5:")
if num_split not in ['1','2','3','4','5']:
 print "invalid input"
 sys.exit()

train_lmdb = '/home/ckp/caffe/models/cuhk03/lmdb_train'+num_split
validation_lmdb = '/home/ckp/caffe/models/cuhk03/lmdb_validation'+num_split

# 如果存在了这个文件夹, 先删除
os.system('rm -rf  ' + train_lmdb)
os.system('rm -rf  ' + validation_lmdb)

# 读取图像
#train_data = [img for img in glob.glob("/home/chenxp/Documents/vehicleID/val/query/*jpg")]
#test_data = [img for img in glob.glob("/home/chenxp/Documents/vehicleID/val/query/*jpg")]
name1="/home/histogram/train/preparedata/split"+num_split+"_train.txt"
name2="/home/histogram/train/preparedata/split"+num_split+"_val.txt"
print "prepare to produce split"+num_split+" lmdbdata"
f = open(name1)
line = f.readline()
train_data=[]
while line:
 train_data.append(line)                
 line = f.readline()
f.close()

f1 = open(name2)
line = f1.readline()
test_data=[]
while line:
 test_data.append(line)                
 line = f1.readline()
f1.close()
# Shuffle train_data
# 打乱数据的顺序
#random.shuffle(train_data)
#random.shuffle(test_data)

# 图像的变换, 直方图均衡化, 以及裁剪到 IMAGE_WIDTH x IMAGE_HEIGHT 的大小
def transpose_for_storage(im):
    return im.transpose((2, 0, 1))
def transform_img(img, img_width=IMAGE_WIDTH, img_height=IMAGE_HEIGHT,img_stripes=STRIPES,img_overlap=OVERLAP):
    img = cv2.resize(img, (img_width, img_height))
    parts = list();
    overlap_stripes_num = img_stripes - 1;
    
    part_height = (np.shape(img)[0] + overlap_stripes_num * img_overlap)/img_stripes;
    
    for i in range(img_stripes):
        
        start = i * part_height - max((i) * img_overlap, 0);
        end = min(np.shape(img)[0], start + part_height);
        current_part = np.copy(img[start:end][:][:])    
        parts.extend(transpose_for_storage(current_part));
        
    return np.array(parts);  
    #Histogram Equalization
    #img[:, :, 0] = cv2.equalizeHist(img[:, :, 0])
    #img[:, :, 1] = cv2.equalizeHist(img[:, :, 1])
    #img[:, :, 2] = cv2.equalizeHist(img[:, :, 2])

    #Image Resizing, 三次插值
    #, interpolation = cv2.INTER_CUBIC)
    #return img

def make_datum(img, label):
    #image is numpy.ndarray format. BGR instead of RGB
    return caffe_pb2.Datum(
        channels=9,
        width=60,
        height=60,
        label=label,
	data=img.tobytes())
        #data=np.rollaxis(img, 2).tobytes())　# or .tostring() if numpy < 1.9

# 打开 lmdb 环境, 生成一个数据文件，定义最大空间, 1e12 = 1000000000000.0

in_db = lmdb.open(train_lmdb, map_size=int(1e12)) 
with in_db.begin(write=True) as in_txn: # 创建操作数据库句柄
    for in_idx, img_path in enumerate(train_data):
        #if in_idx %  6 == 0: # 只处理 5/6 的数据作为训练集
        #    continue         # 留下 1/6 的数据用作验证集
        # 读取图像. 做直方图均衡化、裁剪操作
        img = cv2.imread(img_path[:57], cv2.IMREAD_COLOR)
        img = transform_img(img, img_width=IMAGE_WIDTH, img_height=IMAGE_HEIGHT)
	label=string.atoi(img_path[58:62])

        #if 'cat' in img_path: # 组织 label, 这里是如果文件名称中有 'cat', 标签就是 0
        #    label = 0         # 如果图像名称中没有 'cat', 有的是 'dog', 标签则为 1
        #else:                 # 这里方, label 需要自己去组织
        #    label = 1         # 每次情况可能不一样, 灵活点

        datum = make_datum(img, label)
        # '{:0>5d}'.format(in_idx):
        #      lmdb的每一个数据都是由键值对构成的,
        #      因此生成一个用递增顺序排列的定长唯一的key
        in_txn.put('{:0>5d}'.format(in_idx), datum.SerializeToString()) #调用句柄，写入内存
        print '{:0>5d}'.format(in_idx) + ':' + img_path[:57]

# 结束后记住释放资源，否则下次用的时候打不开。。。
in_db.close() 

# 创建验证集 lmdb 格式文件
print '\nCreating validation_lmdb'
in_db = lmdb.open(validation_lmdb, map_size=int(1e12))
with in_db.begin(write=True) as in_txn:
    for in_idx, img_path in enumerate(test_data):
        #if in_idx % 6 != 0:
        #    continue
        img = cv2.imread(img_path[:57], cv2.IMREAD_COLOR)
        img = transform_img(img, img_width=IMAGE_WIDTH, img_height=IMAGE_HEIGHT,img_stripes=STRIPES,img_overlap=OVERLAP)
	label=string.atoi(img_path[58:62])
        #if 'cat' in img_path:
        #    label = 0
        #else:
        #    label = 1
        datum = make_datum(img, label)
        in_txn.put('{:0>5d}'.format(in_idx), datum.SerializeToString())
        print '{:0>5d}'.format(in_idx) + ':' + img_path[:57]
in_db.close()
print '\nFinished processing all images'
