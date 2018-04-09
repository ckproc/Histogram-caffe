CUHK03MAT = '../data/cuhk-03.mat'
CUHK03_MODELS_ROOT = '/home/ckp/histogram/train/model/'
CAFFE_ROOT = '../'

import h5py
import cv2
import sys
import random as rnd
import os
from os import walk
caffe_root = CAFFE_ROOT  # this file is expected to be in {caffe_root}/examples/siameseimport sys
sys.path.insert(0, caffe_root + 'python')
import caffe
import numpy as np
sys.path.insert(0, '/')
import data_preprocessing as dp
import ranking as rank

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
        
        
def image_name(prefix, camera_num, person_id, photo_num):
    return prefix+"_"+str(camera_num)+"_"+str(person_id)+"_"+str(photo_num)+".png"

def parseCuhk03(dataset_path, writeImages = False, root = ''):
    dataset = h5py.File(dataset_path)
    labeled = dataset['labeled']
    detected = dataset['detected']
    
    labeled_dict = dict()
    detected_dict = dict()
    
    labeled_dict['cam_a'] = dict()
    labeled_dict['cam_b'] = dict()
    
    detected_dict['cam_a'] = dict()
    detected_dict['cam_b'] = dict()
    
    for cam_pair_num in xrange(labeled.shape[1]) : #cam
        cam_pair_labeled = dataset[labeled[0][cam_pair_num]]
        for i in xrange(cam_pair_labeled.shape[1]): #ids
            for j in xrange(cam_pair_labeled.shape[0]): #photos [1..10]
                curr_im_labeled = dataset[cam_pair_labeled[j][i]][:];
                if curr_im_labeled.shape == (2,) :
                    continue;
                    
                person_id = (cam_pair_num + 1) * 1000 + i + 1;
                im = cv2.cvtColor(curr_im_labeled.transpose((2,1,0)), cv2.COLOR_RGB2BGR)
                if writeImages:
                    dirname = os.path.join(root , "labeled",str(cam_pair_num+1)) + "/"
                    ensure_dir(dirname)
                    imname = os.path.join(root ,"labeled",str(cam_pair_num+1), image_name("labeled", cam_pair_num+1, 
                                                                                          person_id, j) )
                    cv2.imwrite(imname, im)

                if j <= 4 :
                    if person_id not in  labeled_dict['cam_a'] :
                        labeled_dict['cam_a'][person_id] = list()
                    labeled_dict['cam_a'][person_id].append(im)
                else :
                    if person_id not in  labeled_dict['cam_b'] :
                        labeled_dict['cam_b'][person_id] = list()
                    labeled_dict['cam_b'][person_id].append(im)
                    
    for cam_pair_num in xrange(detected.shape[1]) :
        cam_pair_detected = dataset[detected[0][cam_pair_num]]
        
        for i in xrange(cam_pair_detected.shape[1]): #ids
            for j in xrange(cam_pair_detected.shape[0]): #photos [1..10]
                curr_im_detected = dataset[cam_pair_detected[j][i]][:];
                if curr_im_detected.shape == (2,) :
                    continue;

                person_id = (cam_pair_num + 1) * 1000 + i + 1;
                im = cv2.cvtColor(curr_im_detected.transpose((2,1,0)), cv2.COLOR_RGB2BGR)
                if writeImages:
                    dirname = os.path.join(root ,"detected",str(cam_pair_num+1)) + "/"
                    ensure_dir(dirname)
                    cv2.imwrite(os.path.join(root ,"detected",str(cam_pair_num+1), image_name("detected", cam_pair_num+1,
                                                                                              person_id,j) ), im)
                if j <= 4 :
                    if person_id not in  detected_dict['cam_a'] :
                        detected_dict['cam_a'][person_id] = list()
                    detected_dict['cam_a'][person_id].append(im)
                else :
                    if person_id not in  detected_dict['cam_b'] :
                        detected_dict['cam_b'][person_id] = list()
                    detected_dict['cam_b'][person_id].append(im)
                    
    return  labeled_dict, detected_dict


def getDescriptorsFromDatasetDict(net, dataset_dict, test_labels, feat_name = 'ip1_reid', batch = 128):
    
    descriptors = dict()
    count = 0
    ims = []
    labels = []
    net.blobs['data'].reshape(batch, 9, 60, 60)
    for label in test_labels:
        for arr in dataset_dict[label]:
            
            if count == batch:
                count = 0
                res = net.forward_all(data=np.array(ims))[feat_name]
                for i in range(np.shape(res)[0]):
                    descriptors[labels[i]].append(res[i].astype('float64'))

                del ims[:]
                del labels[:]

            if (not label in descriptors):
                descriptors[label] = []
            ima = np.copy(arr)/256.
            ims.append(ima)
            labels.append(label)
            count +=1;             

    res = net.forward_all(data=np.array(ims))[feat_name]
    for i in range(np.shape(res)[0]):
        descriptors[labels[i]].append(res[i].astype('float64'));    
                  
    return descriptors;
    
def getTestSet(dataset_path, num) :
    dataset = h5py.File(dataset_path)
    #for i in xrange(dataset['testsets'].shape[1]):
    print dataset[dataset['testsets'][0][num-1]].shape
    test_set = set()
    #filename="idlist"+'%d' %num+".txt"
    #f=open(filename,'a+')
    #f.truncate
    for j in xrange(dataset[dataset['testsets'][0][num-1]].shape[1]) :
        person_id = np.int(dataset[dataset['testsets'][0][num-1]][0][j] * 1000 + dataset[dataset['testsets'][0][num-1]][1][j])
        #print np.int(dataset[dataset['testsets'][0][num-1]][0][j])
        #ss='%d' %person_id
        #ss=ss+'\n'
        #f.writelines(ss)
        #print np.int(dataset[dataset['testsets'][0][num-1]][1][j])
        test_set.add(person_id)
        
    return test_set



def similarity(x, y):
    xy = np.dot(x,y);
    xx = np.dot(x,x)
    yy = np.dot(y,y)
    return xy*1.0/np.sqrt(xx*yy)


def get_random_elements(person_descr_dict):
    result = dict()
    for p in person_descr_dict:
        result[p] = rnd.sample(person_descr_dict[p], 1)[0]
    return result    



def averageRankingSingleShot(descr_probe, descr_gallery, maxrank = 50, iterations =100):
    ranks = np.zeros(maxrank)
    for i in xrange(iterations):
        descr_probe_i = get_random_elements(descr_probe)
        descr_gallery_i = get_random_elements(descr_gallery)
        
        
        descrs_query = []
        query_labels = []

        for p in descr_probe_i.keys():
            query_labels.append(p)
            descrs_query.append(descr_probe_i[p])

    
        descrs_gallery = []
        gallery_labels = []

        for p in descr_gallery_i.keys():
            gallery_labels.append(p)
            descrs_gallery.append(descr_gallery_i[p])
    
        
        r = rank.ranking(descrs_query,query_labels,  descrs_gallery, gallery_labels, maxrank = maxrank)
        ranks+=r
        
    return ranks*1./iterations

labeled, detected = parseCuhk03(CUHK03MAT)
split1_test = getTestSet(CUHK03MAT, 1)
split2_test = getTestSet(CUHK03MAT, 2)
split3_test = getTestSet(CUHK03MAT, 3)
split4_test = getTestSet(CUHK03MAT, 4)
split5_test = getTestSet(CUHK03MAT, 5)




transform_params = dict()
transform_params['reshape_params'] = dict()
transform_params['reshape_params']['stripes'] = 3
transform_params['reshape_params']['overlap'] = 10
transform_params['reshape_params']['resize'] = (60, 160)
cuhk03_dict_prepared_cam_a = dp.prepareDataset(labeled['cam_a'], transform_params)
cuhk03_dict_prepared_cam_b = dp.prepareDataset(labeled['cam_b'], transform_params)

MODEL_FILE = os.path.join(CUHK03_MODELS_ROOT, 'train_val_model.prototxt')
WEIGHTS =  os.path.join(CUHK03_MODELS_ROOT, 'split1_cuhk03.caffemodel')
caffe.set_mode_gpu()
net = caffe.Classifier(MODEL_FILE,WEIGHTS)
cam_a_descr_split1 = getDescriptorsFromDatasetDict(net, cuhk03_dict_prepared_cam_a, 
                                                   test_labels = split1_test, feat_name = 'ip1_reid')
cam_b_descr_split1 = getDescriptorsFromDatasetDict(net, cuhk03_dict_prepared_cam_b, 
                                                   test_labels = split1_test,feat_name = 'ip1_reid')
labeled_split1_singleshot = averageRankingSingleShot(cam_a_descr_split1, cam_b_descr_split1, 
                                                     maxrank = 50, iterations =100)

                                                     
MODEL_FILE = os.path.join(CUHK03_MODELS_ROOT, 'train_val_model.prototxt')
WEIGHTS =  os.path.join(CUHK03_MODELS_ROOT, 'split2_cuhk03.caffemodel')
caffe.set_mode_gpu()
net = caffe.Classifier(MODEL_FILE,WEIGHTS)
cam_a_descr_split2 = getDescriptorsFromDatasetDict(net, cuhk03_dict_prepared_cam_a, 
                                                   test_labels = split2_test, feat_name = 'ip1_reid')
cam_b_descr_split2 = getDescriptorsFromDatasetDict(net, cuhk03_dict_prepared_cam_b, 
                                                   test_labels = split2_test,feat_name = 'ip1_reid')
labeled_split2_singleshot = averageRankingSingleShot(cam_a_descr_split2, cam_b_descr_split2, 
                                                     maxrank = 50, iterations =100)

MODEL_FILE = os.path.join(CUHK03_MODELS_ROOT, 'train_val_model.prototxt')
WEIGHTS =  os.path.join(CUHK03_MODELS_ROOT, 'split3_cuhk03.caffemodel')
caffe.set_mode_gpu()
net = caffe.Classifier(MODEL_FILE,WEIGHTS)
cam_a_descr_split3 = getDescriptorsFromDatasetDict(net, cuhk03_dict_prepared_cam_a, 
                                                   test_labels = split3_test, feat_name = 'ip1_reid')
cam_b_descr_split3 = getDescriptorsFromDatasetDict(net, cuhk03_dict_prepared_cam_b, 
                                                   test_labels = split3_test,feat_name = 'ip1_reid')
labeled_split3_singleshot = averageRankingSingleShot(cam_a_descr_split3, cam_b_descr_split3, 
                                                     maxrank = 50, iterations =100)

MODEL_FILE = os.path.join(CUHK03_MODELS_ROOT, 'train_val_model.prototxt')
WEIGHTS =  os.path.join(CUHK03_MODELS_ROOT, 'split4_cuhk03.caffemodel')
caffe.set_mode_gpu()
net = caffe.Classifier(MODEL_FILE,WEIGHTS)
cam_a_descr_split4 = getDescriptorsFromDatasetDict(net, cuhk03_dict_prepared_cam_a, test_labels = split4_test, feat_name = 'ip1_reid')
cam_b_descr_split4 = getDescriptorsFromDatasetDict(net, cuhk03_dict_prepared_cam_b, test_labels = split4_test,feat_name = 'ip1_reid')
labeled_split4_singleshot = averageRankingSingleShot(cam_a_descr_split4, cam_b_descr_split4, 
                                                     maxrank = 50, iterations =100)

MODEL_FILE = os.path.join(CUHK03_MODELS_ROOT, 'train_val_model.prototxt')
WEIGHTS =  os.path.join(CUHK03_MODELS_ROOT, 'split5_cuhk03.caffemodel')
caffe.set_mode_gpu()
net = caffe.Classifier(MODEL_FILE,WEIGHTS)
cam_a_descr_split5 = getDescriptorsFromDatasetDict(net, cuhk03_dict_prepared_cam_a, 
                                                   test_labels = split5_test, feat_name = 'ip1_reid')
cam_b_descr_split5 = getDescriptorsFromDatasetDict(net, cuhk03_dict_prepared_cam_b, 
                                                   test_labels = split5_test,feat_name = 'ip1_reid')
labeled_split5_singleshot = averageRankingSingleShot(cam_a_descr_split5, cam_b_descr_split5, 
                                                     maxrank = 50, iterations =100)

labeled_singleshot = (labeled_split1_singleshot+ \
                      labeled_split2_singleshot+ \
                      labeled_split3_singleshot+ \
                      labeled_split4_singleshot+ \
                      labeled_split5_singleshot)/5

print "recall@1:",labeled_singleshot[0]
print "recall@5:",labeled_singleshot[4]
print "recall@10:",labeled_singleshot[9]
print "recall@20:", labeled_singleshot[19]
print "recall@30:", labeled_singleshot[29]


