# 1 Conda 是什么

**Conda** 是一个**跨平台的包管理 + 环境管理工具**，核心目标只有两点：

1. **隔离环境**
    
    - 不同项目用不同 Python 版本
        
    - 不同项目依赖互不污染
        
2. **统一管理依赖**
    
    - 不只管理 Python 包
        
    - 还能管理 C/C++ 库（如 `opencv`、`cuda`、`cudnn`、`ffmpeg`）
        

一句工程化理解：

> Conda = Python + 第三方库 + 运行环境的“容器级”管理器（比 virtualenv 更重，但也更稳）

---

## 1.1 Conda 家族成员

| 工具                          | 特点          | 适合场景      |
| --------------------------- | ----------- | --------- |
| **Anaconda**                | 全家桶（几 GB）   | 新手 / 数据分析 |
| **Miniconda**               | 最小安装（推荐）    | 工程师       |
| **Mambaforge / Micromamba** | conda 的高速实现 | CI / 服务器  |


---

# 2 安装 Conda

## 2.1 Linux / WSL 安装

```
# 下载（此处的是base环境的python版本）
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# 安装
bash ~/Miniconda3-latest-Linux-x86_64.sh
```
完成后：

`source ~/.bashrc conda --version`


---

# 3 Conda 的核心概念

## 3.1 环境（Environment）

每个环境包含：

- Python 解释器
    
- 独立的 `site-packages`
    
- 独立的 C/C++ 动态库
    

环境 ≈ **轻量虚拟机**

---

## 3.2 常用 Conda 指令

### 3.2.1 查看与配置

```
conda --version            # 查看版本 
conda info                 # 查看系统与环境信息
conda config --show        # 查看配置 
conda config --show channels
```
---

## 3.3 环境管理

### 3.3.1 创建环境

`conda create -n myenv python=3.10`

指定多个包：

`conda create -n det python=3.9 numpy opencv`

### 3.3.2 激活 / 退出

```
conda activate myenv 
conda deactivate
```

### 3.3.3 查看环境

`conda env list # 或 conda info --envs`

### 3.3.4 删除环境

`conda remove -n myenv --all`

---

## 3.4 包管理

### 3.4.1 安装包

```
conda install numpy 
conda install pytorch torchvision -c pytorch
```

指定版本：

`conda install numpy=1.26`

### 3.4.2 卸载包

`conda remove numpy`

### 3.4.3 查看已安装包

```
conda list 
conda list | grep torch
```

---

### 3.4.4 conda + pip 混用（工程常态）

**原则**：

> 能 conda 装的，优先 conda  
> conda 没有的，再用 pip

示例：

```
conda install numpy opencv 
pip install labelme
```

查看 pip 装的包：

`pip list`

---

## 3.5 Channel（软件源）

### 3.5.1 常见 Channel

|Channel|用途|
|---|---|
|defaults|官方源|
|conda-forge|社区源（强烈推荐）|
|pytorch|PyTorch 官方|

### 3.5.2 添加 conda-forge（工程必做）

```
conda config --add channels conda-forge
conda config --set channel_priority strict

```
---

## 3.6 导出与复现环境

### 3.6.1 导出环境

`conda env export > env.yaml`

### 3.6.2 根据文件创建环境

`conda env create -f env.yaml`

或重命名：

`conda env create -f env.yaml -n newenv`

---

## 3.7 Conda 与 Python venv / Docker 的关系

| 工具                | 适用场景               |
| ----------------- | ------------------ |
| venv / virtualenv | 纯 Python、轻量        |
| conda             | ML / CV / C++ 依赖复杂 |
| Docker            | 交付 / 线上部署          |

工程现实是：

> 本地开发：conda  
> 线上部署：Docker（Docker 里仍可能用 conda）

---

## 3.8 常见问题与坑

### 3.8.1 conda 很慢

mamba = 用 C++ 重写 solver 的 conda， 是conda 的“高速求解器 + 前端替身

```
conda install mamba -n base -c conda-forge
mamba install xxx
```
---

## 3.9 推荐的工程环境命名规范
```
cv_det_py39
dms_train_py310
slam_tools_py38

```

---