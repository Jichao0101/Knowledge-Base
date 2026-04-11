# 1 Model Pipeline Profiling Report

## 1.1 Current Result
- Branch: `br_develop_forJ6b`
- Commit: `6cb763da76a791740129cad4a00535c7db303e04`
- Dirty: `true`
- Timestamp: `2026-04-08T15:01:52+08:00`
- Target: `board / J6B / QNX`
- Build Config: `{'build_script': 'scripts/compile_j6b.sh', 'output_binary': './build/main/sdk'}`
- Run Config: `{'entrypoint': '/userdata/dms/run.sh', 'working_dir': '/userdata/dms', 'mode': 'bounded_20s_stdout_capture'}`
- Document Curation: `downstream_agent_required_for_version_specific_operator_mapping`

### 1.1.1 Stage Metrics
| Stage | Mean(us) |
|---|---:|
| preprocess | 21213.7273 |
| inference | 8266.8601 |
| postprocess | 433.2882 |
| total | n/a |

### 1.1.2 Per-Model Stage Metrics
#### 1.1.2.1 DetModel
| PreProcess(us) | Inference(us) | PostProcess(us) |
|---:|---:|---:|
| 18095.3061 | 12554.8367 | 1708.0612 |

#### 1.1.2.2 EyeStatus
| PreProcess(us) | Inference(us) | PostProcess(us) |
|---:|---:|---:|
| 5253.2683 | 2824.3659 | 81.1707 |

#### 1.1.2.3 HandPose
| PreProcess(us) | Inference(us) | PostProcess(us) |
|---:|---:|---:|
| 2065.8333 | 3548.4667 | 2.9333 |

#### 1.1.2.4 HumanPose
| PreProcess(us) | Inference(us) | PostProcess(us) |
|---:|---:|---:|
| 25336.0227 | 16062.7045 | 214.3182 |

#### 1.1.2.5 Landmark
| PreProcess(us) | Inference(us) | PostProcess(us) |
|---:|---:|---:|
| 3805.4762 | n/a | n/a |

#### 1.1.2.6 Pipeline
| PreProcess(us) | Inference(us) | PostProcess(us) |
|---:|---:|---:|
| 216410.6098 | 8610.6506 | 339.3494 |

#### 1.1.2.7 SmkCallClsModel
| PreProcess(us) | Inference(us) | PostProcess(us) |
|---:|---:|---:|
| 2011.625 | 8053.8958 | 1.9512 |

#### 1.1.2.8 Unassigned
| PreProcess(us) | Inference(us) | PostProcess(us) |
|---:|---:|---:|
| n/a | n/a | n/a |

### 1.1.3 Per-Model Fine-Grained Operators
> Note: model and phase ownership in this section only use names explicitly encoded in the profiling output. Version-specific remapping should be curated by the downstream agent.

#### 1.1.3.1 DetModel
| Operator | Phase | Mean(us) | Median(us) | P95(us) | Count |
|---|---|---:|---:|---:|---:|
| - | - | - | - | - | - |

#### 1.1.3.2 EyeStatus
| Operator | Phase | Mean(us) | Median(us) | P95(us) | Count |
|---|---|---:|---:|---:|---:|
| - | - | - | - | - | - |

#### 1.1.3.3 HandPose
| Operator | Phase | Mean(us) | Median(us) | P95(us) | Count |
|---|---|---:|---:|---:|---:|
| - | - | - | - | - | - |

#### 1.1.3.4 HumanPose
| Operator | Phase | Mean(us) | Median(us) | P95(us) | Count |
|---|---|---:|---:|---:|---:|
| - | - | - | - | - | - |

#### 1.1.3.5 Landmark
| Operator | Phase | Mean(us) | Median(us) | P95(us) | Count |
|---|---|---:|---:|---:|---:|
| - | - | - | - | - | - |

#### 1.1.3.6 Pipeline
| Operator | Phase | Mean(us) | Median(us) | P95(us) | Count |
|---|---|---:|---:|---:|---:|
| - | - | - | - | - | - |

#### 1.1.3.7 SmkCallClsModel
| Operator | Phase | Mean(us) | Median(us) | P95(us) | Count |
|---|---|---:|---:|---:|---:|
| Inference_SMK | Unknown | 3959.6458 | 4605.5 | 4821 | 48 |
| _CropImage | Unknown | 2217.9268 | 2249 | 2632 | 41 |
| _GetDriverBox | Unknown | 20.4792 | 20 | 49 | 48 |

#### 1.1.3.8 Unassigned
| Operator | Phase | Mean(us) | Median(us) | P95(us) | Count |
|---|---|---:|---:|---:|---:|
| cv::resize | Unknown | 3166.1429 | 3184 | 3326 | 42 |
| cv::clone | Unknown | 485.4762 | 492 | 626 | 42 |
| cropEye128 | Unknown | 173.5 | 156 | 279 | 82 |

## 1.2 Baseline Comparison
### 1.2.1 Stage Diff
| Stage | Current | Baseline | Delta(us) | Delta(%) | Status |
|---|---:|---:|---:|---:|---|
| preprocess_us | 21213.7273 | 21213.7273 | 0.0 | 0.0 | unchanged |
| inference_us | 8266.8601 | 8266.8601 | 0.0 | 0.0 | unchanged |
| postprocess_us | 433.2882 | 433.2882 | 0.0 | 0.0 | unchanged |
| total_us | - | - | - | - | unknown |

### 1.2.2 Operator Diff TopN
| Operator | Current | Baseline | Delta(us) | Delta(%) | Status |
|---|---:|---:|---:|---:|---|
| DetModel::Inference | 12554.8367 | 12554.8367 | 0.0 | 0.0 | unchanged |
| DetModel::PostProcess | 1708.0612 | 1708.0612 | 0.0 | 0.0 | unchanged |
| DetModel::PreProcess | 18095.3061 | 18095.3061 | 0.0 | 0.0 | unchanged |
| EyeStatus::Inference | 2824.3659 | 2824.3659 | 0.0 | 0.0 | unchanged |
| EyeStatus::PostProcess | 81.1707 | 81.1707 | 0.0 | 0.0 | unchanged |

### 1.2.3 Comparability Risks
- none

## 1.3 Baseline Status
- Doc Write Mode: `replace_report`
- Baseline Source: `/mnt/c/Users/Jichao/OneDrive/knowledgeBase/02_Projects/DMS/06_SDK_Integration/profiling_baseline.json`
- Baseline Availability: `available`
- Update Pending Confirmation: `false`
- Action Required: `none`

## 1.4 History
| Time | Branch | Commit | Total(us) | Baseline Action |
|---|---|---|---:|---|
| 2026-04-08T15:01:52+08:00 | br_develop_forJ6b | 6cb763da76a791740129cad4a00535c7db303e04 | n/a | pending_confirmation |
