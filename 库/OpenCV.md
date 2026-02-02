# 1 整体概览

OpenCV 在 C++ 中大致可以分成几层：

- **数据结构层**：`cv::Mat`、`cv::Point`、`cv::Rect`、`cv::Size`、`cv::Scalar` 等
    
- **基础运算层**（core/imgproc）：矩阵运算、滤波、几何变换、颜色空间转换
    
- **算法层**（calib3d/features2d/dnn 等）：PnP、特征点、DNN 推理
    
- **工程支持层**：I/O、高效内存管理、多线程、安全传输（protobuf/zmq 等）
    

---

# 2 常用数据类型

## 2.1 `cv::Mat` —— 核心矩阵 / 图像容器

```
cv::Mat img;                        // 默认构造
cv::Mat img(h, w, CV_8UC3);         // 创建空图，3通道8位
cv::Mat img = cv::imread("xx.jpg"); // 从文件读取
```
关键属性：

```
int rows = img.rows;         // 高
int cols = img.cols;         // 宽
int type = img.type();       // CV_8UC3 / CV_32FC1 等
int channels = img.channels();
size_t step = img.step;      // 每行字节数
uchar* data = img.data;      // 原始像素指针
```
**拷贝语义：**

- 浅拷贝（共享数据）：
    
    `cv::Mat b = img;       // 只拷贝头，不拷贝像素`
    
- 深拷贝（独立一份数据）：
    
    `cv::Mat b = img.clone(); // 或 img.copyTo(b);`
---

## 2.2 几何基础类型

### 2.2.1 `cv::Point`, `cv::Point2f`, `cv::Point3f`

```
cv::Point2f p2(10.5f, 20.0f); 
cv::Point3f p3(0.0f, 0.0f, 1000.0f); 
```

### 2.2.2 `cv::Rect`（矩形框）

```
cv::Rect roi(50, 50, 200, 100); 
cv::Mat face = img(roi);    // ROI 子图（视图，共享 data）
```

### 2.2.3 `cv::Size`

```
cv::Size sz(640, 480); 
cv::Mat resized; 
cv::resize(img, resized, sz);
```

### 2.2.4 `cv::Scalar`（颜色 / 多通道标量）

`cv::Scalar green(0, 255, 0); // BGR：G 通道为 255`

---

## 2.3 数值 &特征向量

#### 2.3.1.1 `cv::Vec` 系列

```
cv::Vec3f v(1.0f, 2.0f, 3.0f); 
cv::Vec4b color(0, 255, 0, 255);
```

#### 2.3.1.2 `cv::Matx`（定长矩阵，适合小矩阵）

```
cv::Matx33f K( fx,  0, cx,
               0,  fy, cy,
               0,   0,  1 );

```

---

# 3 常用方法（按模块 & 数据类型）

## 3.1 I/O 与可视化：高频操作

### 3.1.1 图像读写：`cv::imread` / `cv::imwrite`

- **输入输出类型**：`cv::Mat`
    
```
cv::Mat img = cv::imread("a.jpg", cv::IMREAD_COLOR); 
cv::imwrite("result.jpg", img);
```

#### 3.1.1.1 颜色空间：`cv::cvtColor`

- **输入**：`cv::Mat`（必须有正确通道数）
    
- **输出**：`cv::Mat`
    

```
cv::Mat bgr, gray; 
cv::cvtColor(bgr, gray, cv::COLOR_BGR2GRAY);

```
> ⚠ 若输入是单通道，却用 `COLOR_BGR2GRAY`，会直接报错或产生未定义行为。

---

## 3.2 几何变换：`resize` / `warpAffine` / `warpPerspective`

#### 3.2.1.1 `cv::resize`

- **输入**：`cv::Mat src`
    
- **输出**：`cv::Mat dst`
    
- **匹配要求**：任意类型都可以，但需要注意插值方式
    

```
cv::Mat small; 
cv::resize(img, small, cv::Size(640, 360), 0, 0, cv::INTER_LINEAR);
```

- 若 `src` 和 `dst` 是同一个 Mat 且尺寸变化 → 会分配新 buffer，相当于深拷贝。
    
#### 3.2.1.2 `cv::warpAffine`

- **输入**：`cv::Mat src`, 2×3 仿射矩阵 `cv::Mat M`
    
- **适用**：旋转、平移、缩放、剪切
    

```
cv::Mat M = cv::getRotationMatrix2D(center, angle, scale); 
cv::warpAffine(src, dst, M, dstSize);
```

#### 3.2.1.3 `cv::warpPerspective`

- **输入**：3×3 单应矩阵 H
    
- **适用**：透视变换（车道线鸟瞰、平面映射）
    

---

## 3.3 图像处理（`imgproc` 核心）

#### 3.3.1.1 滤波：`GaussianBlur`、`medianBlur`

- **输入**：任意类型（常见 CV_8U / CV_32F）
    
- **输出**：同类型 Mat
    

`cv::GaussianBlur(img, blur, cv::Size(5,5), 1.5);`

#### 3.3.1.2 边缘检测：`Canny`

- **输入**：灰度图 `CV_8UC1`
    
- **输出**：二值边缘图 `CV_8UC1`
    

```
cv::Mat gray, edges; 
cv::cvtColor(img, gray, cv::COLOR_BGR2GRAY); 
cv::Canny(gray, edges, 50, 150);
```

---

## 3.4 绘制：可视化 

常用函数：`rectangle` / `circle` / `line` / `putText`

```
cv::rectangle(img, cv::Rect(100,100,200,150), cv::Scalar(0,255,0), 2);
cv::circle(img, cv::Point(50,50), 3, cv::Scalar(0,255,0), -1);
cv::putText(img, "Driver", cv::Point(100,90),
            cv::FONT_HERSHEY_SIMPLEX, 0.5, cv::Scalar(0,255,0), 1);
```

**数据要求：**

- 图像一般为 `CV_8UC3`（BGR）
    
- 坐标用 `cv::Point / Point2f`
    
- 颜色用 `cv::Scalar(b,g,r)`
    

---

## 3.5 相机模型与几何：`calib3d`

#### 3.5.1.1 内参矩阵 `cameraMatrix`（3×3）

类型推荐：`CV_64F` 或 `CV_32F`

```
cv::Mat K = (cv::Mat_<double>(3,3) << 
    fx, 0, cx,
    0, fy, cy,
    0,  0,  1);
```

#### 3.5.1.2 PnP：`solvePnP` / `solvePnPRansac`

- **输入：**
    
    - `std::vector<cv::Point3f> objectPoints`（3D 标准脸 / 标定板点）
        
    - `std::vector<cv::Point2f> imagePoints`（2D 像素坐标）
        
    - `cv::Mat cameraMatrix`（3×3）
        
- **输出：**
    
    - `cv::Mat rvec`（3×1 Rodrigues 向量）
        
    - `cv::Mat tvec`（3×1 平移）
        

```
cv::solvePnPRansac(objectPoints, imagePoints, cameraMatrix, cv::Mat(),
                   rvec, tvec, false, 100, 8.0, 0.99, inliers,
                   cv::SOLVEPNP_AP3P);

```

**必须匹配的条件：**

- `objectPoints.size() == imagePoints.size()`
    
- 至少 4 对点（AP3P 可以 3 对，但一般留冗余）
    
- 相机内参与图像坐标的单位一致
    

---

# 4 数据与方法匹配要点


## 4.1 颜色相关

| 函数                   | 输入类型      | 输出类型      | 备注        |
| -------------------- | --------- | --------- | --------- |
| `cvtColor(BGR→GRAY)` | `CV_8UC3` | `CV_8UC1` | 灰度预处理     |
| `cvtColor(RGB→BGR)`  | `CV_8UC3` | `CV_8UC3` | 某些模型用 RGB |

---

## 4.2 几何 & PnP

|函数|输入|类型要求|
|---|---|---|
|`solvePnP`|3D 点|`std::vector<cv::Point3f>`|
||2D 点|`std::vector<cv::Point2f>`|
||内参|`cv::Mat` 3×3, `CV_64F/32F`|

如果有自己的 `struct Point3D { float x,y,z; }`，需要先转换为 OpenCV 类型：

```
std::vector<cv::Point3f> objPts;
objPts.reserve(myPts.size());
for (auto& p : myPts) {
    objPts.emplace_back(p.x, p.y, p.z);
}
```

---

## 4.3 与 Eigen / Protobuf 的边界

- **Eigen ↔ OpenCV：**
    
    - 用 `cv::cv2eigen` / `cv::eigen2cv`（需 `opencv_contrib` / `opencv2/core/eigen.hpp`）
        
- **Protobuf ↔ OpenCV：**
    
    - 一般做法：
        
        - 图像：`cv::Mat` → `std::vector<uint8_t>` → bytes 字段
            
        - 几何点：`cv::Point2f` → message `{float x = 1; float y = 2;}`
            

---

# 5 工程实践关键点

## 5.1 深浅拷贝 & 性能

**规则：**

- 函数参数：
    
    - 若仅读 → `const cv::Mat&`
        
    - 若要写入结果 → `cv::Mat&` 或返回值
        
- 避免在频繁调用中无脑 `clone()`，必要时才深拷贝
    

示例：

```
// 好：只读
void Process(const cv::Mat& input, cv::Mat& output);

// 慎用：每次都会复制
void Process(cv::Mat input, cv::Mat& output);
```

---

## 5.2 多线程 + Mat

- `cv::Mat` 的引用计数是线程安全的（增加/减少引用不会崩），但**像素数据不是**。
    
- 多线程读同一 Mat → OK
    
- 多线程写同一 Mat → 必须 clone 或加锁
    

---

## 5.3 硬件 / 平台相关

- ARM / AArch64 上 OpenCV 大量使用 NEON SIMD
    
- 若自己写 NEON 内联或 intrinsics，要注意：
    
    - Mat 的对齐（一般 16 字节以上更友好）
        
    - 行 stride（step）不一定是紧致的
        

---

## 5.4 与 CMake 工程的集成

典型 CMake 片段：

```
find_package(OpenCV REQUIRED core imgproc highgui calib3d)

target_include_directories(my_target PRIVATE ${OpenCV_INCLUDE_DIRS})
target_link_libraries(my_target PRIVATE ${OpenCV_LIBS})
```

如果手动管理 `.so`

- `link_directories()` 指向 `lib-ubuntu22.04`
    
- `target_link_libraries()` 中显式列出：
    
    - `opencv_core`
        
    - `opencv_imgproc`
        
    - `opencv_highgui`
        
    - `opencv_calib3d`
        
    - `opencv_features2d` 等
        

---

