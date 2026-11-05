# 云端 ComfyUI 视频工作流

> 使用前：`export COMFY_API_KEY=comfyui-...`（不要把 key 提交进仓库）。脚本在 `scripts/`，需要 python3 + ffmpeg。
> 部署地址写在 `scripts/gen.py` 的 `BASE`；改部署需用 comfy-cli 和 `build/comfy-build.yaml`。
> 下面是工作备忘（原路径指当时会话的临时目录，对应本仓库 `comfyui/` 下的同名文件）。

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
