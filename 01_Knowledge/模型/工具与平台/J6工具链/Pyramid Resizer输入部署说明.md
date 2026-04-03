---
type: knowledge
status: verified
unit_type: integration_constraint
domain: 模型
topic: Pyramid Resizer输入部署说明
sources:
  - https://horizonrobotics.feishu.cn/wiki/VjZmwGb91iFqzuk7hXBcLGxinwe
scope: 适用于使用 Pyramid/Resizer 作为输入来源的 J6 模型部署场景。
risks: 仍保留 grid placeholder；部分输入格式约束与工具链版本强相关。
source_task: 评估并将 J6 工具链候选文档提升到知识库
evidence:
  - 来源文档：03_Inbox/J6EM_OE_Pyramid_Resizer输入部署说明-v2.3_对外.md
updated_at: 2026-03-30
---

摘要：说明 J6 Pyramid/Resizer 输入部署模型的输入格式、PTQ/QAT 编译、板端性能评测与部署要点。

# 引言
地平线芯片上，在图像输入节点前添加图像颜色空间转换处理可节省DDR带宽以获取更好的模型部署性能（通过BPU硬件支持了YUV420到YUV444的转换，并通过conv来完成YUV444到RGB/BGR的转换，以及归一化操作）。由于在图像通路上，通常Y、UV是独立的地址（Pyramid输出结果即为Y和UV两个独立地址），特别是对于在原图上Crop ROI区域时，Y、UV一定是非连续的，因此J6工具链将输入来源为Pyramid的模型输入直接定义为Y和UV两个Tensor，不再区分NV12和NV12_SEP两种类型，同时保障仿真模型的输入格式与板端部署模型的输入完全一致。下表是J5与J6平台各阶段模型的输入格式（部署时模型输入来源于Pyramid）对比：

<lark-table rows="4" cols="7" column-widths="82,119,119,119,100,100,89">

  <lark-tr>
    <lark-td rowspan="2">
      **计算平台**
    </lark-td>
    <lark-td rowspan="2">
      **原始浮点模型**
    </lark-td>
    <lark-td colspan="2">
      **量化模型**
    </lark-td>
    <lark-td colspan="2">
      **定点模型**
    </lark-td>
    <lark-td rowspan="2">
      **部署模型**
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      **PTQ**
    </lark-td>
    <lark-td>
      **QAT**
    </lark-td>
    <lark-td>
      **PTQ**
    </lark-td>
    <lark-td>
      **QAT**
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      **J6**
    </lark-td>
    <lark-td>
      RGB归一化后的Float32浮点数
    </lark-td>
    <lark-td>
      RGB归一化后的Float32浮点数
    </lark-td>
    <lark-td>
      RGB归一化后的Float32浮点数
    </lark-td>
    <lark-td>
      Y+UV
    </lark-td>
    <lark-td>
      Y+UV
    </lark-td>
    <lark-td>
      Y+UV
    </lark-td>
  </lark-tr>
  <lark-tr>
    <lark-td>
      **J5**
    </lark-td>
    <lark-td>
      RGB归一化后的Float32浮点数
    </lark-td>
    <lark-td>
      yuv444-128
    </lark-td>
    <lark-td>
      RGB归一化后的Float32浮点数
    </lark-td>
    <lark-td>
      yuv444-128
    </lark-td>
    <lark-td>
      yuv444-128
    </lark-td>
    <lark-td>
      NV12或者NV12_SEP
    </lark-td>
  </lark-tr>
</lark-table>

由上表可见，J6计算平台对于不同量化方式以及仿真与板端的输入格式一致性保持情况会更好，同时可简化用户做一致性验证的复杂性。模型开发阶段的前处理均和原始浮点模型保持一致（量化及模型转换），应用开发阶段（仿真及板端部署）的输入数据格式与SOC相关硬件输出格式保持一致。

# 示例
## PTQ编译
### 编译&可视化（batch1）
1. **yaml配置**
<grid cols="2">
  <column width="50">
    **Pyramid**
    ```python {wrap}
    input_parameters:
        input_type_rt: 'nv12'
        input_type_train: 'rgb'
        input_layout_train: 'NCHW'
        norm_type: 'data_mean_and_scale'
        mean_value: "123.675 116.28 103.53"
        scale_value: "0.01712475 0.017507 0.01742919"
    # input_type_rt 为 nv12 时 input_source 默认为pyramid
    ```

  </column>
  <column width="50">
    **Resizer**
    ```python {wrap}
    input_parameters:
        input_type_rt: 'nv12'
        input_type_train: 'rgb'
        input_layout_train: 'NCHW'
        norm_type: 'data_mean_and_scale'
        mean_value: "123.675 116.28 103.53"
        scale_value: "0.01712475 0.017507 0.01742919"
    compiler_parameters:
        # data为模型输入节点的名称
        input_source: {"data": "resizer"}
    ```

  </column>
</grid>

1. **可视化**
  1. `**hb_model_info -v xxx.hbm**`
  <grid cols="2">
    <column width="50">
      **Pyramid**
      ![](./Pyramid Resizer输入部署说明.assets/J6EM_OE_Pyramid_Resizer输入部署说明-v2.3_对外_image_001)

    </column>
    <column width="50">
      **Resizer**
      ![](./Pyramid Resizer输入部署说明.assets/J6EM_OE_Pyramid_Resizer输入部署说明-v2.3_对外_image_002)

    </column>
  </grid>

  <quote-container>
  -9223372036854775808占位表示该位置的数据为动态shape，pyramid输入的stirde为动态；resizer输入的H和W以及stride均为动态
  </quote-container>

  1. `**hrt_model_exec model_info --model_file xxx.hbm**`
<grid cols="2">
  <column width="50">
    **Pyramid**
    ![](./Pyramid Resizer输入部署说明.assets/J6EM_OE_Pyramid_Resizer输入部署说明-v2.3_对外_image_003)


  </column>
  <column width="50">
    **Resizer**
    ![](./Pyramid Resizer输入部署说明.assets/J6EM_OE_Pyramid_Resizer输入部署说明-v2.3_对外_image_004)

  </column>
</grid>

<quote-container>
-1占位表示该位置的数据为动态shape，pyramid输入的stride为动态；resizer输入的H和W以及stride均为动态
</quote-container>

由于nv12数据在内存中是二维存储的（一般数据在内存中均是1维连续存储），可以通过stride指定截取的原图范围，因此其stride信息是动态的。在J6平台上要求数据满足W32对齐（J5平台为W16对齐）。在此基础上，由于resizer输入与原图大小相关，因此resizer输入的模型shape（H、W）以及stride信息均为动态。
### 编译&可视化（batch n）
由于PTQ方案batchn Pyramid的支持方案还在设计中，因此用户暂时无法通过配置yaml文件中的相关参数直接编译出可上板推理的batchn Pyramid模型。**因此若您的模型输入shape第一维不等于1，请务必将input_type_train和input_type_rt参数配置为featuremap**。
若要使用PTQ方案，并希望部署时每个batch的数据可以来源于不同的内存地址，可先使用hb_compile工具生成`*ptq_model.onnx`之后通过如下代码将模型输入沿batch维度拆开，并插入前处理节点和格式转换节点：
```python {wrap}
import onnx
from hbdk4.compiler.onnx import export
from hbdk4.compiler import convert, compile, visualize, save

model_path = "mobilenetv1_224x224_nv12_ptq_model.onnx"
onnx_model = onnx.load(model_path)
model = export(onnx_model)
func = model.functions[0]

batch_input = ["input_name1"]   # 需要使用独立地址方式部署的输入节点名称列表
resizer_input = ["resize"]      # 部署时数据来源于resizer的输入节点名称列表
pyramid_input = ["pym"]         # 部署时数据来源于pyramid的输入节点名称列表

def channge_source(input, source):
    node = input.insert_transpose(permutes=[0, 3, 1, 2])
    node = node.insert_image_preprocess(mode=None, divisor=1, mean=[128, 128, 128], std=[128, 128, 128])
    if source == "pyramid":
        node.insert_image_convert("nv12")
    elif source == "resizer":
        node.insert_roi_resize("nv12")
# 为和历史版本保持兼容，建议使用flatten_inputs将输入展开，如下代码同时兼容新旧版本模型：
for input in func.flatten_inputs[::-1]:
    if input.name in batch_input:
        origin_name = input.name
        split_inputs = input.insert_split(dim=0)
        for split_input in reversed(split_inputs):
            if origin_name in pyramid_input:
                channge_source(split_input, "pyramid")
            elif origin_name in resizer_input:
                channge_source(split_input, "resizer")

quantized_model = convert(model, march="nash-m")
save(quantized_model, "mobilenetv1_224x224_nv12_quantized.bc")
```

随后，使用hb_compile工具，将yaml文件中的model路径改为quantized.bc的路径，完成删除节点和模型编译的过程。

## QAT编译
### 编译&可视化
先参考用户手册导出并保存qat.bc，然后参考如下代码编译部署模型：
```python
import torch
import torch.nn as nn
from hbdk4.compiler.torch import export
from hbdk4.compiler import load, compile, convert, March, visualize, hbm_perf


model = load("qat.bc")
func = model.functions[0]

batch_input = ["input_name1"]   # 需要使用独立地址方式部署的输入节点名称列表
resizer_input = ["resize"]      # 部署时数据来源于resizer的输入节点名称列表
pyramid_input = ["pym"]         # 部署时数据来源于pyramid的输入节点名称列表

def channge_source(input, source):
    node = input.insert_transpose(permutes=[0, 3, 1, 2])
    node = node.insert_image_preprocess(mode=None, divisor=1, mean=[128, 128, 128], std=[128, 128, 128])
    if source == "pyramid":
        node.insert_image_convert("nv12")
    elif source == "resizer":
        node.insert_roi_resize("nv12")
# 为和历史版本保持兼容，建议使用flatten_inputs将输入展开，如下代码同时兼容新旧版本模型：
for input in func.flatten_inputs[::-1]:
    if input.name in batch_input:
        origin_name = input.name
        split_inputs = input.insert_split(dim=0)
        for split_input in reversed(split_inputs):
            if origin_name in pyramid_input:
                channge_source(split_input, "pyramid")
            elif origin_name in resizer_input:
                channge_source(split_input, "resizer")

# 转定点
quantized_model = convert(model, "nash-m")
# visualize(quantized_model)
# 删除量化反量化节点
quantized_model[0].remove_io_op(op_types = ["Quantize", "Dequantize"])

# 模型编译及性能评测
hbm = compile(quantized_model, march="nash-m",path="test.hbm", debug=True, opt=2, jobs=40, progress_bar=True)
# hbm.visualize()
hbm_perf("test.hbm")
```


## 板端性能评测
由于Pyramid和Resizer模型中存在一些动态的属性，因此使用`hrt_model_exec perf`工具评测时需要指定一下这些属性：
<quote-container>
ps：为了提高用户评测效率，Pyramid模型可支持用户不提供动态参数的值（由工具依据模型实际尺寸计算最小对齐要求的参数大小），但是对于Resizer模型，roi大小不同会导致延时不一样，因此建议Resizer模型还是由用户指定输入数据和roi
```shell {wrap}
hrt_model_exec perf --model_file pyramid.hbm
hrt_model_exec perf --model_file resizer.hbm --input_file zebra_cls.jpg,zebra_cls.jpg,roi.txt --input_img_properties="Y,UV"
```

</quote-container>

<quote-container>
roi.txt（使用空格隔开：[left, top, right, bottom]，即roi的左上角坐标以及右下角坐标）：
```cpp {wrap}
0 0 200 200
```

</quote-container>

### Pyramid输入
stride计算方式（W32对齐）：
```cpp
// 假设tensor输入尺寸valid_shape=（1,112,112,2,），tensor_type=HB_DNN_TENSOR_TYPE_U8，stride= (-1,-1,2,1,)
// stride[3]=sizeof(tensor_type)                 -> 1
// stride[2]=stride[3]*valid_shape[3]            -> 2
// stride[1]=ALIGN_32(stride[2]*valid_shape[2])  -> ALIGN_32(2*112）=224
// stride[0]=stride[1]*valid_shape[1]            -> 224*112=25088

#define ALIGN_32(value) ((value + (32-1)) & ~(32-1))
```

perf命令（Pyramid输入的模型其stride为动态，可以不用指定，工具会自动计算）：
假设模型输入尺寸为Y=（1,224,224,1），UV=(1,112,112,2,)
```shell {wrap}
hrt_model_exec perf --model_file pyramid.hbm --input_stride="50176,224,1,1;25088,224,2,1"
```

### Resizer输入
由于Resizer输入的模型其stride以及valid_shape均为动态，且模型性能与roi参数相关，需要用户提供真实的推理数据和roi信息。若提供的Y和UV数据为jpg图像，则需要通过`input_img_properties`参数指定该图片需要处理成的数据格式。若指定的input_valid_shape与jpg图像尺寸不符，则工具会将原图resize至指定尺寸。
perf命令：
假设希望评测的是原图尺寸为HxW=300x300，ROI=（0,0,199,199）下的性能数据，则perf命令如下所示（valid_shape和stride可以不用指定，工具会自动计算，如果无需基于特定数据评测，则仅指定模型参数即可）：
```shell {wrap}
hrt_model_exec perf --model_file=mobilenetv1_224x224_resizer.hbm --input_file=1.jpg,1.jpg,roi.txt --input_img_properties=Y,UV --input_valid_shape="1,300,300,1;1,150,150,2" --input_stride="96000,320,1,1;48000,320,2,1"
```

roi.txt（使用空格隔开：[left, top, right, bottom]，即roi的左上角坐标以及右下角坐标）：
```cpp {wrap}
0 0 199 199
```


## 板端部署
OE包中的示例路径为：
Pyramid：OE/samples/ucp_tutorial/dnn/basic_samples/code/00_quick_start
Resizer：OE/samples/ucp_tutorial/dnn/basic_samples/code/01_api_tutorial/roi_infer
### 示例代码解析
#### Pyramid
pyramid模型的输入节点属性如下所示：
![](./Pyramid Resizer输入部署说明.assets/J6EM_OE_Pyramid_Resizer输入部署说明-v2.3_对外_image_005)

对应Y和UV两个输出，stride属性为动态，因此J5迁移J6需要关注输入数据的准备方式的区别（若使用的是Pyramid硬件的输出，则已经是经过W32对齐的数据，直接赋值给模型输入tensor即可；以下示例是读取jpg图像，使用opencv处理得到nv12数据并进行推理，用于说明如何计算pyramid数据的stride信息）：
##### main函数
J6 UCP新增加了`hbDNNInferV2`接口，该接口可根据输入参数创建同步/异步推理任务。对于异步任务，调用方可以跨函数、跨线程使用返回的 `taskHandle`。请注意该接口与J5推理接口在指定`ctrl_param`方面的区别。hbDNNInfer仅用于推理兼容模式的模型，关于兼容模式的模型说明具体请参考本文第三章。
```cpp
/**
 * Step1: get model handle
 * Step2: prepare input and output tensor
 * Step3: set input data to input tensor
 * Step4: run inference
 * Step5: do postprocess with output data
 * Step6: release resources
 */
int main(int argc, char **argv) {
  // Parsing command line arguments
  gflags::SetUsageMessage(argv[0]);
  gflags::ParseCommandLineFlags(&argc, &argv, true);
  std::cout << gflags::GetArgv() << std::endl;

  // Init logging
  hobot::hlog::HobotLog::Instance()->SetLogLevel(
      "DNN_BASIC_SAMPLE", hobot::hlog::LogLevel::log_info);

  hbDNNPackedHandle_t packed_dnn_handle;
  hbDNNHandle_t dnn_handle;
  const char **model_name_list;
  auto modelFileName = FLAGS_model_file.c_str();
  int model_count = 0;
  // Step1: get model handle
  {
    HB_CHECK_SUCCESS(
        hbDNNInitializeFromFiles(&packed_dnn_handle, &modelFileName, 1),
        "hbDNNInitializeFromFiles failed");
    HB_CHECK_SUCCESS(hbDNNGetModelNameList(&model_name_list, &model_count,
                                           packed_dnn_handle),
                     "hbDNNGetModelNameList failed");
    HB_CHECK_SUCCESS(
        hbDNNGetModelHandle(&dnn_handle, packed_dnn_handle, model_name_list[0]),
        "hbDNNGetModelHandle failed");
  }

  std::vector<hbDNNTensor> input_tensors;
  std::vector<hbDNNTensor> output_tensors;
  int input_count = 0;
  int output_count = 0;
  // Step2: prepare input and output tensor
  {
    HB_CHECK_SUCCESS(hbDNNGetInputCount(&input_count, dnn_handle),
                     "hbDNNGetInputCount failed");
    HB_CHECK_SUCCESS(hbDNNGetOutputCount(&output_count, dnn_handle),
                     "hbDNNGetOutputCount failed");
    input_tensors.resize(input_count);
    output_tensors.resize(output_count);
    prepare_tensor(input_tensors.data(), output_tensors.data(), dnn_handle);
  }

  // Step3: set input data to input tensor
  {
    // read a single picture for input_tensor[0], for multi_input model, you
    // should set other input data according to model input properties.
    HB_CHECK_SUCCESS(
        read_image_2_tensor_as_nv12(FLAGS_image_file, input_tensors.data()),
        "read_image_2_tensor_as_nv12 failed");
    LOGI("read image to tensor as nv12 success");
  }

  hbUCPTaskHandle_t task_handle{nullptr};
  hbDNNTensor *output = output_tensors.data();
  // Step4: run inference
  {
    // make sure memory data is flushed to DDR before inference
    for (int i = 0; i < input_count; i++) {
      hbUCPMemFlush(&input_tensors[i].sysMem, HB_SYS_MEM_CACHE_CLEAN);
    }

    // generate task handle
    HB_CHECK_SUCCESS(
        hbDNNInferV2(&task_handle, output, input_tensors.data(), dnn_handle),
        "hbDNNInferV2 failed");

    // submit task
    hbUCPSchedParam ctrl_param;
    HB_UCP_INITIALIZE_SCHED_PARAM(&ctrl_param);
    HB_CHECK_SUCCESS(hbUCPSubmitTask(task_handle, &ctrl_param),
                     "hbUCPSubmitTask failed");

    // wait task done
    HB_CHECK_SUCCESS(hbUCPWaitTaskDone(task_handle, 0),
                     "hbUCPWaitTaskDone failed");
  }

  // Step5: do postprocess with output data
  std::vector<Classification> top_k_cls;
  {
    // make sure CPU read data from DDR before using output tensor data
    for (int i = 0; i < output_count; i++) {
      hbUCPMemFlush(&output_tensors[i].sysMem, HB_SYS_MEM_CACHE_INVALIDATE);
    }

    get_topk_result(output, top_k_cls, FLAGS_top_k);
    for (int i = 0; i < FLAGS_top_k; i++) {
      LOGI("TOP {} result id: {}", i, top_k_cls[i].id);
    }
  }

  // Step6: release resources
  {
    // release task handle
    HB_CHECK_SUCCESS(hbUCPReleaseTask(task_handle), "hbUCPReleaseTask failed");
    // free input mem
    for (int i = 0; i < input_count; i++) {
      HB_CHECK_SUCCESS(hbUCPFree(&(input_tensors[i].sysMem)),
                       "hbUCPFree failed");
    }
    // free output mem
    for (int i = 0; i < output_count; i++) {
      HB_CHECK_SUCCESS(hbUCPFree(&(output_tensors[i].sysMem)),
                       "hbUCPFree failed");
    }
    // release model
    HB_CHECK_SUCCESS(hbDNNRelease(packed_dnn_handle), "hbDNNRelease failed");
  }

  return 0;
}
```

##### 准备nv12数据
前处理将jpg图像读入并处理成nv12格式，并按对齐要求将Y和UV数据分别赋给模型的两个输入节点。
```cpp
int32_t read_image_2_tensor_as_nv12(std::string &image_file,
                                    hbDNNTensor *input_tensor) {
  // the struct of input shape is NHWC
  int input_h = input_tensor[0].properties.validShape.dimensionSize[1];
  int input_w = input_tensor[0].properties.validShape.dimensionSize[2];

  cv::Mat bgr_mat = cv::imread(image_file, cv::IMREAD_COLOR);
  if (bgr_mat.empty()) {
    LOGE("image file not exist!");
    return -1;
  }
  // resize
  cv::Mat mat;
  mat.create(input_h, input_w, bgr_mat.type());
  cv::resize(bgr_mat, mat, mat.size(), 0, 0);
  // convert to YUV420
  if (input_h % 2 || input_w % 2) {
    LOGE("input img height and width must aligned by 2!");
    return -1;
  }
  cv::Mat yuv_mat;
  cv::cvtColor(mat, yuv_mat, cv::COLOR_BGR2YUV_I420);
  uint8_t *yuv_data = yuv_mat.ptr<uint8_t>();
  uint8_t *y_data_src = yuv_data;

  // copy y data
  uint8_t *y_data_dst =
      reinterpret_cast<uint8_t *>(input_tensor[0].sysMem.virAddr);
  for (int32_t h = 0; h < input_h; ++h) {
    memcpy(y_data_dst, y_data_src, input_w);
    y_data_src += input_w;
    // add padding
    y_data_dst += input_tensor[0].properties.stride[1];
  }

  // copy uv data
  int32_t uv_height = input_tensor[1].properties.validShape.dimensionSize[1];
  int32_t uv_width = input_tensor[1].properties.validShape.dimensionSize[2];
  uint8_t *uv_data_dst =
      reinterpret_cast<uint8_t *>(input_tensor[1].sysMem.virAddr);
  uint8_t *u_data_src = yuv_data + input_h * input_w;
  uint8_t *v_data_src = u_data_src + uv_height * uv_width;

  for (int32_t h = 0; h < uv_height; ++h) {
    auto *cur_data = uv_data_dst;
    for (int32_t w = 0; w < uv_width; ++w) {
      *cur_data++ = *u_data_src++;
      *cur_data++ = *v_data_src++;
    }
    // add padding
    uv_data_dst += input_tensor[1].properties.stride[1];
  }
  return 0;
}
```

##### 准备输入tensor
由于模型输入tensor的stride是动态的，因此推理前需要为模型输入节点指定正确的stride信息，并完成W32对齐的操作（J5为W16对齐）。同时依据对齐后的stride信息计算需要申请的内存空间大小
```cpp
#define ALIGN(value, alignment) (((value) + ((alignment)-1)) & ~((alignment)-1))
#define ALIGN_32(value) ALIGN(value, 32)

int prepare_tensor(hbDNNTensor *input_tensor, hbDNNTensor *output_tensor,
                   hbDNNHandle_t dnn_handle) {
  int input_count = 0;
  int output_count = 0;
  hbDNNGetInputCount(&input_count, dnn_handle);
  hbDNNGetOutputCount(&output_count, dnn_handle);

  /** Tips:
   * For input memory size in most cases:
   * *   input_memSize = input[i].properties.alignedByteSize
   * but here for dynamic stride of y and uv，alignedByteSize is not fixed
   * For output memory size:
   * *   output_memSize = output[i].properties.alignedByteSize
   */
  hbDNNTensor *input = input_tensor;
  for (int i = 0; i < input_count; i++) {
    HB_CHECK_SUCCESS(
        hbDNNGetInputTensorProperties(&input[i].properties, dnn_handle, i),
        "hbDNNGetInputTensorProperties failed");

    /** Tips:
     * For input tensor, usually need to pad the input data according to stride obtained from properties.
     * but here for dynamic stride of y and uv，user needs to specify a value which should be 32 bytes aligned for the -1 position in stride.
     * */
    auto dim_len = input[i].properties.validShape.numDimensions;
    for (int32_t dim_i = dim_len - 1; dim_i >= 0; --dim_i) {
      if (input[i].properties.stride[dim_i] == -1) {
        auto cur_stride =
            input[i].properties.stride[dim_i + 1] *
            input[i].properties.validShape.dimensionSize[dim_i + 1];
        input[i].properties.stride[dim_i] = ALIGN_32(cur_stride);
      }
    }

    int input_memSize = input[i].properties.stride[0] *
                        input[i].properties.validShape.dimensionSize[0];
    HB_CHECK_SUCCESS(hbUCPMallocCached(&input[i].sysMem, input_memSize, 0),
                     "hbUCPMallocCached failed");

    // Show how to get input name
    const char *input_name;
    HB_CHECK_SUCCESS(hbDNNGetInputName(&input_name, dnn_handle, i),
                     "hbDNNGetInputName failed");
    LOGI("input[{}] name is {}", i, input_name);
  }

  hbDNNTensor *output = output_tensor;
  for (int i = 0; i < output_count; i++) {
    HB_CHECK_SUCCESS(
        hbDNNGetOutputTensorProperties(&output[i].properties, dnn_handle, i),
        "hbDNNGetOutputTensorProperties failed");
    int output_memSize = output[i].properties.alignedByteSize;
    HB_CHECK_SUCCESS(hbUCPMallocCached(&output[i].sysMem, output_memSize, 0),
                     "hbUCPMallocCached failed");

    // Show how to get output name
    const char *output_name;
    HB_CHECK_SUCCESS(hbDNNGetOutputName(&output_name, dnn_handle, i),
                     "hbDNNGetOutputName failed");
    LOGI("output[{}] name is {}", i, output_name);
  }
  return 0;
}
```

#### Resizer
resizer模型的输入节点属性如下：
![](./Pyramid Resizer输入部署说明.assets/J6EM_OE_Pyramid_Resizer输入部署说明-v2.3_对外_image_006)

对应Y、UV以及Roi三个输入，其中Y和UV的shape和stride属性均为动态，J5迁移J6需要关注输入数据的准备方式的区别（若使用的是Pyramid硬件的输出，则已经是经过W32对齐的数据，直接赋值给模型输入tensor即可；以下示例是读取jpg图像，使用opencv处理得到nv12数据并进行推理，用于说明如何计算pyramid数据的stride信息）：
##### main函数
J6 UCP新增加了`hbDNNInferV2`接口，该接口可根据输入参数创建同步/异步推理任务。由于resizer输入的模型通常会有多组roi，推理通过连续创建任务，只提交一次的方案来实现，类似于J5 推理时的`more`功能。`hbDNNRoiInfer`以及`hbDNNRoiInferV2`仅用于推理兼容模式的模型，关于兼容模式的模型说明具体请参考本文第三章。
```cpp
int main(int argc, char **argv) {
  // Parsing command line arguments
  gflags::SetUsageMessage(argv[0]);
  gflags::ParseCommandLineFlags(&argc, &argv, true);
  std::cout << gflags::GetArgv() << std::endl;

  // Init logging
  hobot::hlog::HobotLog::Instance()->SetLogLevel(
      "DNN_BASIC_SAMPLE", static_cast<hobot::hlog::LogLevel>(FLAGS_log_level));

  // load model
  hbDNNPackedHandle_t packed_dnn_handle;
  hbDNNHandle_t dnn_handle;
  const char *model_file = FLAGS_model_file.c_str();
  const char **model_name_list;
  int model_count = 0;
  // Step1: get model handle
  {
    HB_CHECK_SUCCESS(
        hbDNNInitializeFromFiles(&packed_dnn_handle, &model_file, 1),
        "hbDNNInitializeFromFiles failed");

    HB_CHECK_SUCCESS(hbDNNGetModelNameList(&model_name_list, &model_count,
                                           packed_dnn_handle),
                     "hbDNNGetModelNameList failed");

    HB_CHECK_SUCCESS(
        hbDNNGetModelHandle(&dnn_handle, packed_dnn_handle, model_name_list[0]),
        "hbDNNGetModelHandle failed");
  }

  // Step2: set input data to nv12
  // In the sample, since the input is a same image, can allocate a memory for
  // reusing. image_mems is to save image data for y and uv.
  std::vector<hbUCPSysMem> image_mems(2);
  // image input size
  int input_h = 0;
  int input_w = 0;
  {
    // read a single picture, for multi_input model, you
    // should set other input data according to model input properties.
    HB_CHECK_SUCCESS(
        read_image_2_nv12(FLAGS_image_file, image_mems, input_h, input_w),
        "read_image_2_nv12 failed");
    LOGI("read image to nv12 success");
  }

  // Step3: prepare roi mem
  /**
   * Suppose to infer 2 roi tasks of data, the number of ROIs to be prepared is
   * also 2.
   */

  // left = 6, top = 12, right = 253, bottom = 253
  hbDNNRoi roi_1 = {6, 12, 253, 253};
  // left = 18, top = 24, right = 253, bottom = 251
  hbDNNRoi roi_2 = {18, 24, 253, 251};

  std::vector<hbDNNRoi> rois;
  rois.push_back(roi_1);
  rois.push_back(roi_2);
  int roi_num = 2;
  std::vector<hbUCPSysMem> roi_mems(2);
  prepare_roi_mem(rois, roi_mems);

  // Step4: prepare input and output tensor
  std::vector<std::vector<hbDNNTensor>> input_tensors(roi_num);
  std::vector<std::vector<hbDNNTensor>> output_tensors(roi_num);

  for (int i = 0; i < roi_num; ++i) {
    // prepare input tensor
    int input_count = 0;
    HB_CHECK_SUCCESS(hbDNNGetInputCount(&input_count, dnn_handle),
                     "hbDNNGetInputCount failed");
    input_tensors[i].resize(input_count);
    // prepare image tensor

    /** Tips:
     * In the sample, all tasks use the same image, so allocate memory to
     * save image. all input tensor can reuse the memory. if your model has
     * different input image, please allocate different memory for all inputs.
     * */
    HB_CHECK_SUCCESS(prepare_image_tensor(image_mems, input_h, input_w,
                                          dnn_handle, input_tensors[i]),
                     "prepare_image_tensor failed");

    auto roi_tensor_id = 2;
    HB_CHECK_SUCCESS(prepare_roi_tensor(&roi_mems[i], dnn_handle, roi_tensor_id,
                                        &input_tensors[i][roi_tensor_id]),
                     "prepare_roi_tensor failed");
    LOGI("prepare input tensor success");

    // prepare output tensor
    int output_count = 0;
    HB_CHECK_SUCCESS(hbDNNGetOutputCount(&output_count, dnn_handle),
                     "hbDNNGetInputCount failed");
    output_tensors[i].resize(output_count);
    HB_CHECK_SUCCESS(prepare_output_tensor(dnn_handle, output_tensors[i]),
                     "prepare_output_tensor failed");
    LOGI("prepare output tensor success");
  }

  // Step5: run inference
  hbUCPTaskHandle_t task_handle{nullptr};
  {
    /** Tips:
     * In the sample, submit multiple tasks at the same time
     * when taskHandle is nullptr, here create a new task，and
     * when taskHandle is created but not submitted yet, attach new task to the previous which represents multi model task
     * */
    for (int i = 0; i < roi_num; ++i) {
      HB_CHECK_SUCCESS(hbDNNInferV2(&task_handle, output_tensors[i].data(),
                                    input_tensors[i].data(), dnn_handle),
                       "hbDNNInferV2 failed");
    }

    // submit multi tasks
    hbUCPSchedParam infer_ctrl_param;
    HB_UCP_INITIALIZE_SCHED_PARAM(&infer_ctrl_param);
    HB_CHECK_SUCCESS(hbUCPSubmitTask(task_handle, &infer_ctrl_param),
                     "hbUCPSubmitTask failed");
    // wait task done
    HB_CHECK_SUCCESS(hbUCPWaitTaskDone(task_handle, 0),
                     "hbUCPWaitTaskDone failed");
  }

  // Step6: do postprocess with output data for every task
  for (int i = 0; i < roi_num; ++i) {
    HB_CHECK_SUCCESS(post_process(output_tensors[i], FLAGS_top_k, i),
                     "do post process failed");
  }

  // Step7: release resources
  {
    // release task handle
    HB_CHECK_SUCCESS(hbUCPReleaseTask(task_handle), "hbUCPReleaseTaskfailed");

    // free input mem
    for (auto &mem : image_mems) {
      HB_CHECK_SUCCESS(hbUCPFree(&mem), "hbUCPFree failed");
    }
    for (auto &mem : roi_mems) {
      HB_CHECK_SUCCESS(hbUCPFree(&mem), "hbUCPFree failed");
    }

    // free output mem
    for (auto &tensors : output_tensors) {
      for (auto &tensor : tensors) {
        HB_CHECK_SUCCESS(hbUCPFree(&(tensor.sysMem)), "hbUCPFree failed");
      }
    }

    // release model
    HB_CHECK_SUCCESS(hbDNNRelease(packed_dnn_handle), "hbDNNReleasefailed");
  }

  return 0;
}
```

##### 准备nv12数据
前处理将jpg图像读入并处理成nv12格式，并按对齐要求将Y和UV数据分别赋给模型的Y和UV两个输入节点。
```cpp
int read_image_2_nv12(std::string &image_file,
                      std::vector<hbUCPSysMem> &image_mem, int &input_h,
                      int &input_w) {
  cv::Mat bgr_mat = cv::imread(image_file, cv::IMREAD_COLOR);
  if (bgr_mat.empty()) {
    LOGE("image file not exist!");
    return -1;
  }

  input_h = bgr_mat.rows;
  input_w = bgr_mat.cols;

  // convert to YUV420
  if (input_h % 2 || input_w % 2) {
    LOGE("input img height and width must aligned by 2!");
    return -1;
  }
  cv::Mat yuv_mat;
  cv::cvtColor(bgr_mat, yuv_mat, cv::COLOR_BGR2YUV_I420);
  uint8_t *nv12_data = yuv_mat.ptr<uint8_t>();

  // Save cv::Mat into sysMem, so here need a memcpy operator.
  // And here should be 32 bytes aligned for y and uv data

  // copy y data
  auto w_stride = ALIGN_32(input_w);
  int32_t y_mem_size = input_h * w_stride;
  HB_CHECK_SUCCESS(hbUCPMallocCached(&image_mem[0], y_mem_size, 0),
                   "hbUCPMallocCached failed");
  uint8_t *y_data_dst = reinterpret_cast<uint8_t *>(image_mem[0].virAddr);
  uint8_t *y_data_src = nv12_data;
  for (int32_t h = 0; h < input_h; ++h) {
    memcpy(y_data_dst, y_data_src, input_w);
    y_data_src += input_w;
    // add padding
    y_data_dst += w_stride;
  }

  // copy uv data
  int32_t uv_height = input_h / 2;
  int32_t uv_width = input_w / 2;
  int32_t uv_mem_size = uv_height * w_stride;
  HB_CHECK_SUCCESS(hbUCPMallocCached(&image_mem[1], uv_mem_size, 0),
                   "hbUCPMallocCached failed");
  uint8_t *uv_data_dst = reinterpret_cast<uint8_t *>(image_mem[1].virAddr);
  uint8_t *u_data_src = nv12_data + input_h * input_w;
  uint8_t *v_data_src = u_data_src + uv_height * uv_width;

  for (int32_t h = 0; h < uv_height; ++h) {
    auto *cur_data = uv_data_dst;
    for (int32_t w = 0; w < uv_width; ++w) {
      *cur_data++ = *u_data_src++;
      *cur_data++ = *v_data_src++;
    }
    // add padding
    uv_data_dst += w_stride;
  }

  // make sure cahced mem data is flushed to DDR before inference
  hbUCPMemFlush(&image_mem[0], HB_SYS_MEM_CACHE_CLEAN);
  hbUCPMemFlush(&image_mem[1], HB_SYS_MEM_CACHE_CLEAN);
  return 0;
}
```

##### 准备输入tensor
由于resizer输入的Y以及UV的H和W也是动态的，需要在推理前将其设置为原图尺寸，并计算满足W32对齐的stride参数。请注意roi是模型的输入节点也需要为其进行赋值，不再作为一个推理参数。
```cpp
#define ALIGN(value, alignment) (((value) + ((alignment)-1)) & ~((alignment)-1))
#define ALIGN_32(value) ALIGN(value, 32)

int prepare_image_tensor(const std::vector<hbUCPSysMem> &image_mem, int input_h,
                         int input_w, hbDNNHandle_t dnn_handle,
                         std::vector<hbDNNTensor> &input_tensor) {
  // y and uv tensor
  for (int i = 0; i < 2; i++) {
    HB_CHECK_SUCCESS(hbDNNGetInputTensorProperties(&input_tensor[i].properties,
                                                   dnn_handle, i),
                     "hbDNNGetInputTensorProperties failed");
    input_tensor[i].sysMem = image_mem[i];

    /** Tips:
     * roi model should modify input valid shape to input image shape.
     * here the struct of y/uv shape is NHWC
     * */
    input_tensor[i].properties.validShape.dimensionSize[1] = input_h;
    input_tensor[i].properties.validShape.dimensionSize[2] = input_w;
    if (i == 1) {
      // uv input
      input_tensor[i].properties.validShape.dimensionSize[1] /= 2;
      input_tensor[i].properties.validShape.dimensionSize[2] /= 2;
    }

    /** Tips:
     * For input tensor, stride should be set according to real padding
     * of the user's data. And 32 bytes alignment is the requirement of y/uv
     * */
    input_tensor[i].properties.stride[1] =
        ALIGN_32(input_tensor[i].properties.stride[2] *
                 input_tensor[i].properties.validShape.dimensionSize[2]);
    input_tensor[i].properties.stride[0] =
        input_tensor[i].properties.stride[1] *
        input_tensor[i].properties.validShape.dimensionSize[1];
  }

  return 0;
}

int prepare_roi_tensor(const hbUCPSysMem *roi_mem, hbDNNHandle_t dnn_handle,
                       int32_t roi_tensor_id, hbDNNTensor *roi_tensor) {
  HB_CHECK_SUCCESS(hbDNNGetInputTensorProperties(&roi_tensor->properties,
                                                 dnn_handle, roi_tensor_id),
                   "hbDNNGetInputTensorProperties failed");

  roi_tensor->sysMem = *roi_mem;
  return 0;
}

int prepare_roi_mem(const std::vector<hbDNNRoi> &rois,
                    std::vector<hbUCPSysMem> &roi_mem) {
  auto roi_size = rois.size();
  roi_mem.resize(roi_size);
  for (auto i = 0; i < roi_size; ++i) {
    int32_t mem_size = 4 * sizeof(int32_t);
    HB_CHECK_SUCCESS(hbUCPMallocCached(&roi_mem[i], mem_size, 0),
                     "hbUCPMallocCached failed");
    int32_t *roi_data = reinterpret_cast<int32_t *>(roi_mem[i].virAddr);
    // The order of filling in the corner points of roi tensor is left, top, right, bottom
    roi_data[0] = rois[i].left;
    roi_data[1] = rois[i].top;
    roi_data[2] = rois[i].right;
    roi_data[3] = rois[i].bottom;
    // make sure cahced mem data is flushed to DDR before inference
    hbUCPMemFlush(&roi_mem[i], HB_SYS_MEM_CACHE_CLEAN);
  }
  return 0;
}
```


