# 基于深度学习的单幅图像的超分辨率
## 基于TensorFlow1.14对以下论文的实装，已经通过训练与测试
## "Deep Laplacian Pyramid Networks for Fast and Accurate Super-Resolution" (CVPR 2017)

本次实装依据论文Github：
$ git clone https://github.com/zjuela/LapSRN-tensorflow.git

### 软件环境
Windows10 Visual Studio Code
Python3.6
Cuda 8.0
TensorLayer

### 硬件环境
CPU- i7 8700K 3.70GHz
RAM- 32GB
GPU- GeForce 1080 Ti

### 数据库
DIV2K-Dataset
https://data.vision.ee.ethz.ch/cvl/DIV2K/
训练用数据集：DIV2K_train_HR，DIV2K_train_LR_bicubic/X4/
验证用数据集：DIV2K_valid_HR, DIV2K_valid_LR_bicubic/X4/

### 下载节点:

    $ git clone https://github.com/Dakewe-DS1000/LapRSNet.git

### 训练方法
训练之前，请检查config.py，以保证数据集的路径的正确性，然后运行以下命令进行训练：

	$ python main.py --mode train

### 测试方法
指定路径与图像文件名的测试:

	$ python main.py --mode test --file 测试图像所在的路径以及文件名

测试的结果将会保存在 /samples/test/






