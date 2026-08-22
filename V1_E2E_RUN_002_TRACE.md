# 笛语 V1 E2E RUN_002 执行追踪

> 全部字段取自 Dify 后台 `workflow_runs` / `workflow_node_executions` /
> `workflow_conversation_variables`，不取模型自述。

| 记录 | workflow_run_id | 状态 | route | patch_ok | state_saved | Skill | 节点数 | 服务端秒 | tokens |
|---|---|---|---|---|---|---|---|---|---|
| `AU-01#T1` | `8fa7a864` | succeeded | HUMAN_DECISION | true | true | - | 7 | 17.07 | 2957 |
| `AU-01#T2` | `96cea2a8` | succeeded | CONFIRM_TASK | true | false | - | 7 | 63.19 | 5706 |
| `AU-01#T3` | `9d097479` | succeeded | HUMAN_DECISION | true | false | - | 7 | 20.39 | 4255 |
| `AU-01#T4` | `7dde6150` | succeeded | DISCUSS | true | false | - | 7 | 9.77 | 3574 |
| `AU-02#T1` | `b086ebc8` | succeeded | FOCUS | true | false | - | 7 | 22.31 | 4436 |
| `AU-02#T2` | `d736ea89` | succeeded | FOCUS | true | true | - | 7 | 64.77 | 5379 |
| `AU-02#T3` | `0da6f793` | succeeded | FOCUS | true | true | - | 7 | 35.62 | 5146 |
| `AU-02#T4` | `6e2f09c4` | succeeded | CONFIRM_TASK | true | true | - | 7 | 28.16 | 4581 |
| `AU-03#T1` | `3f5d9613` | succeeded | FOCUS | true | true | - | 7 | 31.63 | 5210 |
| `AU-03#T2` | `cdb12118` | succeeded | CONFIRM_TASK | true | true | - | 7 | 25.57 | 4196 |
| `AU-03#T3` | `e33ba3aa` | succeeded | CONFIRM_TASK | true | true | - | 7 | 32.23 | 3730 |
| `AU-03#T4` | `8d219e7e` | succeeded | HUMAN_DECISION | true | true | - | 7 | 38.09 | 3893 |
| `AU-04#T1` | `d130c186` | succeeded | HUMAN_DECISION | true | true | - | 7 | 53.81 | 7870 |
| `AU-04#T2` | `a9cc8263` | succeeded | CONFIRM_TASK | true | false | - | 7 | 32.26 | 6004 |
| `AU-04#T3` | `de2768f4` | succeeded | DISCUSS | true | false | - | 7 | 13.76 | 3770 |
| `AU-05#T1` | `2edb5b46` | succeeded | HUMAN_DECISION | true | true | - | 7 | 14.06 | 3570 |
| `AU-05#T2` | `f2d192f4` | succeeded | DISCUSS | false | false | - | 7 | 59.29 | 6066 |
| `AU-05#T3` | `7c5af389` | partial-succeeded | DISCUSS | true | true | - | 7 | 21.22 | 4111 |
| `AU-06#T1` | `ab7c1560` | succeeded | OUT_OF_SCOPE | true | false | - | 7 | 14.29 | 3867 |
| `AU-06#T2` | `9201b138` | partial-succeeded | OUT_OF_SCOPE | true | false | - | 7 | 30.72 | 4847 |
| `AU-06#T3` | `34b4206f` | partial-succeeded | OUT_OF_SCOPE | true | false | - | 7 | 16.32 | 3459 |
| `AU-07#T1` | `4a79a018` | succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 425.57 | 62637 |
| `AU-07#T2` | `a24986ce` | succeeded | DISCUSS | false | false | - | 7 | 114.81 | 15871 |
| `AU-07#T3` | `cc4c8c92` | succeeded | CONFIRM_TASK | true | true | - | 7 | 74.89 | 8998 |
| `AU-08#T1` | `808b49d0` | succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 197.05 | 33678 |
| `AU-08#T2` | `e7dbace2` | succeeded | HUMAN_DECISION | true | true | - | 7 | 55.89 | 10191 |
| `AU-08#T3` | `3598ac25` | succeeded | FOCUS | true | false | - | 7 | 39.71 | 7617 |
| `AU-08#T4` | `61702c40` | succeeded | HUMAN_DECISION | true | true | - | 7 | 76.85 | 9607 |
| `CT-01#T1` | `c30fa942` | partial-succeeded | FOCUS | true | false | - | 7 | 37.40 | 3946 |
| `CT-01#T2` | `88ed9286` | partial-succeeded | FOCUS | true | true | - | 7 | 38.85 | 4897 |
| `CT-01#T3` | `485e0b19` | partial-succeeded | DISCUSS | true | false | - | 7 | 40.08 | 5363 |
| `CT-01#T4` | `57ce9aaf` | succeeded | SIDE_TOPIC | true | false | - | 7 | 15.52 | 3939 |
| `CT-01#T5` | `47eeeba7` | partial-succeeded | DISCUSS | false | false | - | 7 | 63.01 | 6906 |
| `CT-02#T1` | `2addf349` | partial-succeeded | FOCUS | true | true | - | 7 | 72.52 | 4997 |
| `CT-02#T2` | `ff405382` | succeeded | SIDE_TOPIC | true | false | - | 7 | 23.70 | 4171 |
| `CT-02#T3` | `e19edb11` | succeeded | SIDE_TOPIC | true | false | - | 7 | 15.90 | 4068 |
| `CT-02#T4` | `cad7bb46` | succeeded | SIDE_TOPIC | true | false | - | 7 | 18.12 | 3907 |
| `CT-03#T1` | `660569b9` | succeeded | FOCUS | true | true | - | 7 | 31.12 | 3530 |
| `CT-03#T2` | `2bcd9ab8` | succeeded | FOCUS | true | true | - | 7 | 31.88 | 5699 |
| `CT-03#T3` | `4f770762` | succeeded | CONFIRM_TASK | true | true | - | 7 | 24.58 | 5527 |
| `CT-03#T4` | `e924282c` | partial-succeeded | FOCUS | true | true | - | 7 | 39.20 | 6120 |
| `CT-04#T1` | `c1b89925` | partial-succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 293.73 | 41655 |
| `CT-04#T2` | `` | None | - | None | None | - | 0 | None | None |
| `CT-04#T3` | `4cedd66f` | succeeded | DISCUSS | true | true | - | 7 | 132.94 | 20859 |
| `CT-04#T4` | `8ebcb9fc` | partial-succeeded | DISCUSS | true | false | - | 7 | 38.89 | 6087 |
| `CT-05#T1` | `b8e8a5bf` | succeeded | CONFIRM_TASK | true | false | - | 7 | 14.68 | 3827 |
| `CT-05#T2` | `44149e81` | succeeded | FOCUS | true | false | - | 7 | 39.22 | 6367 |
| `CT-05#T3` | `e46d435a` | partial-succeeded | DISCUSS | true | false | - | 7 | 35.83 | 3958 |
| `CT-06#T1` | `5ccbc376` | succeeded | HUMAN_DECISION | true | true | - | 7 | 21.47 | 4055 |
| `CT-06#T2` | `5ebb09e4` | succeeded | CONFIRM_TASK | true | false | - | 7 | 104.42 | 11701 |
| `CT-06#T3` | `1185569a` | partial-succeeded | DISCUSS | true | false | - | 7 | 76.30 | 4404 |
| `CT-07#T1` | `a0bcbe50` | succeeded | FOCUS | true | true | - | 7 | 15.15 | 3479 |
| `CT-07#T2` | `85fd5910` | succeeded | FOCUS | true | true | - | 7 | 68.72 | 6788 |
| `CT-07#T3` | `5deb5ce0` | succeeded | DISCUSS | true | false | - | 7 | 17.66 | 4627 |
| `CT-07#T4` | `fb92e2cc` | partial-succeeded | DISCUSS | true | false | - | 7 | 23.73 | 4257 |
| `CT-07#T5` | `68cfa181` | succeeded | DISCUSS | true | false | - | 7 | 21.04 | 5888 |
| `CT-07#T6` | `c193c96a` | partial-succeeded | CONFIRM_TASK | true | false | - | 7 | 35.50 | 6501 |
| `FL-01#T1` | `1f1126b1` | partial-succeeded | OUT_OF_SCOPE | true | false | - | 7 | 42.79 | 3928 |
| `FL-01#T2` | `742648bf` | partial-succeeded | OUT_OF_SCOPE | true | false | - | 7 | 60.44 | 3978 |
| `FL-01#T3` | `65139728` | succeeded | DISCUSS | true | false | - | 7 | 15.99 | 4310 |
| `LC-01#T1` | `bdebdef3` | succeeded | DISCUSS | true | false | - | 7 | 10.97 | 3125 |
| `LC-01#T2` | `069ca765` | succeeded | DISCUSS | true | false | - | 7 | 16.33 | 3732 |
| `LC-01#T3` | `835c063c` | succeeded | DISCUSS | true | false | - | 7 | 10.53 | 4096 |
| `LC-02#T1` | `4ec9548a` | succeeded | FOCUS | true | false | - | 7 | 13.96 | 3858 |
| `LC-02#T2` | `79b448c0` | partial-succeeded | DISCUSS | false | false | - | 7 | 134.98 | 7882 |
| `LC-02#T3` | `6af5553c` | succeeded | FOCUS | true | true | - | 7 | 39.65 | 5103 |
| `LC-02#T4` | `37c7a42b` | succeeded | DISCUSS | true | false | - | 7 | 6.36 | 3608 |
| `LC-03#T1` | `b6d7a09f` | succeeded | FOCUS | true | false | - | 7 | 22.14 | 3892 |
| `LC-03#T2` | `ff33e2c8` | succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 244.44 | 38420 |
| `LC-03#T3` | `5c5b907a` | succeeded | CONFIRM_TASK | true | true | - | 7 | 58.17 | 6192 |
| `LC-04#T1` | `bccbf794` | succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 293.41 | 31646 |
| `LC-04#T2` | `6fc283ff` | succeeded | DISCUSS | true | false | - | 7 | 15.00 | 4327 |
| `LC-05#T1` | `2cb68e74` | succeeded | FOCUS | true | false | - | 7 | 16.35 | 4063 |
| `LC-05#T2` | `cadb1ea1` | succeeded | FOCUS | true | true | - | 7 | 26.82 | 4300 |
| `LC-05#T3` | `d9dd973e` | succeeded | CONFIRM_TASK | true | true | - | 7 | 19.30 | 4845 |
| `LC-05#T4` | `976f248d` | succeeded | DISCUSS | false | false | - | 7 | 43.40 | 5663 |
| `LC-06#T1` | `a2a69c5a` | succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 254.32 | 37598 |
| `LC-06#T2` | `dbcd96f5` | succeeded | CONFIRM_TASK | true | true | - | 7 | 36.32 | 7431 |
| `LC-06#T3` | `1754240e` | succeeded | CONFIRM_TASK | true | true | - | 7 | 21.61 | 6034 |
| `LC-07#T1` | `4498414f` | succeeded | FOCUS | true | false | - | 7 | 15.05 | 3321 |
| `LC-07#T2` | `bd9fc07b` | succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 200.55 | 33273 |
| `LC-07#T3` | `4f0246aa` | succeeded | DISCUSS | false | false | - | 7 | 50.01 | 6445 |
| `LC-07#T4` | `8cc17238` | succeeded | DISCUSS | true | true | - | 7 | 26.74 | 6126 |
| `LC-08#T1` | `8fac1d7b` | succeeded | FOCUS | true | true | - | 7 | 15.49 | 3525 |
| `LC-08#T2` | `1491a485` | succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 347.75 | 43974 |
| `LC-08#T3` | `2c49a1fe` | succeeded | DISCUSS | false | false | - | 7 | 36.14 | 7915 |
| `LC-08#T4` | `67c1e7af` | succeeded | CONFIRM_TASK | true | true | - | 7 | 52.54 | 9745 |
| `LC-08#T5` | `d1222c87` | succeeded | CONFIRM_TASK | true | false | - | 7 | 32.71 | 7488 |
| `LC-09#T1` | `55d2549b` | partial-succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 587.88 | 39415 |
| `LC-09#T2` | `a4332350` | succeeded | HUMAN_DECISION | true | true | - | 7 | 41.88 | 7976 |
| `LC-09#T3` | `08f343d9` | succeeded | FOCUS | true | false | - | 7 | 100.73 | 8465 |
| `LC-10#T1` | `d260083a` | succeeded | DISCUSS | false | false | - | 7 | 20.80 | 4177 |
| `LC-10#T2` | `4ea96be9` | succeeded | FOCUS | true | true | - | 7 | 38.93 | 6535 |
| `LC-10#T3` | `940fd7bb` | partial-succeeded | CONFIRM_TASK | true | false | - | 7 | 69.34 | 9877 |
| `LC-10#T4` | `183b97bf` | succeeded | DISCUSS | true | false | - | 7 | 16.92 | 4727 |
| `LC-11#T1` | `4d16606a` | partial-succeeded | EXECUTE_MATRIX | true | true | matrix | 10 | 444.00 | 3304 |
| `LC-11#T2` | `b375e40f` | succeeded | FOCUS | true | true | - | 7 | 48.34 | 8073 |
| `LC-11#T3` | `9ae38537` | partial-succeeded | DISCUSS | true | false | - | 7 | 33.32 | 4421 |
| `LC-12#T1` | `37bd19be` | succeeded | DISCUSS | true | false | - | 7 | 28.67 | 3702 |
| `LC-12#T2` | `ed11d35c` | succeeded | DISCUSS | true | false | - | 7 | 137.48 | 3704 |
| `LC-12#T3` | `10d93275` | partial-succeeded | DISCUSS | true | false | - | 7 | 36.91 | 5737 |
| `S01#T1` | `03f74009` | succeeded | DISCUSS | true | false | - | 7 | 10.85 | 3308 |
| `S01#T2` | `6fac2d0b` | succeeded | DISCUSS | true | false | - | 7 | 42.71 | 4062 |
| `S01#T3` | `d4891495` | succeeded | DISCUSS | true | false | - | 7 | 13.50 | 4859 |
| `S02#T1` | `1150c7ec` | succeeded | FOCUS | true | false | - | 7 | 17.82 | 4249 |
| `S02#T2` | `825fe5a3` | succeeded | CONFIRM_TASK | true | false | - | 7 | 20.93 | 4885 |
| `S02#T3` | `599f789c` | partial-succeeded | FOCUS | true | true | - | 7 | 41.14 | 6065 |
| `S02#T4` | `5b06f17d` | partial-succeeded | CONFIRM_TASK | true | true | - | 7 | 85.25 | 7760 |
| `S03#T1` | `c86d85c3` | succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 297.89 | 42117 |
| `S03#T2` | `21d105ae` | partial-succeeded | DISCUSS | false | false | - | 7 | 31.30 | 926 |
| `S04#T1` | `d4d3142a` | succeeded | FOCUS | true | true | - | 7 | 44.82 | 5983 |
| `S04#T2` | `621a9920` | succeeded | FOCUS | true | true | - | 7 | 39.75 | 5245 |
| `S04#T3` | `5a5b1b09` | partial-succeeded | SIDE_TOPIC | true | false | - | 7 | 26.09 | 5011 |
| `S04#T4` | `7710ecec` | succeeded | SIDE_TOPIC | true | false | - | 7 | 20.82 | 5077 |
| `S04#T5` | `85fe84a7` | succeeded | CONFIRM_TASK | true | true | - | 7 | 34.66 | 7254 |
| `S05#T1` | `f1c2f39b` | succeeded | FOCUS | true | false | - | 7 | 28.35 | 4421 |
| `S05#T2` | `fd103358` | partial-succeeded | FOCUS | true | true | - | 7 | 39.75 | 5171 |
| `S05#T3` | `27363487` | succeeded | FOCUS | true | true | - | 7 | 14.59 | 4154 |
| `S05#T4` | `71393391` | succeeded | DISCUSS | true | false | - | 7 | 22.70 | 5247 |
| `S06#T1` | `ef77d1f3` | succeeded | FOCUS | true | true | - | 7 | 99.46 | 5151 |
| `S06#T2` | `97f12d1e` | succeeded | CONFIRM_TASK | true | true | - | 7 | 38.99 | 4563 |
| `S06#T3` | `210d28ad` | succeeded | CONFIRM_TASK | true | true | - | 7 | 28.53 | 4593 |
| `S06#T4` | `fde72443` | succeeded | HUMAN_DECISION | true | true | - | 7 | 28.24 | 5559 |
| `S07#T1` | `3ab8c2f7` | succeeded | FOCUS | true | false | - | 7 | 17.42 | 3744 |
| `S07#T2` | `db3de008` | succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 194.54 | 34401 |
| `S07#T3` | `50604d00` | succeeded | HUMAN_DECISION | true | true | - | 7 | 25.22 | 6277 |
| `S08#T1` | `65b9502c` | succeeded | FOCUS | true | false | - | 7 | 28.31 | 4717 |
| `S08#T2` | `df3f298c` | partial-succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 550.24 | 38503 |
| `S08#T3` | `f460a1d1` | partial-succeeded | HUMAN_DECISION | true | true | - | 7 | 46.62 | 6206 |
| `S08#T4` | `f9bd194c` | succeeded | DISCUSS | false | false | - | 7 | 60.86 | 8206 |
| `S09#T1` | `e7b796e0` | succeeded | FOCUS | true | true | - | 7 | 35.54 | 5087 |
| `S09#T2` | `af8f9463` | succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 211.59 | 33769 |
| `S09#T3` | `53ac842c` | succeeded | DISCUSS | false | false | - | 7 | 27.38 | 6993 |
| `S09#T4` | `79d6301d` | succeeded | HUMAN_DECISION | true | true | - | 7 | 37.71 | 8153 |
| `S09#T5` | `a90c6e4b` | succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 311.39 | 41349 |
| `S09#T6` | `12337e1f` | succeeded | HUMAN_DECISION | true | true | - | 7 | 22.51 | 6764 |
| `S10#T1` | `167d2eb9` | succeeded | CONFIRM_TASK | true | false | - | 7 | 16.45 | 4475 |
| `S10#T2` | `4562a8e4` | succeeded | HUMAN_DECISION | true | true | - | 7 | 17.59 | 4185 |
| `S10#T3` | `587e81c2` | succeeded | OUT_OF_SCOPE | true | false | - | 7 | 24.20 | 5444 |
| `S10#T4` | `895ffc96` | succeeded | FOCUS | true | true | - | 7 | 35.85 | 6328 |
| `S10#T5` | `b45dfddc` | succeeded | HUMAN_DECISION | true | true | - | 7 | 35.96 | 7350 |
| `SK-01#T1` | `f6a4eca4` | partial-succeeded | FOCUS | true | false | - | 7 | 29.21 | 3406 |
| `SK-01#T2` | `ff866ef0` | partial-succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 282.18 | 39079 |
| `SK-01#T3` | `b7e2b549` | succeeded | HUMAN_DECISION | true | true | - | 7 | 40.74 | 7558 |
| `SK-01#T4` | `cc54c41f` | succeeded | DISCUSS | true | false | - | 7 | 15.06 | 5127 |
| `SK-02#T1` | `13d1b1d8` | partial-succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 600.79 | 38604 |
| `SK-02#T2` | `538b37c4` | succeeded | EXECUTE_CAMPAIGN | true | true | campaign | 13 | 247.25 | 82779 |
| `SK-02#T3` | `b653e2f3` | succeeded | HUMAN_DECISION | true | true | - | 7 | 25.17 | 6625 |
| `SK-02#T4` | `` | None | - | None | None | - | 0 | None | None |
| `SK-03#T1` | `cfd5bded` | succeeded | FOCUS | true | true | - | 7 | 38.63 | 6433 |
| `SK-03#T2` | `85f8d735` | succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 262.91 | 37213 |
| `SK-03#T3` | `4da92f5f` | partial-succeeded | EXECUTE_CAMPAIGN | true | true | campaign | 13 | 217.17 | 92313 |
| `SK-03#T4` | `31745aff` | succeeded | EXECUTE_CONTENT_BRIEF | true | true | content_brief | 13 | 279.36 | 75406 |
| `SK-03#T5` | `8ecb7258` | partial-succeeded | DISCUSS | false | false | - | 7 | 87.86 | 1955 |
| `SK-03#T6` | `a934e503` | partial-succeeded | EXECUTE_CONTENT_BRIEF | true | true | content_brief | 13 | 196.74 | 67475 |
| `SK-04#T1` | `c99a25fd` | partial-succeeded | EXECUTE_MATRIX | true | true | matrix | 10 | 30.37 | 3397 |
| `SK-04#T2` | `1cfbe855` | partial-succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 263.48 | 38953 |
| `SK-04#T3` | `088190d1` | partial-succeeded | DISCUSS | false | false | - | 7 | 76.35 | 11513 |
| `SK-04#T4` | `ad2eeb9a` | succeeded | DISCUSS | true | true | - | 7 | 24.76 | 5832 |
| `SK-04#T5` | `cb921d4f` | succeeded | DISCUSS | true | false | - | 7 | 57.05 | 10920 |
| `SK-04#T6` | `c7368fe0` | succeeded | DISCUSS | true | false | - | 7 | 20.80 | 5825 |
| `SK-05#T1` | `43117261` | succeeded | FOCUS | true | true | - | 7 | 34.11 | 5086 |
| `SK-05#T2` | `871743fb` | partial-succeeded | DISCUSS | false | false | - | 7 | 78.08 | 1101 |
| `SK-05#T3` | `6e4ea692` | partial-succeeded | SIDE_TOPIC | true | true | - | 7 | 59.83 | 3870 |
| `SK-06#T1` | `a2b789d2` | partial-succeeded | DISCUSS | false | false | - | 7 | 46.87 | 994 |
| `SK-06#T2` | `fc8475c9` | partial-succeeded | EXECUTE_MATRIX | true | true | matrix | 13 | 178.05 | 30105 |
| `SK-06#T3` | `6c83b2fe` | succeeded | FOCUS | true | true | - | 7 | 48.78 | 8518 |

## 逐会话终态

| 会话 | matrix | campaign | content_brief |
|---|---|---|---|
| `AU-01` | None | None | None |
| `AU-02` | None | None | None |
| `AU-03` | None | None | None |
| `AU-04` | None | None | None |
| `AU-05` | None | None | None |
| `AU-06` | None | None | None |
| `AU-07` | VALIDATED | None | None |
| `AU-08` | VALIDATED | None | None |
| `CT-01` | None | None | None |
| `CT-02` | None | None | None |
| `CT-03` | None | None | None |
| `CT-04` | VALIDATED | None | None |
| `CT-05` | None | None | None |
| `CT-06` | None | None | None |
| `CT-07` | None | None | None |
| `FL-01` | None | None | None |
| `LC-01` | None | None | None |
| `LC-02` | None | None | None |
| `LC-03` | USER_ACCEPTED | None | None |
| `LC-04` | VALIDATED | None | None |
| `LC-05` | None | None | None |
| `LC-06` | USER_ACCEPTED | None | None |
| `LC-07` | VALIDATED | None | None |
| `LC-08` | VALIDATED | None | None |
| `LC-09` | VALIDATED | None | None |
| `LC-10` | None | None | None |
| `LC-11` | None | None | None |
| `LC-12` | None | None | None |
| `S01` | None | None | None |
| `S02` | None | None | None |
| `S03` | VALIDATED | None | None |
| `S04` | None | None | None |
| `S05` | None | None | None |
| `S06` | None | None | None |
| `S07` | VALIDATED | None | None |
| `S08` | FAILED | None | None |
| `S09` | VALIDATED | None | None |
| `S10` | None | None | None |
| `SK-01` | VALIDATED | None | None |
| `SK-02` | USER_ACCEPTED | VALIDATED | None |
| `SK-03` | USER_ACCEPTED | USER_ACCEPTED | VALIDATED |
| `SK-04` | VALIDATED | None | None |
| `SK-05` | None | None | None |
| `SK-06` | VALIDATED | None | None |

## 逐轮节点路径

### AU-01

- `AU-01#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-01#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-01#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-01#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### AU-02

- `AU-02#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-02#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-02#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-02#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### AU-03

- `AU-03#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-03#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-03#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-03#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### AU-04

- `AU-04#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-04#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-04#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### AU-05

- `AU-05#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-05#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-05#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### AU-06

- `AU-06#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-06#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-06#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### AU-07

- `AU-07#T1` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `AU-07#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-07#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### AU-08

- `AU-08#T1` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `AU-08#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-08#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `AU-08#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### CT-01

- `CT-01#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-01#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-01#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-01#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-01#T5` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### CT-02

- `CT-02#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-02#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-02#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-02#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### CT-03

- `CT-03#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-03#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-03#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-03#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### CT-04

- `CT-04#T1` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `CT-04#T2` → （无）
- `CT-04#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-04#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### CT-05

- `CT-05#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-05#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-05#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### CT-06

- `CT-06#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-06#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-06#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### CT-07

- `CT-07#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-07#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-07#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-07#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-07#T5` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `CT-07#T6` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### FL-01

- `FL-01#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `FL-01#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `FL-01#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### LC-01

- `LC-01#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-01#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-01#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### LC-02

- `LC-02#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-02#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-02#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-02#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### LC-03

- `LC-03#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-03#T2` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `LC-03#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### LC-04

- `LC-04#T1` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `LC-04#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### LC-05

- `LC-05#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-05#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-05#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-05#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### LC-06

- `LC-06#T1` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `LC-06#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-06#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### LC-07

- `LC-07#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-07#T2` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `LC-07#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-07#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### LC-08

- `LC-08#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-08#T2` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `LC-08#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-08#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-08#T5` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### LC-09

- `LC-09#T1` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `LC-09#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-09#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### LC-10

- `LC-10#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-10#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-10#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-10#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### LC-11

- `LC-11#T1` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → v1_toolfail_detail → v1_toolfail_kind → v1_toolfail → v1_toolfail_save → v1_toolfail_answer
- `LC-11#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-11#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### LC-12

- `LC-12#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-12#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `LC-12#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### S01

- `S01#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S01#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S01#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### S02

- `S02#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S02#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S02#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S02#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### S03

- `S03#T1` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `S03#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### S04

- `S04#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S04#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S04#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S04#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S04#T5` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### S05

- `S05#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S05#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S05#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S05#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### S06

- `S06#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S06#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S06#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S06#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### S07

- `S07#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S07#T2` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `S07#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### S08

- `S08#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S08#T2` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `S08#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S08#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### S09

- `S09#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S09#T2` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `S09#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S09#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S09#T5` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `S09#T6` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### S10

- `S10#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S10#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S10#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S10#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `S10#T5` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### SK-01

- `SK-01#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `SK-01#T2` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `SK-01#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `SK-01#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### SK-02

- `SK-02#T1` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `SK-02#T2` → v1_start → v1_shadow → v1_state → v1_route → tool_campaign → lit_campaign → pre_campaign → gate_campaign → judge_campaign → fin_campaign → artsave_campaign → snapsave_campaign → answer_campaign
- `SK-02#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `SK-02#T4` → （无）
### SK-03

- `SK-03#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `SK-03#T2` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `SK-03#T3` → v1_start → v1_shadow → v1_state → v1_route → tool_campaign → lit_campaign → pre_campaign → gate_campaign → judge_campaign → fin_campaign → artsave_campaign → snapsave_campaign → answer_campaign
- `SK-03#T4` → v1_start → v1_shadow → v1_state → v1_route → tool_content_brief → lit_content_brief → pre_content_brief → gate_content_brief → judge_content_brief → fin_content_brief → artsave_content_brief → snapsave_content_brief → answer_content_brief
- `SK-03#T5` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `SK-03#T6` → v1_start → v1_shadow → v1_state → v1_route → tool_content_brief → lit_content_brief → pre_content_brief → gate_content_brief → judge_content_brief → fin_content_brief → artsave_content_brief → snapsave_content_brief → answer_content_brief
### SK-04

- `SK-04#T1` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → v1_toolfail_detail → v1_toolfail_kind → v1_toolfail → v1_toolfail_save → v1_toolfail_answer
- `SK-04#T2` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `SK-04#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `SK-04#T4` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `SK-04#T5` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `SK-04#T6` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### SK-05

- `SK-05#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `SK-05#T2` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `SK-05#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
### SK-06

- `SK-06#T1` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
- `SK-06#T2` → v1_start → v1_shadow → v1_state → v1_route → tool_matrix → lit_matrix → pre_matrix → gate_matrix → judge_matrix → fin_matrix → artsave_matrix → snapsave_matrix → answer_matrix
- `SK-06#T3` → v1_start → v1_shadow → v1_state → v1_route → v1_chat_save → v1_chat_llm → v1_chat_answer
