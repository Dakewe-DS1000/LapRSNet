# Deep Laplacian Pyramid Networks for Fast and Accurate Super-Resolution (CVPR 2017)
# Python程序下载，训练与数字病理图像超分辨率的应用

本程序基于TensorFlow，使用“TensorLayer”进行编程实现

原始程序通过以下Git下载：

[project webpage](http://vllab1.ucmerced.edu/~wlai24/LapSRN/).

### 编程与实验环境
python 3.6 

cuda 8.0.

### 源代码下载节点:

    $ git clone https://github.com/zjuela/LapSRN-tensorflow.git

### 训练
在程序config.py文件中指定相应的图像数据库，并运行以下命令进行训练:

	$ python main.py

预先训练的模型使用以下数据库，请到以下网址进行数据库下载：

[NTIRE 2017](http://www.vision.ee.ethz.ch/ntire17/)

### 测试
运行以下命令，并指定输入的图像文件:

	$ python main.py -m test -f TESTIMAGE

TESTIMAGE是输入的图像文件的整个路径与文件名加后缀

测试的结果请在文件夹./samples/中进行查看

### 评价
使用PSNR对超分辨率之后的图像以及原始高分辨率图像进行对比

请运行以下命令，对输出在./samples/中的图像进行对比评价

	$ python validation.py

> 请注意：需要将原始图像拷贝到./samples/文件夹中\
并进行相应的文件命名，在本程序中，文件命名规则如下：\
test_origin.bmp：是原始的高分辨率图像文件
test_out.bmp：是LapRSNet输出的超分辨率图像文件

评价算法主要的代码如下：
	
	import cv2
	import math
	
	diff = 0.0
	# 遍历整个图像
    for y in range(oriHeight) :
       	for x in range(oriWidth) :
		   # 计算图像差分的平方和
		   diff += (float(origin_image[y, x]) - float(result_image[y, x])) * (float(origin_image[y, x]) - float(result_image[y, x]))
	
	# 计算图像差分的均值
    diff /= oriHeight * oriWidth
    print("DIFF : ", diff)

	#计算图像RMS误差
    rmse = math.sqrt(diff)
    print("RMSE : ", rmse)

	# 计算图像的PSNR(Peak Signal and Noise Rate)
    psnr = 20.0 * math.log10(255.0 / rmse)
    print("PSNR : ", psnr, " [dB]")





