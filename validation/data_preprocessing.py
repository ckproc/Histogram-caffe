import cv2
import numpy as np

def transpose_for_storage(im):
    return im.transpose((2, 0, 1))
def transpose_for_show(im):
    return im.transpose((1, 2, 0))                                                                                                        
def break_the_image(stripes_num, img, overlap = 0):
    parts = list();
    overlap_stripes_num = stripes_num - 1;
    
    part_height = (np.shape(img)[0] + overlap_stripes_num * overlap)/stripes_num;
    
    for i in range(stripes_num):
        
        start = i * part_height - max((i) * overlap, 0);
        end = min(np.shape(img)[0], start + part_height);
        current_part = np.copy(img[start:end][:][:])    
        parts.extend(transpose_for_storage(current_part));
        
    return np.array(parts);    


def prepareImage(im, transform_params):
    if transform_params.has_key('reshape_params'):
        if transform_params['reshape_params'].has_key('resize'):
            im = cv2.resize(im, transform_params['reshape_params']['resize'])
       
        if transform_params['reshape_params'].has_key('stripes') and transform_params['reshape_params'].has_key('overlap') :   
            im = break_the_image(transform_params['reshape_params']['stripes'], im, overlap=transform_params['reshape_params']['overlap'] );
    return im;


def prepareDataset(dataset_dict, transform_params):
    result = dict()

    for l in dataset_dict.keys() :
        if not result.has_key(l):
           result[l] = []
        for i in xrange(len(dataset_dict[l])):
            image_prepared = prepareImage(dataset_dict[l][i], transform_params)        
            result[l].append(image_prepared) 
    return result

#def prepareDataset(image_path, transform_params):
#    images = list()
#    for i in xrange(len(image_path)):
#        im = cv2.imread(image_path[i], cv2.IMREAD_COLOR)
#        images_prepared = prepareImage(im, transform_params)        
#        images.append(images_prepared) #only one image is supposed to return 
#    return images
