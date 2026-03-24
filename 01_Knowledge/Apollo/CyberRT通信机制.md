
# 1 订阅机制
Orin的通信基于Apollo的CyberRT架构，使用和组件绑定的节点创建Reader和Writer实现消息接收和发送。
## 1.1 Reader
用于订阅消息并绑定相应的回调函数，当收到特定消息类型时自动触发处理
```
/*节点创建了一个名为m_apa_veh_pos_reader_的reader，监听FLAGS_parking_mcu_apa_veh_pos话题，接收到byd::msg::parking::base::AlgInterfaceApaVehPos类型的消息后，触发与该组件ParkingAvmComponent实例绑定的的回调函数AlgInterfaceApaVehPosCallback
*/
m_apa_veh_pos_reader_ =
      node_->CreateReader<byd::msg::parking::base::AlgInterfaceApaVehPos>(
          FLAGS_parking_mcu_apa_veh_pos,
          std::bind(&ParkingAvmComponent::AlgInterfaceApaVehPosCallback, this,
                    std::placeholders::_1));
```

## 1.2 Writer
用于发布指定类型的消息到指定的topic，供其他节点的Reader订阅
```
//创建一个writer将AlgInterfaceApaVehPos类型的消息发布到FLAGS_avm_veh_pos_topic主题
m_veh_pos_writer_ =
      node_->CreateWriter<byd::msg::parking::base::AlgInterfaceApaVehPos>(
          FLAGS_avm_veh_pos_topic);
```

## 1.3 Topic
### 1.3.1 配置文件
.pb.txt配置文件中集中、静态指定了消息话题和参数的值
```
app_name:"ParkingAvm"
pub_avm_status:"/parking_avm/avm_status"
pub_pas_alarm:"/parking_avm/pas_alarm"
pub_veh_pos:"/parking_avm/veh_pos"
```

### 1.3.2 GFlags
Orin中同时使用了GFlags，可以动态设置消息话题。
```
//拼接出GFLags_avm_veh_pos_topic变量，其默认值为/parking_avm/veh_pos
DEFINE_string(avm_veh_pos_topic, "/parking_avm/veh_pos", ""); 
```

可以在命令行中覆盖默认值
```
./mainboard --avm_veh_pos_topic=/custom/veh_pos
```

# 2 消息类型
## 2.1 Orin和J3的消息类型
在J3平台 ，ProtoMsg消息模板类继承自 Message 基类，并包含一个Protocol Buffers(Protobuf)类型的成员变量 proto。在消息处理系统中，Message负责通用的消息管理功能，如生成和获取时间戳、管理扩展信息等，而 proto 成员变量负责存放和处理 Protobuf 格式的消息内容。在消息发送过程中，具体的 ProtoMsg对象会被多态地视为Message基类对象，从而能够统一管理和传递。在消息接收时，通过动态指针转换可以将 Message 指针恢复为具体的 ProtoMsg类型，从而访问和处理存储的数据。
在Orin平台，直接使用Protobuf 类型的消息，其中包含一个消息头成员Header和实际的消息内容。Header中包含发布消息的时间戳publish_timestamp，传感器时间戳measurement_timestamp，模块名module_name，序列号sequence_num等
```
//仅示例
message AvmCanInputData
{
    optional byd.msg.basic.Header header = 1; //消息头
    optional float speed = 2; //实际内容                   
    optional bool avm_enable_state = 3;
}
message Header {
  optional double publish_timestamp = 1;
  optional double measurement_timestamp = 2;
  optional string module_name = 3;
  optional uint32 sequence_num = 4;
  ...
} 
```

## 2.2 Protobuf的编译
Protocol Buffers是一种与平台、语言无关的数据序列化机制。通过调用Protobuf编译器protoc可以将.protp文件编译到多种平台例如c++。
Orin代码中使用Bazel接管了该编译流程，根据build配置，.proto文件会先被编译链接成中间文件，最终生成.pb.h和.pb.cc文件，.proto文件中的每一个消息都会有一个对应的类。
```
cc_proto_library(
    name = "parking_avm_cc_proto",
    deps = [
        ":parking_avm_proto",
    ],
)
proto_library(
    name = "parking_avm_proto",
    srcs = ["parking_avm.proto"],
    deps = [
        "//modules/msg/basic_msgs:header_proto",
        "//modules/msg/parking_base_msgs:parking_base_proto",
        "//modules/msg/parking_decision_msgs:parking_decision_proto",
    ],
)
```

## 2.3 消息类型和算法结构体的转换
算法模块从上游模块接收消息后，需要将消息类型转换成算法结构体，在模块对应的.pb.h文件下，inline定义的消息成员同名函数可以直接获取其成员，然后转换赋值给算法结构体的成员，示例如下
```
uint64_t ts = static_cast<uint64_t>(data->header().measurement_timestamp() * 1000);
input_data.speed = data->speed();
```


算法模块完成计算后，需要将算法结构体转换成消息类型发送到下游模块，可以使用内联定义的set函数把算法结构体成员转换成消息成员，示例如下。需要注意的是，对于消息类型的可变消息成员（如嵌套的header)，只能使用带mutable_前缀函数来修改
```
data->mutable_header()->set_measurement_timestamp(ts); 
data->set_ads_apa_confirm_swt_avl(out_selected_slot_available_state_);

```
## 2.4 序列化与反序列化
在模块的.pb.cc文件中定义了SerializeToArray方法，发送消息时将消息序列化成二进制格式，以便传输；接收消息时ParseFromArray方法将二进制数据反序列化成具体的protobuf消息对象，以便访问其内容
