# 1 疲劳

| 序号 | 信号名 | 含义 |
|---|---|---|
| 1 | ADASDMSDrwsyDrvrWrngIndReq | 疲劳报警：$0=Indicator Off; $1=Lightly Drowsy; $2=Severe Drowsy |
| 2 | isEyeClosed | 是否闭眼 |
| 3 | isYawn | 是否打哈欠 |
| 4 | vis_spd | 表显车速（kph） |
| 5 | ADAS100CstCurrSetVal | 灵敏度设置：<br>$0=Setting Unknown; $1=Off; $2=Low Sensitivity;<br>$3=Normal Sensitivity; $4=High Sensitivity;<br>$5=Reserved_5; $6=Reserved_6; $7=Reserved_7 |
| 6 | if_DrwsyinCool | 是否在冷却期 |
| 7 | ADASDMSWrkStaAtthctd | DMS状态：$0=Off; $1=Standby; $2=Active; |
| 8 | PID_DMS_Inhibit_Byte0_3<br>PID_DMS_Inhibit_Byte4_7 | DMS inhibit |

## 1.1 闭眼功能排查

1. 驾驶员闭眼，isEyeClosed持续true，2s以上（非低灵敏度），5s以上（低灵敏度），ADASDMSDrwsyDrvrWrngIndReq一直是0

   1.1 检查ADASDMSWrkStaAtthctd是否为Active，如果不是，读取：

   - PID_DMS_Inhibit_Byte0_3
   - PID_DMS_Inhibit_Byte4_7

   1.2 检查ADASDMSWrkStaAtthctd为Active，功能是否处于冷却期 if_DrwsyinCool=true，如果处于冷却期，正常表现

   1.3 检查vis_spd是否大于18kph持续2s，如果车速不满足要求，正常表现

2. 驾驶员闭眼，但isEyeClosed一直为false，定位为感知问题

3. 驾驶员睁眼，但isEyeClosed一直为true，定位为感知问题


---

## 1.2 打哈欠功能排查

1. 驾驶员打哈欠，isYawn一直为true，持续3s以上（高灵敏度，低灵敏度无该功能），ADASDMSDrwsyDrvrWrngIndReq一直是0

   1.1 检查ADASDMSWrkStaAtthctd是否为Active，如果不是，读取：

   - PID_DMS_Inhibit_Byte0_3
   - PID_DMS_Inhibit_Byte4_7

   1.2 检查ADASDMSWrkStaAtthctd为Active，功能是否处于冷却期 if_DrwsyinCool=true，如果处于冷却期，正常表现

   1.3 检查vis_spd是否大于18kph持续2s，如果车速不满足要求，正常表现

2. 驾驶员打哈欠，但isYawn一直为false，定位为感知问题

3. 驾驶员没有打哈欠，但isYawn一直为true，定位为感知问题


---

# 2 分心

| 序号  | 信号名                                                | 含义                                                                                                                                                      |
| --- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | ADASDMSInattntvDrvrWrngIndReq                      | 分心报警：$0=Indicator Off; $1=Inattentive                                                                                                                   |
| 2   | ADASDMSDrwsyDrvrWrngIndReq                         | 疲劳报警：$0=Indicator Off; $1=Lightly Drowsy; $2=Severe Drowsy                                                                                              |
| 3   | if_attentionoff                                    | 是否视线分心                                                                                                                                                  |
| 4   | vis_spd                                            | 表显车速（kph）                                                                                                                                               |
| 5   | ADAS100CstCurrSetVal                               | 灵敏度设置：<br>$0=Setting Unknown; $1=Off; $2=Low Sensitivity;<br>$3=Normal Sensitivity; $4=High Sensitivity;<br>$5=Reserved_5; $6=Reserved_6; $7=Reserved_7 |
| 6   | if_sightinCool                                     | 冷却期                                                                                                                                                     |
| 7   | isMonitoringEnabled                                | 非打转向灯且非转角在10度内                                                                                                                                          |
| 8   | ADASDMSWrkStaAtthctd                               | DMS状态：$0=Off; $1=Standby; $2=Active;                                                                                                                    |
| 9   | PID_DMS_Inhibit_Byte0_3<br>PID_DMS_Inhibit_Byte4_7 | DMS inhibit                                                                                                                                             |

## 2.1 视线分心功能排查

1. 驾驶员视线不在车辆正前方，if_attentionoff持续true，3s以上，非低灵敏度ADASDMSInattntvDrvrWrngIndReq一直是0

   1.1 检查ADASDMSWrkStaAtthctd是否为Active，如果不是，读取：

   - PID_DMS_Inhibit_Byte0_3
   - PID_DMS_Inhibit_Byte4_7

   1.2 检查ADASDMSWrkStaAtthctd为Active，功能是否处于冷却期if_sightinCool=true，如果处于冷却期，正常表现

   1.3 检查vis_spd是否大于18kph持续2s，如果车速不满足要求，正常表现

   1.4 ADASDMSDrwsyDrvrWrngIndReq>0，疲劳优先级高，表现正常

2. 驾驶员视线分心，但if_attentionoff一直为false，定位为感知问题

3. 驾驶员视线正常前方，但if_attentionoff一直为true，定位为感知问题


## 2.2 头部姿态分心功能排查（当前状态标定关闭）

1. 驾驶员头部姿态不正，if_abnormalhead持续true：

   - 3s（非低灵敏度）
   - 60s（低灵敏度）

   ADASDMSInattntvDrvrWrngIndReq一直是0

   1.1 检查ADASDMSWrkStaAtthctd是否为Active，如果不是，读取：

   - PID_DMS_Inhibit_Byte0_3
   - PID_DMS_Inhibit_Byte4_7

   1.2 检查ADASDMSWrkStaAtthctd为Active，功能是否处于冷却期if_sightinCool=true（共享冷却时间），如果处于冷却期，正常表现

   1.3 检查vis_spd是否大于18kph持续2s，如果车速不满足要求，正常表现

   1.4 ADASDMSDrwsyDrvrWrngIndReq>0，疲劳优先级高，表现正常

2. 驾驶员头部不正，但if_abnormalhead一直为false，定位为感知问题

3. 驾驶员头部正常，但if_abnormalhead一直为true，定位为感知问题


---

# 3 抽烟、接打电话

| 序号 | 信号名 | 含义 |
|---|---|---|
| 1 | ADASDMSDangrsDrvgBhvWrngIndReq | 危险报警：$0=Indicator Off; $1=smoke; $3=phone |
| 2 | if_phone | 是否打电话 |
| 3 | if_smoke | 是否抽烟 |
| 4 | vis_spd | 表显车速（kph） |
| 5 | ADAS100CstCurrSetVal | 灵敏度设置：<br>$0=Setting Unknown; $1=Off; $2=Low Sensitivity;<br>$3=Normal Sensitivity; $4=High Sensitivity;<br>$5=Reserved_5; $6=Reserved_6; $7=Reserved_7 |
| 6 | if_PhoneinCool | 是否在冷却期 |
| 7 | if_SmokeinCool | 是否在冷却期 |
| 8 | ADASDMSWrkStaAtthctd | DMS状态：$0=Off; $1=Standby; $2=Active; |
| 9 | PID_DMS_Inhibit_Byte0_3<br>PID_DMS_Inhibit_Byte4_7 | DMS inhibit |

1. 驾驶员视线在接打电话，if_phone持续true，3s以上，高灵敏度，其余灵敏度该功能无，ADASDMSDangrsDrvgBhvWrngIndReq一直是0

   1.1 检查ADASDMSWrkStaAtthctd是否为Active，如果不是，读取：

   - PID_DMS_Inhibit_Byte0_3
   - PID_DMS_Inhibit_Byte4_7

   1.2 检查ADASDMSWrkStaAtthctd为Active，功能是否处于冷却期if_PhoneinCool=true，如果处于冷却期，正常表现（抽烟对应if_SmokeinCool）

   1.3 检查vis_spd是否大于18kph持续2s，如果车速不满足要求，正常表现

   1.4 ADASDMSDrwsyDrvrWrngIndReq>0，疲劳优先级高，表现正常

   1.5 ADASDMSInattntvDrvrWrngIndReq>0，分心优先级高，表现正常

2. 驾驶员视线打电话，但if_phone一直为false，定位为感知问题

3. 驾驶员视线不在打电话，但if_phone一直为true，定位为感知问题