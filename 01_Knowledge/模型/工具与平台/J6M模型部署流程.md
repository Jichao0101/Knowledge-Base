# 1 流程

完整的模型部署流程应同时包含：  **训练集上的模型转换精度验证**，以及  **测试集上的最终模型精度验证**  

- **数据准备**  
    从训练集中抽取具有代表性的原始图片，构建：
    
    - calibration 数据集（RGB格式 + NPY），用于模型校准与中间精度验证
        
    - runtime 数据集（YUV格式 + NPY），用于模拟真实运行环境下的模型推理
        
- **pth模型验证**  
    在原始图片集上验证 pth 模型精度，作为后续模型转换精度对比的基准（Golden Reference）。
    
- **onnx模型验证**  
    将 pth 模型转换为 onnx 模型，并通过 hb_compile 对模型结构进行校验，确保模型算子与拓扑满足目标计算平台的支持约束。
	在calibration数据集上对onnx模型进行精度评测
    
- **bc模型转换**  
    基于校准数据集，将 onnx 模型逐步转换为 bc 模型，并进一步转换为 hbm 模型，用于目标硬件平台部署。
    
- **bc/hbm模型性能验证**  
    在 runtime 数据集上对 bc / hbm 模型进行性能测试，评估推理延迟、吞吐率及资源占用情况。
    
- **bc/hcm模型精度验证**  
    在 runtime 数据集上对 bc / hbm 模型进行精度评测，对比分析模型转换过程中可能引入的精度变化。

- **测试集精度验证**

  **独立测试集**上对最终部署模型进行精度验证，以评估模型在真实数据分布下的性能表现


# 2 数据预处理
## 2.1 前处理

目标是第一层算子输入张量一致

[[输入语义一致性]]
### 2.1.1 构建采样集

从 train/awake 与 train/sleepy 中按类别均衡随机采样共 N=100（seed 固定），得到 calibration_data_rgb/{id}.jpg

### 2.1.2 构建校准集

对每张 rgb 执行

- decode -> RGB HWC uint8

- resize -> 短边缩放到 128，长边按比例缩放（bilinear

- center crop -> 128×128

- HWC->CHW

- RGB->NV12

- 保存 runtime_data_bin/{id}.bin

- 同时拆分保存 runtime_data_npy/{id}.y.npy 与 runtime_data_npy/{id}.uv.npy

scale和norm写到yaml文件，由hb_compile修改计算图实现

### 2.1.3 构建运行集（NV12）

对每张 rgb 执行

- decode -> RGB HWC uint8

- resize -> 128×128（bilinear）

- RGB->YUV，标准：BT.xxx + range

- pack 为 NV12，保存 runtime_data_bin/{id}.bin

- 同时拆分保存 runtime_data_npy/{id}.y.npy 与 runtime_data_npy/{id}.uv.npy

> [!NOTE] 
> J6平台会将norm类预处理操作加入到模型graph中并在pyramid核完成加速处理，因此对比calibration操作，runtime数据不需要添加norm操作

## 2.2 数据集结构

```
datasets
|———calibration_data     
|	|---calibration_data_rgb     			
|	|	|---xx.jpg
|   |———calibration_data_npy
|       |——-xx.npy
|
|---runtime_data
	|---runtime_data_bin
	|	|---xx.bin
	|---runtime_data_npy
		|----xx.y.npy
		|---xx.uv.npy

```

# 3 onnx模型验证

将pth模型转换成onnx模型，进行模型验证，以确保其符合计算平台的支持约束
```
hb_compile --model resnet50.onnx \ --march nash-e
```
|   |   |
|---|---|
|`--march`|用于指定需要适配的处理器类型，J6E处理器请设置为 `nash-e`，J6M处理器需设置为 `nash-m`，J6P处理器需设置为 `nash-p`。|
|`--proto`|此参数仅在model-type指定caffe时有效，取值为caffe模型的 **prototxt** 文件名称； onnx模型无需配置该参数。|
|`--model`|在模型为caffe模型时，取值为Caffe模型的**caffemodel** 文件名称；在模型为onnx模型时，取值为 **ONNX模型** 文件名称。|

在calibration数据集上对onnx模型进行精度评测
# 4 模型转换

## 4.1 模型转换流程

### 4.1.1 输入数据处理

`边缘平台格式数据->数据格式转换->原始模型数据格式->数据前处理->模型计算`

### 4.1.2 模型优化编译

1. 模型解析：caffe模型会转换成onnx模型，产出 original_float_model.onnx
2. 模型优化：算子优化，产出float32的optimized_float_model.onnx
3. 模型校准：使用校准数据计算量化参数，产出calibrated_model.onnx 和 ptq_model.onnx
4. 模型量化：使用ptq_model.onnx 根据前处理配置（包括input_type_rt到input_type_train的色彩转换，mean/scale的处理等）进行模型量化， 产出 quantized_model.bc；如果模型量化过程中存在移除输入/输出端的节点的情况，会产出 quantized_removed_model.bc
5. 模型编译：将量化模型转换为地平线平台支持的计算指令和数据，产出*.hbm模型
## 4.2 构建yaml文件

### 4.2.1 hb_config_generator 构建yaml文件

`hb_config_generator --full-yaml --model model.onnx --march nash-e`

|**参数名称**|**参数说明**|
|---|---|
|`-h, --help`|显示帮助信息。|
|`-s, --simple-yaml`|生成最简yaml配置文件，用于您快速验证模型转换能否正常进行。|
|`-f, --full-yaml`|生成包含全部参数默认值的yaml配置文件。|
|`-m, --model`|Caffe或ONNX模型文件。|
|`-p, --proto`|用于指定Caffe模型prototxt文件。|
|`--march`|BPU的微架构。使用J6E处理器需设置为 `nash-e` ，使用J6M处理器需设置为 `nash-m` ，使用J6P处理器需设置为 `nash-p`。|
### 4.2.2 yaml文件示例

- input_type_train: 原始浮点模型的输入类型 (rgb, yuv444, bgr, nv12, gray, yuv420, feature map)
- Input_layout_train:原始浮点模型的输入布局 (NCHW/NHWC)
- input_type_rt：对接的边缘平台输入数据类型(rgb, yuv444, bgr, nv12, gray, yuv420, feature map)
- mean_value： mean * scale
- scale_value: 1/(std * sclale)

```
# 模型参数组

model_parameters:

  

  # 原始Onnx浮点模型文件

  onnx_model: '../../eye_state_model/mobilenet_v2.onnx'

  

  # 转换的目标处理器架构

  march: 'nash-m'

  

  # 模型转换输出的用于上板执行的模型文件的名称前缀

  output_model_file_prefix: 'mobilenet_v2_128x128_nv12'

  

  # 模型转换输出的结果的存放目录

  working_dir: '../../eye_state_model'

  

  debug_mode: 'dump_calibration_data'

  

# 输入信息参数组

input_parameters:

  

  # 原始浮点模型的输入节点名称

  input_name: ""

  

  # 原始浮点模型的输入数据格式（数量/顺序与input_name一致）

  input_type_train: 'rgb'

  

  # 原始浮点模型的输入数据排布（数量/顺序与input_name一致）

  input_layout_train: 'NCHW'

  

  # 原始浮点模型的输入数据尺寸

  input_shape: '1x3x128x128'

  

  # 网络实际执行时，输入给网络的batch_size，默认值为1

  input_batch: 1

  

  # 预处理方法的图像减去的均值, 如果是通道均值，value之间必须用空格分隔

  mean_value: '123.675 116.28 103.53'

  

  # 预处理方法的图像缩放比例，如果是通道缩放比例，value之间必须用空格分隔

  scale_value: '0.01712475 0.017507 0.01742919'

  

  # 转换后上板模型需要适配的输入数据格式（数量/顺序与input_name一致）

  input_type_rt: 'nv12'

  

  # 输入数据格式的特殊制式

  input_space_and_range: 'regular'

  

# 校准参数组

calibration_parameters:

  

  # 模型校准使用的标定样本的存放目录

  cal_data_dir: '../../data/calibration_data/calibration_data_npy/images'

# 编译参数组

compiler_parameters:

  

  # 编译策略选择

  compile_mode: 'latency'

  

  # 模型运行核心数

  core_num: 1

  

  # 模型编译的优化等级选择

  optimize_level: 'O2'

  

  # 指定模型的每个function call的最大可连续执行时间

  max_time_per_fc: 1000

  

  # 指定编译模型时的进程数

  jobs: 8
```

## 4.3 hb_compile 转换模型

`hb_compile -c src/translate_model/full_compile_config.yaml`

# 5 模型性能验证

## 5.1 静态性能评估

hb_compile 会生成 model.html 静态性能评估文件，包含性能评估核心指标 latency (us)，FPS等

## 5.2 动态性能评估

将hbm模型拷贝至开发板/userdata下任意路径，使用`hrt_model_exec perf` 工具快捷评估模型的耗时和帧率

```
# 单BPU核单线程串行状态下评测latency 
hrt_model_exec perf --model_file resnet50_224x224_nv12.hbm --thread_num 1 --frame_count 1000 --input_stride="50176,224,1,1;25088,224,2,1" 

# 单BPU核多线程并发状态下评测FPS 
hrt_model_exec perf --model_file resnet50_224x224_nv12.hbm --core_id 0 --thread_num 8 --frame_count 1000 --input_stride="50176,224,1,1;25088,224,2,1"
```

# 6 模型精度验证

## 6.1 hb_verifier 验证一致性

hb_verifier 支持 ONNX模型与HBIR模型、HBIR模型与HBIR模型之间的余弦相似度对比， HBIR与HBM模型之间的输出一致性对比

### 6.1.1 对比onnx模型与qbc模型的余弦相似度

```
hb_verifier -m optimized_float_model.onnx,quantized_model.bc -i calibration_data_npy/awake_s0001.npy
```

### 6.1.2 对比qbc模型与hbm模型的输出一致性

```
hb_verifier  -m quantized_model.bc,model.hbm -i runtime_data_npy/awake_s0001.y.npy,runtime_data_npy/awake_s0001.uv.npy
```

## 6.2 精度评测

| 格式   | Confusion Matrix [TP,FP,TN,FN] | Precision | Recall | Accuracy | Note                                  |
| ---- | ------------------------------ | --------- | ------ | -------- | ------------------------------------- |
| pth  | [45, 7, 44, 4]                 | 0.8654    | 0.9184 | 0.89     | 训练集均匀采样100张图片，其中闭眼49张，睁眼51张，闭眼为1，睁眼为0 |
| onnx | [45, 7, 44, 4]                 | 0.8654    | 0.9184 | 0.89     |                                       |
| bc   | [46, 6, 45, 3]                 | 0.8846    | 0.9388 | 0.91     |                                       |
| hbm  | [46, 6, 45, 3]                 | 0.8846    | 0.9388 | 0.91     |                                       |
# 7 测试集精度验证

在完成模型转换精度验证，并确认各阶段模型精度差异满足要求后，仍需在**独立测试集**上对最终部署模型进行精度验证，以评估模型在真实数据分布下的性能表现。

## 7.1 验证目的

测试集精度验证的目标在于：

- 评估模型在**未参与训练与校准的数据**上的泛化能力
    
- 排除因训练集分布偏置导致的精度“虚高”现象
    
- 验证模型在完成量化与硬件部署后，是否仍满足业务精度要求
    

该阶段不用于定位模型转换问题，而用于评估模型的**最终可用性**。

## 7.2 测试数据集要求

- 测试集需与训练集、校准集严格隔离
    
- 数据分布应尽可能覆盖真实业务场景
    
- 数据规模应满足统计稳定性要求
    

测试集仅用于精度评估，不参与任何形式的模型训练、校准或参数调整。

## 7.3 验证模型形态

测试集精度验证建议至少覆盖以下模型形态：

- 原始 pth 模型（作为泛化性能参考）
    
- 最终部署模型（hbm 模型）
    

如有需要，可补充 onnx / bc 模型的对比结果，但不作为主要结论依据。

## 7.4 精度判定原则

- 对比 pth 与 hbm 在测试集上的精度差异
    
- 若精度下降在可接受范围内，则模型可进入上线或交付阶段
    
- 若精度下降超出阈值，需回溯：
    
    - 量化策略
        
    - 模型结构
        
    - 前处理与输入格式设计