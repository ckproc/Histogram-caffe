#HistogramLoss

1.Prepare data
 
 get cuhk03 dataset http://pan.baidu.com/s/1qXSXIw8 ,upzip it and get the cuhk-03.mat file.
 
 then run the function "parseCuhk03" in "validation/vali_recall.py" with parameter 'writeImages' = True,
 and the image files will be produced.

2.Train Histogram Loss on cuhk03
 
 first run file in "train/preparedata/"(you should change the directories in getslits.py).
 ```shell
 python getsplits.py
 ```
 then run file in "train/preparedata/" to prepare lmdb data of each split for training.
 ```shell
 python precuhk03lmdbdata.py
 ```
 last run "train/traincuhk03.sh" to train the model.
 ```shell
 bash traincuhk03.sh
 ```
 Note : you should add the cosine_similarity_batch_layer.hpp and cosine_similarity_batch_layer.cpp file to your own caffe and change the caffe.proto file.
 
3.Test on trained models
 
 after trained the model,use it to test recall@K on the 5 splits by run the file in "validation/".
 ```shell
 python vali_recall.py
 ```