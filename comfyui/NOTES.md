# 云端 ComfyUI 项目备忘（压缩后先读这个）

## 部署
- 地址: https://dep-f307503a-180f-462c-b702-a0138fdaa503.run.comfy.app （Comfy API v2）
- API key: scratchpad/.comfy_key（不要提交到仓库、不要打印）
- Build: h3-scail2-video-service（id e981cb77-...），当前部署 video-service = release v4
  - 含 MiniMax H3 Ref2VA、SCAIL-2、SAM3.1、Qwen-Image 2.1(int8+qwen3vl_8b+vae+8步LoRA)、
    h3_character_swap_v1.5、minimax_h3_fl2v_turbo_8step、MaskVidExperiments 0.2.1
  - 改 build: scratchpad/build/comfy-build.yaml + comfy-cli（scratchpad/ccli，env COMFY_CLOUD_API_KEY）
    → `comfy --where cloud build push --release --target linux/nvidia` → `deploy up --release <id> --deployment video-service`

## 脚本（scratchpad/p2）
- gen.py: H3 Ref2VA。参考视频自动转 24fps。--charswap(换人LoRA+FL2V turbo, er_sde/normal) --anchor(首5帧锚定) --no-ref-video --final(720p/40步)
- h3_chain.py: 长视频无缝接力（124帧/段，5帧锚定），原速拼接+原音频
- scail.py / scail_long.py: SCAIL-2 换人（参考图用半身照，不要大脸特写/全身）
- scail_crop.py: SCAIL-2 + MaskVidExperiments（适合远处小人物）
- qwen21.py: 本地 Qwen-Image 2.1 文生图/改图（免 API 费）
- t2i.py/edit.py: Qwen 3.0 API（付费，尽量不用）

## 用户规则
1. 测试 480p+加速LoRA；用户确认后才 720p 40步
2. 参考视频一律先转 24fps（H3 按 24fps 读，否则动作变慢）
3. 长视频用接力+锚定，避免接缝闪
4. 生成不出来就如实说，绝不降速/补帧凑时长
5. 视频任务每 10 分钟 send_later 播报进度，完成即删提醒
6. 生图默认本地 Qwen 2.1
7. 交付前与原视频逐帧对比（位置/时间点/人物）
8. 用户不在时可自行决定；全程中文回复

## 项目状态
- p3 颁奖礼（男主=boyG 皮夹克）：out/award_chain.mp4 已交付（H3+换人LoRA+接力，测试档，用户认可）。
  正在重做第3段让大屏幕海报也换成男主：cs/poster.log → 拼成 out/award_poster.mp4
  （piece1 c6d1d6de 帧0-123 + piece2 c2d53364 局部5-123 + 新piece3 局部31-123，配 award_chain_chain/src24.mp4 音频）
- p2 演唱会：FINAL_v5.mp4 已交付；原片30fps，旧版有1.25x慢放，可用新流程重做
- p4 自拍（新人物 woman2，干净肌）：j1/j2 已交付；可用 H3+换人LoRA+24fps 重做以严格贴原片
- 角色图：p2/in/boyG_*.png（男主灰底）, p3/crop/ref_half.png（男主半身，SCAIL/换人用）, p4/in/woman2_*.png

## 更新（定稿）
- 颁奖礼正式版：p3/out/award_final720.mp4（1280x736, 40步, 海报也换脸）——已交付，定稿。
- 演唱会正式版：p2/out/FINAL_720.mp4（720x1280, 13.9s）——用户认可，定稿。
  镜头1=H3换人(参考 p5/alt_shot1.mp4 去水印版, 始终低头, 无包带)；镜头2=H3 24fps；镜头3=SCAIL no-distill 40步(衣服变成无袖背心，用户接受)
- gen.py --charswap --final：去掉 turbo，换人LoRA直接挂基础模型，40步。h3_chain.py 新增 --done（续跑）、--prompt-last。
- 用户时区 UTC-4，报时用用户时间。后台长任务用 run_in_background（nohup 会被杀；2小时上限后需重启盯任务进程）。

## 角色参考图标准（用户定，林逍 v3 为样板：p6/out/ref3/linxiao_refsheet_v3.png）
1. 先用 qwen21.py 编辑模式从定稿全身图做 base（只改用户要求的地方，不擅自加装饰）
2. 全部用高清：--full（25步）--res 1328，输出约 1088x1632
3. 上排五视图：正面 / 侧面 / 背面 / 半身（腰上，必要时从全身裁）/ 高清特写（脸占满画面，睫毛发丝毛孔清晰）
4. 下排 3–4 张服装/道具细节特写（微距产品照风格，如配饰、武器、袖口、鞋）
5. 灰色背景；顶部标题：角色名 · 角色参考图 + 身份/境界/灵力 + 一句性格
6. 拼版脚本参考 ref3 里的 PIL 代码；单图另存 *_front / *_half / *_face 供视频锁脸

## 更新（2026-11-06）
- 部署升级到 release v5（fc0ca393），新增 SeedVR2 7B fp8 mixed + ema_vae（约 9.0GB），总约 101.3GB；GPU rtx-pro-6000-mig 48GB $1.75/h，min0/max2
- p2/upscale.py：SeedVR2 超分（--res 1080 短边，batch 21，overlap 4）。10.7s 720p→1080p 约 8 分钟
- h3_chain.py：接缝改在下一段锚定帧之后切（消除接缝闪），新增 --deflicker
- p6 终极修仙：角色/设定见 p6/SETTING.md；参考图工具 p6/tools/refsheet.py + specs/；标准校徽 p6/out/emblem/STANDARD_emblem.png
- p7 Chovy 换人：out/chovy_final720.mp4（720p 40步）、out/chovy_final1080.mp4（SeedVR2 超分）
- 待做：五人便服版参考图（用户已同意，排在后面）
- 干净版超分流程：720p 先 ffmpeg smartblur=lr=2.0:ls=0.7:lt=-4 + curves 压高光（0.75→0.73, 1→0.93），再 upscale.py --in-noise 0.3 --lat-noise 0.15。成品 p7/out/chovy_final1080_clean.mp4

## 打戏做法（p8 测试总结，480p 测试即可，不必出 720p）
- 分段：每段 10–17s 一个节奏（飙灵力 / 冲刺交锋 / 大招收尾），H3 --no-ref-video，参考图=林逍脸+正面、反派脸+全身
- 每个 [Shot N] 写清景别、谁对谁做什么、方向、速度；大招先拉开距离，对手要有格挡反应；“用自己的手握自己的剑”
- 冲刺：脸部特写<1s 接压低前倾冲刺（几乎水平、剑拖地），侧面中远景跟拍要亮
- 灵力指数：后期叠 p8/hud2.py（闪电箭头+抠图头像+透视倾斜；右侧原版，左侧 --mirror）；头像用 Qwen 抠绿幕 *_cut.png
- 打戏检查清单新增：每个镜头核对【站位（谁在画面左/右）】与【角色朝向（面向谁、背对/正对镜头）】是否和上下镜头的空间关系一致；镜头从某人身后拍时，那人必须背对镜头
- 部署现为 release v6（f3df44fa，含 ACE-Step v1 ace_step_v1_3.5b 7.7GB）；旧 v1–v4 已删，v5（fc0ca393）留作回滚待用户决定
- p2/acestep.py：ACE-Step 配乐（--tags --lyrics "[inst]" --sec）；gen.py 新增 --steps40（480p 40 步无 turbo）
- p8 打戏 40 步版：p8/s40/fight40_noBGM.mp4（52.4s）、fight40_sfx.wav、fight40_bgm_1/2.wav、fight40_withBGM_1/2.mp4

## 规则更新（11/07）
- 测试一律用 turbo LoRA（gen.py 不加 --steps40），480p。
- 额度/用量用完：脚本自动每 10 分钟重试，重置后自动继续（p6/ep1/run.py）。
- 第一集：故事 p6/story/ep01.md；镜头 p6/ep1/s*.txt；x2 配乐打戏备份 p8/keep/

## 第一集全集（11/07 开跑）
- p6/ep1/full/build.py 镜头表 → prompts/*.txt + jobs.json（35 段，约 434 秒），run.py 40 步、自动重试、已完成跳过
- 第 8–12 场改为当晚学校天台（和已拍好的 fight40 场景一致）；第 10–11 场直接用 fight40
- 表演要求：自然、不夸张；全剧台湾腔

## 站位/背景规则（11/07 用户要求）
- 每个场景先用 Qwen 出一张空景参考图（p6/ep1/sets/SET_*.png），同场景每段都挂同一张，作为最后一张 Picture
- 每段提示词写固定布局（左右墙/道具位置）+ Blocking 段（谁在哪、面朝哪、机位只在哪一侧、180 度规则）
- 每个镜头写明机位、谁在画面左/右、朝向、身后是什么背景
- 群戏挂无脸校服参考图（out/uni/uniform_f.png），写明群演都穿交领校服
- v2：build2.py → prompts2/ jobs2.json，run2.py → raw2/
