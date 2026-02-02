# 1 简介

**NEON** 是 ARMv7/ARMv8-A 上的 **SIMD（Single Instruction, Multiple Data）向量扩展**，主要用于：

- 向量化的 **整数 / 浮点** 运算
    
- 多媒体处理：图像、音频、视频
    
- 信号处理、数值计算
    
- 深度学习推理中的卷积、GEMM、点积等
    

核心思想：

> 一条指令同时处理多份数据（多通道 / 多 lanes），显著提升吞吐。

在 AArch64（Cortex-A）上，NEON 与标量浮点共享同一套向量寄存器。

---

# 2 向量寄存器与数据通道

## 2.1 寄存器布局

以 **AArch64 的 Cortex-A** 为例：

- 向量寄存器：`v0 ~ v31` 共 32 个
    
- 每个寄存器宽度：**128 bit = 16 字节**
    
- 同时承担两个角色：
    
    1. 标量浮点寄存器（`S`/`D` 形式）
        
    2. NEON SIMD 向量寄存器（`8B/16B/4H/8H/4S/2D` 形式）
        

标量视角（别名）：

- `S0` / `D0` 等：访问 `v0` 的低 32/64 bit
    
- 标量浮点指令操作这些 `S`/`D`，本质上仍在用 `v` 寄存器。
    

向量视角：

- `V0.4S` → 把 v0 看成 4 个 32-bit 元素
    
- `V0.16B` → 把 v0 看成 16 个 8-bit 元素
    

---

## 2.2 通道数（lanes）

128-bit 寄存器可以按不同元素宽度切分为多通道：

|元素类型|每元素 bit 数|每寄存器元素数（通道数）|常用类型（C intrinsics）|
|---|---|---|---|
|`float32` / `int32`|32|4|`float32x4_t` / `int32x4_t`|
|`int16` / `uint16`|16|8|`int16x8_t`|
|`int8` / `uint8`|8|16|`int8x16_t`|
|`float64` / `int64`|64|2|`float64x2_t`|

**SIMD 并行**：

- `vaddq_f32(a, b)`：一次对 **4 个 float32** 做加法
    
- `vaddq_s16(a, b)`：一次对 **8 个 int16** 做加法
    
- `vaddq_u8(a, b)`：一次对 **16 个 uint8** 做加法
    

> 一条 NEON 指令 = 对一个向量寄存器中的所有 lanes **锁步执行同一运算**。

---

# 3 编程方式

## 3.1 自动矢量化（auto-vectorization）

编译器自动将标量循环转成 NEON 指令：

`for (int i = 0; i < N; ++i) {     c[i] = a[i] + b[i]; }`

在开启优化（`-O3 -ftree-vectorize` / `-Ofast`）并指定目标（如 `-mcpu=cortex-a76`）时，编译器可能自动生成：

- `LD1` / `FADD V?.4S` / `ST1` 等 NEON 指令
    

优点：

- 无需手写 intrinsics
    
- 代码可读性高
    

缺点：

- 是否矢量化 **不可控**
    
- 在访问复杂、分支多、alias 不清晰时，编译器会放弃或产生低质量代码
    

适合：

- 简单的数值循环
    
- 非极限性能路径
    

---

## 3.2 NEON intrinsics

C/C++ 层直接调用 NEON 函数，映射为对应指令：

```
#include <arm_neon.h>

void vec_add(const float* a, const float* b, float* c, int n) {
    int i = 0;
    for (; i + 4 <= n; i += 4) {
        float32x4_t va = vld1q_f32(a + i);
        float32x4_t vb = vld1q_f32(b + i);
        float32x4_t vc = vaddq_f32(va, vb);
        vst1q_f32(c + i, vc);
    }
    for (; i < n; ++i) {
        c[i] = a[i] + b[i];
    }
}

```

特点：

- **一一对应** NEON 指令，行为确定
    
- 可精细控制：
    
    - load/store 模式
        
    - 运算顺序
        
    - unroll 程度
        
- 性能上限高，适合热点算子（GEMM/Conv/点云处理）
    

---

### 3.2.1 手写汇编（inline asm / .S）

在极端性能场景，可以直接写 AArch64 + NEON 汇编：

`; V0.4S = V1.4S + V2.4S FADD   V0.4S, V1.4S, V2.4S`

但一般只有在：

- 编译器寄存器分配不理想
    
- 需要复杂 schedule / 指令重排
    
- intrinsics 无法表达某些细粒度控制
    

时才考虑，维护成本极高。

---

## 3.3 常用 NEON 数据类型与操作

### 3.3.1 C intrinsics 类型

头文件：`<arm_neon.h>`

常见向量类型示例：

```
// 整数
int8x16_t   v_int8;   // 16 x int8
uint8x16_t  v_uint8;  // 16 x uint8
int16x8_t   v_int16;  // 8 x int16
int32x4_t   v_int32;  // 4 x int32

// 浮点
float32x4_t v_f32;    // 4 x float32
float64x2_t v_f64;    // 2 x float64 (在支持 double NEON 的核上)

```

---

### 3.3.2 加载与存储

```
float32x4_t vld1q_f32(const float32_t* ptr);  // 向量加载
void        vst1q_f32(float32_t* ptr, float32x4_t val); // 存储

```
注意：

- 推荐数据起始地址 **16 字节对齐**（SIMD 边界）
    
- 若配合 cache line 优化，进一步确保 **64 字节对齐**
    

---

### 3.3.3 算术运算

```
float32x4_t vaddq_f32(float32x4_t a, float32x4_t b);
float32x4_t vsubq_f32(float32x4_t a, float32x4_t b);
float32x4_t vmulq_f32(float32x4_t a, float32x4_t b);

// FMA（部分架构支持）
float32x4_t vfmaq_f32(float32x4_t acc, float32x4_t a, float32x4_t b);
// acc = acc + a * b

```

整数版本：

```
int16x8_t vaddq_s16(int16x8_t a, int16x8_t b);
int16x8_t vsubq_s16(int16x8_t a, int16x8_t b);
int16x8_t vmulq_s16(int16x8_t a, int16x8_t b);

```

---

### 3.3.4 比较与掩码

```
uint32x4_t vcltq_f32(float32x4_t a, float32x4_t b); // a < b
uint32x4_t vcgtq_f32(float32x4_t a, float32x4_t b); // a > b
uint32x4_t vceqq_f32(float32x4_t a, float32x4_t b); // a == b

// 结果是掩码向量，可配合位运算 / 选择使用
```
---

### 3.3.5 混合、重排（shuffle / zip / unzip）

用于重排通道、打包/解包数据：

```
int16x8x2_t vzipq_s16(int16x8_t a, int16x8_t b);   // 交错合并
int16x8x2_t vuzpq_s16(int16x8_t a, int16x8_t b);   // 解交错
int8x16_t   vextq_s8(int8x16_t a, int8x16_t b, const int imm); // 串接并截取

```

在矩阵/卷积/点云等场景中常用于：

- **打包（pack）权重 / 特征图**

---
