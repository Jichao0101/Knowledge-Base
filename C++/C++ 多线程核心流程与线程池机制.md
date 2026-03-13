
# 1 多线程核心目标

多线程解决的本质问题：

`让多个任务并发执行，提高CPU利用率和吞吐量`

单线程：

`Task A → Task B → Task C`


多线程：

```
Thread1: Task A
Thread2: Task B
Thread3: Task C
```

实现并行执行

---

# 2 多线程核心流程总览

完整流程：

```
1. 定义任务
2. 提交任务（Commit）
3. 任务进入队列
4. worker线程等待任务
5. worker线程被唤醒
6. worker线程执行任务
7. 结果写入future
8. future获取结果
9. 任务生命周期结束
```

对应时序图：

```
主线程                任务队列              worker线程

定义任务
   │
提交Commit()
   │
   ├── push(task) ─────→ queue               |
   │                                       wait()
   ├── notify_one()
   │                                         │
   │                                   
   │                                         │
   │                                       wake up
   │                                         │
   │                                      pop task
   │                                         │
   │                                     execute task
   │                                         │
future.get()              ←────          result ready

```

---


# 3 多线程核心组件关系图

```
           ThreadPool

        ┌─────────────┐
        │ task queue  │
        └──────┬──────┘
               │
        notify_one()
               │
    ┌──────────┼──────────┐
    │          │          │

 worker1    worker2    worker3

 execute    execute    execute
 task       task       task

```

---

# 4 核心本质总结

多线程线程池本质：

`任务队列 + worker线程`

Commit本质：

`提交任务到队列`

worker线程本质：

`循环取任务执行`

future本质：

`跨线程结果同步机制`

condition_variable本质：

`线程高效等待与唤醒机制`

---

