
# 1 基本流程
1. 初始化工作区WORKSPACE
	1. Bazel 根据 WORKSPACE 加载外部依赖；
	2. 所有 Bazel 规则必须在这个定义的环境里运行
2. bazel编译生成可执行文件
	1. bazel build 生成 mainboard、各个模块的 .so 等
3. cyber_launch启动mainboard
	1. 解析 .launch 文件，确定要加载的 .dag 配置
	2. 把 \<param\> 中的 gflags/flagfile 注入 mainboard 进程
4. 解析gflags（进程级参数）
	1. 在 mainboard 进程启动早期，gflags 完成初始化
5. cyber::Init()
	1. 初始化进程管理；
	2. 启动日志系统、调度系统、消息传输层
6. 解析.dag文件
	1. 读取 dag_config（线程数、调度策略等）；
	2. dlopen() 加载 module_library（组件 so）；
	3. 构造组件实例（CYBER_REGISTER_COMPONENT）
7. 调用各组件的Init()
	1. 每个组件在 Init() 中解析结构化配置（conf.pb.txt）
	2. 可结合 gflags 进行覆盖；
	3. 创建 Writer/Reader、初始化内部参数
8. 进入运行态
	1. 调度器根据 dag_config（或默认）在线程池里调度任务；
	2. Writer/Reader 驱动消息流转，组件 Proc()/定时任务开始运行
# 2 mainboard启动流程
使用模块管理框架mainboard来管理组件，多个模块共享一个进程，提高CPU调度效率
## 2.1 实例
```
modules/parking_avm/dag/parking_avm.dag
dag_config{
    process_name: "parking_avm"
    thread_num: 8
    policy: "SCHED_RR"
}

module_config {
    module_library : "modules/parking_avm/libparking_avm_component.so"
    timer_components {
        class_name : "ParkingAvmComponent"
        config {
            name : "parkingavm"
            config_file_path : "modules/parking_avm/conf/parking_avm_conf.pb.txt"
            interval: 20
        }
    }
}
```

- dag文件中dag_config并不是必须项。缺省时，mainboard会使用cyberRT默认调度配置（线程池大小、调度策略等）。mainboard支持同时加载多个.dag，这些模块会落在同一个进程的同一线程池里，由cyberRT调度器在多个工作线程中执行
```
module_config {
    module_library : "/apollo/bazel-bin/modules/tutorial/libreceiver_component.so"

    components {
        class_name : "ReceiverComponent"
        config {
            name : "receiver"
            readers {
                channel: "/tutorial/obstacles"
            }
        }
    }
}
```

- dag中配置readers声明输入通道和队列深度，在Component<>流式组件模式下，框架会据此自动创建reader并把消息拼成Proc的入参；在TimerComponent定时组件模式下，通常在代码里手动CreateReader+回调
- conf.pb.txt中的输出topic属于组件私有proto配置，仅该组件读取使用，适合写结构化、版本化的参数，在Init()中解析；gflags是进程级，通过--flagfile= 注入，同一mainboard内所有组件共享命名空间，适合运行期常调参数
```
DEFINE_string(parking_mcu_selected_slot, "/drivers/parking_mcu/selected_slot","");
```