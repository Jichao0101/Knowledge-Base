# 1 Tensor 基础（形状、dtype、device）

```
import torch  x = torch.randn(2, 3, 224, 224)          # NCHW 
x = x.float()                             # dtype 
x = x.to("cuda") if torch.cuda.is_available() else x  
print(x.shape, x.dtype, x.device)
```

常见注意点：

- **深度学习视觉任务基本默认 NCHW**（batch, channel, height, width）
    
- **模型权重多为 float32 / float16（AMP）**
    
- CPU ↔ GPU 频繁搬运非常贵：尽量把前后处理流程组织好，减少来回 `.cpu()` / `.cuda()`
    

---
# 2 Dataset / DataLoader（数据管道）

```
from torch.utils.data import Dataset, DataLoader

class MyDataset(Dataset):
    def __init__(self, items):
        self.items = items

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        # 返回 (input_tensor, label)
        return self.items[idx]

ds = MyDataset(items=[(torch.randn(3,224,224), 0) for _ in range(100)])
dl = DataLoader(ds, batch_size=8, shuffle=True, num_workers=4, pin_memory=True)

for xb, yb in dl:
    # pin_memory=True 时，配合 non_blocking=True 可更快搬运到 GPU
    xb = xb.to("cuda", non_blocking=True)
    yb = torch.tensor(yb).to("cuda", non_blocking=True)

```

建议：

- `num_workers`：Linux 下可开到 CPU 核数的一部分（例如 4~8），Windows/WSL2 视情况调
    
- `pin_memory=True`：训练/推理走 GPU 时一般更快
    

---

## 2.1 模型、损失、优化器（训练最小闭环）

```
import torch
import torch.nn as nn
import torch.optim as optim

model = nn.Sequential(
    nn.Conv2d(3, 16, 3, padding=1),
    nn.ReLU(),
    nn.AdaptiveAvgPool2d(1),
    nn.Flatten(),
    nn.Linear(16, 10),
).to("cuda")

criterion = nn.CrossEntropyLoss()
optimizer = optim.AdamW(model.parameters(), lr=1e-3)

model.train()
for step in range(100):
    xb = torch.randn(8,3,224,224, device="cuda")
    yb = torch.randint(0,10,(8,), device="cuda")

    optimizer.zero_grad(set_to_none=True)
    logits = model(xb)
    loss = criterion(logits, yb)
    loss.backward()
    optimizer.step()

```

---

## 2.2 推理（eval / no_grad / autocast）

```
model.eval()
with torch.no_grad():
    x = torch.randn(1,3,224,224, device="cuda")
    y = model(x)
```
混合精度（GPU 推理常用）：

```
from torch.cuda.amp import autocast

model.eval()
with torch.no_grad(), autocast(dtype=torch.float16):
    x = torch.randn(1,3,224,224, device="cuda")
    y = model(x)

```

---

## 2.3 保存与加载权重

```
# 保存
torch.save(model.state_dict(), "model.pt")

# 加载
model2 = model.__class__()  # 示意，实际要按真实结构构建
model2.load_state_dict(torch.load("model.pt", map_location="cpu"))

```

工程化建议：

- 保存 **state_dict**（更稳）
    
- 同时保存 config（输入尺寸、类别数、mean/std、label map），避免“权重能加载但不知道怎么用”
    

---

## 2.4 常用调试技巧

```
# 梯度是否爆炸/为 NaN
for n, p in model.named_parameters():
    if p.grad is not None and torch.isnan(p.grad).any():
        print("NaN grad:", n)

# 检查张量范围
print(x.min().item(), x.max().item(), x.mean().item())

```