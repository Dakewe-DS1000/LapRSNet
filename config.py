from easydict import EasyDict as edict
import json

config = edict()

config.model = edict()
config.model.result_path = "D:/LapSRNet/samples"
config.model.checkpoint_path = "D:/LapSRNet/checkpoint"
config.model.log_path = "D:/LapSRNet/log"

config.model.scale = 4                  #对输入图像的上采样比例，论文中是2，不知道这里为什么是4
config.model.resblock_depth  = 10
config.model.recursive_depth = 1

#用于训练和验证的数据集，均来自DIV2K数据库
#链接如下：
#https://data.vision.ee.ethz.ch/cvl/DIV2K/
config.valid = edict()
# Default
#config.valid.hr_folder_path = 'F:/DataBase/LapSRN-Data/DIV2K_valid_HR/'              #用于验证的高分辨图像数据集
#config.valid.lr_folder_path = 'F:/DataBase/LapSRN-Data/DIV2K_valid_LR_bicubic/X4/'   #用于验证的低分辨图像数据集
#这里选用低分辨率的X4数据集，可能与上面的Scale等于4，是有关系的

# Digital Pathology Valid DataSet
config.valid.hr_folder_path = "F:/DataBase/LymphnodePathology/validDataSet/20X/"       #用于验证的显微高分辨图像数据集
config.valid.lr_folder_path = "F:/DataBase/LymphnodePathology/validDataSet/5X/"        #用于验证的显微低分辨图像数据集

config.train = edict()
# Default
#config.train.hr_folder_path = 'F:/DataBase/LapSRN-Data/DIV2K_train_HR/'              #用于训练的高分辨图像数据集
#config.train.lr_folder_path = 'F:/DataBase/LapSRN-Data/DIV2K_train_LR_bicubic/X4/'   #用于验证的低分辨图像数据集
#这里选用低分辨率的X4数据集，可能与上面的Scale等于4，是有关系的
config.train.hr_folder_path = "F:/DataBase/LymphnodePathology/trainDataSet/20X/"      #用于训练的显微高分辨图像数据集
config.train.lr_folder_path = "F:/DataBase/LymphnodePathology/trainDataSet/5X/"       #用于训练的显微高分辨图像数据集

#深度学习网络的一些参数设置
config.train.batch_size = 4             #如果有足够的GPU内存，这个Size可以设置地更大一些，以方便训练加速，但是似乎与图像数量有关，待考证, Default = 4
config.train.in_patch_size = 64         # Default = 64
config.train.out_patch_size = config.model.scale * config.train.in_patch_size
config.train.batch_size_each_folder = 30
config.train.log_write = False
#设置学习率的参数值
config.train.lr_init = 5 * 1.e-6
config.train.lr_decay = 0.5
config.train.decay_iter = 10
#设置偏移量的参数值
config.train.beta1 = 0.90
config.train.n_epoch = 1000              # Epoch Number while Training, Default = 300
config.train.dump_intermediate_result = True

def log_config(filename, cfg):
    with open(filename, 'w') as f:
        f.write("================================================\n")
        f.write(json.dumps(cfg, indent=4))
        f.write("\n================================================\n")
