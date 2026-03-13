# 1 整体架构

统一计算平台（Unify Compute Platform）定义了一套统一的异构编程接口，将SOC上的功能硬件抽象出来并进行封装，对外提供基于功能的API，用于创建相应的UCP任务，并支持设置硬件Backend提交至UCP调度器，提供功能：
- 视觉处理(Vision Process)
- 神经网络模型推理（Neural Network）
- 高性能计算库（High Performance Library）
- 自定义算子插件开发

# 2 视觉处理

vp模块主要用于模型的前后处理环节，将图像处理相关的硬件调用进行了封装，通过设置backend来选择不同的硬件方案（若不指定backend，UCP会自动适配负载更低的处理单元）

## 2.1 功能架构

- 应用层
	- remap
	- resize
	- transpose
	- roi resize
	- warp affine
	- pyrdown
	- codec
- 系统层
	- 服务
		- task management
		- session management
		- graph management
		- engine management
	- 硬件驱动
		- dsp
		- stitch
		- gdc
		- jpu
		- vpu
		- pyramid
		- isp

# 3 模型推理

## 3.1 tensor内部布局对齐

BPU对数据有对齐限制。有效数据排布和对齐数据排布用 `hbDNNTensorProperties` 中的 `validShape` 和 `stride` 表示。

- `validShape` 是有效数据的shape。
- `stride[i]` 表示 移动1单位该维度需要跳过的byte数

### 3.1.1 contiguous layout（软件自然布局）

内存排列：
```
[C][H][W] 紧密排列
每行:
212 * element_size

```

没有空洞，没有padding。

优点：

- 内存占用最小
    
- CPU访问友好
    
- numpy / pytorch 默认布局
    

缺点：

- 不满足硬件DMA和SIMD最优访问条件

### 3.1.2 stride + padding layout（BPU布局）

W维对齐到224：

`[C][H][224]`

真实数据212，剩余12是padding。

stride示例：

```
stride[3] = element_size 
stride[2] = 224 * element_size 
stride[1] = 224 * 224 * element_size 
stride[0] = C * stride[1]
```

优点：

- 每行大小是硬件友好的对齐长度
    
- DMA可以满速传输
    
- SIMD可以满宽执行
    

缺点：

- 内存占用增加
    
- 有padding

## 3.2 tensor起始地址对齐

BPU对模型输入输出内存首地址有对齐限制，要求输入与输出内存的首地址 `32` 或者 `64` 对齐，tensor base address alignment

示例：

```
base addr = 0x10000000   ✓ (64 aligned) 
base addr = 0x10000020   ✓ (32 aligned) 
base addr = 0x10000003   ✗
```

保证DMA可以直接访问tensor起点。

否则：

- DMA必须拆成多个访问
    
- 或直接非法

## 3.3 模型推理工具

1. 获取模型信息
```
hrt_model_exec model_info --model_file=xxx.hbm
```

2. 模型推理
```
hrt_model_exec infer --model_file=xxx.hbm --input_file=xxx.bin
```

3. 模型性能分析
```
hrt_model_exec perf --model_file=xxx.hbm
```

# 4 高性能算子库

## 4.1 功能架构

- 应用
	- fft
	- ifft
- 系统
	- 服务
		- task management
		- session management
		- graph management
		- engine management
	- 硬件
		- dsp