"""Deep Laaplacian Pyramid Networks for Fast and Accurate Super-Resolution"
算法分为两个分支：
1- 特征提取分支
   对图像的特征进行提取，提取后的图像类似于Laplace边缘强化后的图像，也就是说，所提取的特征就是放大后模拟的插值信息
2- 图像重构分支
   对于每一级而言，对输入图像用一个Scale等于4的一个上采样层进行操作，
   然后这个上采样层将和当前层的特征提取分支预测到的Residual图进行相加，
   相加利用Element-wise Summation
   并将相加得到的HR图像输入到下一级中
因此，整个网络就是一个Cascade的CNN架构

本算法还另外创造了新的损失策略
   由于网络是级联的，因此我们需要对每一级的输出都进行误差的损失，
   举例来说，当我们的网络一种有2级也就是对图像分辨率提升4倍这样的一个实际实例而言
   第二级的标签显而易见就是我们给出的HR的高清图，而第一级的标签，我们定义为
   用双立方下采样来得到的这一级的标签
   就是因为这种Loss的策略实现了文章中说的
   我们即使训练的是3级的网络，我们仍然能够很好的利用前面两级来放大两倍或者四倍的超分辨率图"""

import os, time, random
import numpy as np
import scipy

import tensorflow as tf
import tensorlayer as tl
from model import *
from utils import *
from config import *

import pdb #用于debug跟踪调试
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

###====================== HYPER-PARAMETERS ===========================###
batch_size = config.train.batch_size
patch_size = config.train.in_patch_size
ni = int(np.sqrt(config.train.batch_size))

def compute_charbonnier_loss(tensor1, tensor2, is_mean=True):
    epsilon = 1e-6
    if is_mean:
        loss = tf.reduce_mean(tf.reduce_mean(tf.sqrt(tf.square(tf.subtract(tensor1,tensor2))+epsilon), [1, 2, 3]))
    else:
        loss = tf.reduce_mean(tf.reduce_sum(tf.sqrt(tf.square(tf.subtract(tensor1,tensor2))+epsilon), [1, 2, 3]))
    return loss


#调取训练和验证数据集的文件
def load_file_list():
    train_hr_file_list = []
    train_lr_file_list = []
    valid_hr_file_list = []
    valid_lr_file_list = []

    directory = config.train.hr_folder_path
    for filename in [y for y in os.listdir(directory) if os.path.isfile(os.path.join(directory,y))]:
        train_hr_file_list.append("%s%s"%(directory,filename))

    directory = config.train.lr_folder_path
    for filename in [y for y in os.listdir(directory) if os.path.isfile(os.path.join(directory,y))]:
        train_lr_file_list.append("%s%s"%(directory,filename))

    directory = config.valid.hr_folder_path
    for filename in [y for y in os.listdir(directory) if os.path.isfile(os.path.join(directory,y))]:
        valid_hr_file_list.append("%s%s"%(directory,filename))

    directory = config.valid.lr_folder_path
    for filename in [y for y in os.listdir(directory) if os.path.isfile(os.path.join(directory,y))]:
        valid_lr_file_list.append("%s%s"%(directory,filename))

    return sorted(train_hr_file_list),sorted(train_lr_file_list),sorted(valid_hr_file_list),sorted(valid_lr_file_list)


#准备训练和验证用的图像
def prepare_nn_data(hr_img_list, lr_img_list, idx_img=None):
    i = np.random.randint(len(hr_img_list)) if (idx_img is None) else idx_img

    input_image  = get_imgs_fn(lr_img_list[i])
    output_image = get_imgs_fn(hr_img_list[i])
    scale        = int(output_image.shape[0] / input_image.shape[0])
    assert scale == config.model.scale

    out_patch_size = patch_size * scale
    input_batch  = np.empty([batch_size,patch_size,patch_size,3])
    output_batch = np.empty([batch_size,out_patch_size,out_patch_size,3])

    for idx in range(batch_size):
        in_row_ind   = random.randint(0,input_image.shape[0]-patch_size)
        in_col_ind   = random.randint(0,input_image.shape[1]-patch_size)    

        input_cropped = augment_imgs_fn(input_image[in_row_ind:in_row_ind+patch_size,
                                                in_col_ind:in_col_ind+patch_size])
        input_cropped = normalize_imgs_fn(input_cropped)
        input_cropped = np.expand_dims(input_cropped,axis=0)
        input_batch[idx] = input_cropped
    
        out_row_ind    = in_row_ind * scale
        out_col_ind    = in_col_ind * scale
        output_cropped = output_image[out_row_ind:out_row_ind+out_patch_size,
                                      out_col_ind:out_col_ind+out_patch_size]
        output_cropped = normalize_imgs_fn(output_cropped)
        output_cropped = np.expand_dims(output_cropped,axis=0)
        output_batch[idx] = output_cropped
    return input_batch,output_batch



def train():
    save_dir = "%s/%s_train"%(config.model.result_path,tl.global_flag['mode'])
    checkpoint_dir = "%s"%(config.model.checkpoint_path)
    #本地创建缓存文件夹
    #如果不存在文件夹，则创建
    #如果已存在文件夹，则检测后不创建
    tl.files.exists_or_mkdir(save_dir)          #在本地创建文件夹：samples\train_train
    tl.files.exists_or_mkdir(checkpoint_dir)    #在本地创建文件夹：checkpoint

    ###========================== DEFINE MODEL ============================###
    #placeholder，占位符，先放在这里，等需要的时候，通过feed_dict映射，传入数据给深度学习网络
    #placeholder(数据类型，数据维度，数据名称)

    #输入的低分辨图像数据的占位符
    # size = batch_size X batch_size
    #在这里是原始高清图像经过图像处理算法压缩后的图像
    t_image = tf.placeholder('float32', [batch_size, patch_size, patch_size, 3], name='t_image_input')
    
    #输出的高分辨目标图像数据的占位符
    # size = (batch_size x scale) X (batch_size x scale)
    #在这里是原始的高清图像
    t_target_image = tf.placeholder('float32', [batch_size, patch_size*config.model.scale, patch_size*config.model.scale, 3], name='t_target_image')
    
    #降采样（图像缩小）后的图像数据占位符
    # size = patch_size x 2 X patch_size x 2
    #在这里的降采样图像数据，来自于目标图像数据，是通过图像处理算法按照一定比例进行压缩的中间图像
    t_target_image_down = tf.image.resize_images(t_target_image, size=[patch_size*2, patch_size*2], method=0, align_corners=False) 

    #配置超分辨率的深度学习模型：LapSRN(t_image, is_train=True, reuse=False)
    #输入：原始图像，t_image
    #输出：  net_image1：第一级网络图
    #       net_image2：第二级网络图
    #       net_grad1：第一级梯度图
    #       net_grad2：第二级梯度图

    #LapSRN函数里面包括两级超分辨，每一级超分辨对应函数LapSRNSingleLevel
    #函数LapSRNSingleLevel的输出，除了网络图和梯度图，还有特征图，net_feature
    #特征图可在实验过程中输出出来看看是什么样子
    net_image2, net_grad2, net_image1, net_grad1 = LapSRN(t_image, is_train=True, reuse=False)
    net_image2.print_params(False)

    #配置超分辨的测试模型：LapSRN(t_image, is_train=False, reuse=True)
    #输入：原始图像，t_image
    #输出：
    # net_image_test：测试的网络最终输出，这是测试过程中的第二级网络图
    # net_grad_test：测试的梯度最终输出，这是测试过程中的第二级梯度图
    net_image_test, net_grad_test, _, _ = LapSRN(t_image, is_train=False, reuse=True)

    ###========================== DEFINE TRAIN OPS ==========================###
    #用来计算损失量的函数和计算方法
    #第二级网络的输出与真值比较，计算损失loss2
    #net_image2的输出是整个网络的输出，也就是第二级网络的输出
    #t_target_image是真实超分辨大图的输出
    #以上两者进行比较计算，输出损失量
    loss2   = compute_charbonnier_loss(net_image2.outputs, t_target_image, is_mean=True)
    #第一级网络的输出与真值比较，计算损失loss1
    #net_image1的输出是第一级网络的输出
    #t_target_image_down是降采样之后的真实图像，作为第一级网络的真值
    #以上两者进行比较计算，输出损失量
    loss1   = compute_charbonnier_loss(net_image1.outputs, t_target_image_down, is_mean=True)
    #第一级网络的损失与第二级网络的损失通过以下计算，得到整个网络的损失量
    g_loss  = loss1 + loss2 * 4
    g_vars  = tl.layers.get_variables_with_name("LapSRN", True, True)
    
    with tf.variable_scope("learning_rate"):
        lr_v = tf.Variable(config.train.lr_init, trainable=False)

    #优化器计算后的损失量
    g_optim = tf.train.AdamOptimizer(lr_v, beta1=config.train.beta1).minimize(g_loss, var_list=g_vars)
    
    ###========================== RESTORE MODEL =============================###
    sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True, log_device_placement=False))
    tl.layers.initialize_global_variables(sess)
    #加载已有的模型
    tl.files.load_and_assign_npz(sess=sess, name=checkpoint_dir+"/params_{}.npz".format(tl.global_flag["mode"]), network=net_image2)

    ###========================== PRE-LOAD DATA ===========================###
    #加载训练用高分辨图像数据，训练用低分辨数据，验证用高分辨数据，验证用低分辨数据
    # 训练用高分辨数据：train_hr_list
    # 训练用低分辨数据：train_lr_list
    # 验证用高分辨数据：valid_hr_list
    # 验证用低分辨数据：valid_lr_list
    train_hr_list,train_lr_list,valid_hr_list,valid_lr_list = load_file_list()
 
    ###========================== INTERMEDIATE RESULT ===============================###
    sample_ind = 37
    #获取用于验证的数据，包括验证用的高分辨数据，验证用的低分辨数据
    #这个函数后面要仔细阅读：prepare_nn_data
    #sample_input_imgs 是验证用低分辨图像数据
    #sample_output_imgs 是验证用高分辨图像数据
    sample_input_imgs,sample_output_imgs = prepare_nn_data(valid_hr_list,valid_lr_list,sample_ind)
    tl.vis.save_images(truncate_imgs_fn(sample_input_imgs),  [ni, ni], save_dir+"/train_sample_input.png")
    tl.vis.save_images(truncate_imgs_fn(sample_output_imgs), [ni, ni], save_dir+"/train_sample_output.png")

    ###========================== TRAINING ====================###
    sess.run(tf.assign(lr_v, config.train.lr_init))
    print(" ** learning rate: %f" % config.train.lr_init)

    for epoch in range(config.train.n_epoch):
        ## update learning rate
        if epoch != 0 and (epoch % config.train.decay_iter == 0):
            lr_decay = config.train.lr_decay ** (epoch // config.train.decay_iter)
            lr = config.train.lr_init * lr_decay
            sess.run(tf.assign(lr_v, lr))
            print(" ** learning rate: %f" % (lr))

        epoch_time = time.time()
        total_g_loss, n_iter = 0, 0

        ## load image data
        #将train_hr_list里面的内容，打乱顺序
        idx_list = np.random.permutation(len(train_hr_list))
        #遍历打乱顺序后的train_hr_list，也即idx_list
        for idx_file in range(len(idx_list)):
            step_time = time.time()
            #获取用于训练的图像数据，包括训练用高分辨图像数据，训练用低分辨图像数据
            batch_input_imgs,batch_output_imgs = prepare_nn_data(train_hr_list,train_lr_list,idx_file)
            #在这里实现之前说的占位符映射
            #t_image 映射 batch_input_imgs，这是训练用低分辨图像数据
            #t_target_image 映射 batch_output_imgs，这是训练用高分辨图像数据
            errM, _ = sess.run([g_loss, g_optim], {t_image: batch_input_imgs, t_target_image: batch_output_imgs})
            total_g_loss += errM
            n_iter += 1
        
        print("[*] Epoch: [%2d/%2d] time: %4.4fs, loss: %.8f" % (epoch, config.train.n_epoch, time.time() - epoch_time, total_g_loss/n_iter))

        ## save model and evaluation on sample set
        if (epoch >= 0):
            tl.files.save_npz(net_image2.all_params,  name=checkpoint_dir+"/params_{}.npz".format(tl.global_flag["mode"]), sess=sess)
            
            if config.train.dump_intermediate_result is True:
                sample_out, sample_grad_out = sess.run([net_image_test.outputs,net_grad_test.outputs], {t_image: sample_input_imgs})#; print('gen sub-image:', out.shape, out.min(), out.max())
                tl.vis.save_images(truncate_imgs_fn(sample_out), [ni, ni], save_dir+"/train_predict_%d.png" % epoch)
                tl.vis.save_images(truncate_imgs_fn(np.abs(sample_grad_out)), [ni, ni], save_dir+"/train_grad_predict_%d.png" % epoch)
            


def test(file):
    try:
        img = get_imgs_fn(file)
    except IOError:
        print('cannot open %s'%(file))
    else:
        checkpoint_dir = config.model.checkpoint_path
        save_dir = "%s/%s"%(config.model.result_path,tl.global_flag['mode'])
        input_image = normalize_imgs_fn(img)

        size = input_image.shape
        print('Input size: %s,%s,%s'%(size[0],size[1],size[2]))
        t_image = tf.placeholder('float32', [None,size[0],size[1],size[2]], name='input_image')
        net_g, _, _, _ = LapSRN(t_image, is_train=False, reuse=False)

        ###========================== RESTORE G =============================###
        sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True, log_device_placement=False))
        tl.layers.initialize_global_variables(sess)
        tl.files.load_and_assign_npz(sess=sess, name=checkpoint_dir+'/params_train.npz', network=net_g)

        ###======================= TEST =============================###
        start_time = time.time()
        out = sess.run(net_g.outputs, {t_image: [input_image]})
        print("took: %4.4fs" % (time.time() - start_time))
    
        tl.files.exists_or_mkdir(save_dir)
        tl.vis.save_image(truncate_imgs_fn(out[0,:,:,:]), save_dir+'/test_out.bmp')
        tl.vis.save_image(input_image, save_dir+'/test_input.bmp')



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', choices=['train','test'], default='train', help='select mode')
    parser.add_argument('-f','--file', help='input file')
    
    args = parser.parse_args()

    tl.global_flag['mode'] = args.mode
    if tl.global_flag['mode'] == 'train':
        train()
    elif tl.global_flag['mode'] == 'test':
        if (args.file is None):
            raise Exception("Please enter input file name for test mode")
        test(args.file)
    else:
        raise Exception("Unknow --mode")
