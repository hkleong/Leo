# TX Game Club 会员活动网站

一个独立网站：会员注册 / 登入，查看俱乐部活动并报名；管理员可以发布活动、查看会员资料。
账号和数据用 Google 的 **Firebase**（免费额度），网站本身是纯静态文件，可以放在任何免费托管上。

## 网站功能

- 右上角红色「登入」按钮，旁边是文字「注册」
- 注册：用户名、电话号码、游戏 ID、密码、确认密码
- 登入：用户名 + 密码，可勾选「记住我」（勾选后关掉浏览器也保持登入）
- 左上角菜单：首页 / 活动 / 我的报名 / 我的资料（管理员多一个「会员名单」）
- 活动和报名只对会员开放
- **其他会员只看得到用户名**；电话号码和游戏 ID 只有本人和管理员看得到
- 管理员：添加 / 编辑 / 删除活动、移除报名、查看和复制会员名单

## 文件

| 文件 | 作用 |
|---|---|
| `index.html` | 页面和样式 |
| `app.js` | 网站逻辑 |
| `firebase-config.js` | **你要填写**的 Firebase 配置 |
| `firestore.rules` | 数据库权限规则（谁能看什么、改什么） |

---

## 设置步骤（大约 15–20 分钟）

### 1. 创建 Firebase 项目
1. 用 Google 账号打开 <https://console.firebase.google.com>
2. 点「创建项目」（Add project），名称填 `tx-game-club`
3. Google Analytics 可以关掉，点「创建」

> 免费的 Spark 方案就够用，不需要绑定信用卡。

### 2. 添加网页应用，拿到配置
1. 在项目首页点 `</>`（网页）图标
2. 应用昵称填 `tx-game-club`，**不用**勾选 Firebase Hosting，点「注册应用」
3. 页面会显示一段 `const firebaseConfig = { ... }`
4. 把里面的值逐项复制到本文件夹的 `firebase-config.js` 里（apiKey、authDomain、projectId …）

### 3. 开启账号登录
1. 左侧菜单 → **Authentication** → 「开始使用」
2. 「登录方法」→ 选 **电子邮件/密码** → 打开第一个开关「启用」→ 保存
   （第二个「电子邮件链接」不用开）

> 会员用用户名登入，网站在后台会把用户名转换成 Firebase 需要的账号格式，不会发任何邮件或短信。

### 4. 创建数据库并贴上权限规则
1. 左侧菜单 → **Firestore Database** → 「创建数据库」
2. 位置选离会员近的，例如 `asia-southeast1 (Singapore)`；选「以生产模式启动」
3. 创建好后点上方「**规则**」标签
4. 把 `firestore.rules` 的**全部内容**贴进去，替换原来的内容，点「发布」

### 5. 把网站放上网（二选一）

**方法 A：Netlify（最简单）**
1. 注册一个免费的 Netlify 账号：<https://app.netlify.com>
2. 打开 <https://app.netlify.com/drop>，把整个 `tx-game-club` 文件夹拖进去
3. 几秒后会得到一个网址，例如 `https://xxx.netlify.app`
4. 以后修改文件，再拖一次就会更新

**方法 B：GitHub Pages**
1. 把 `tx-game-club` 文件夹里的文件放进一个公开仓库的根目录（或 `docs/` 文件夹）
2. 仓库 Settings → Pages → Source 选 `Deploy from a branch`，选对应的分支和文件夹
3. 得到网址 `https://你的用户名.github.io/仓库名/`

### 6. 告诉 Firebase 你的网址
Authentication → **设置**（Settings）→ **已获授权的网域**（Authorized domains）→「添加网域」
填上第 5 步的网域，例如 `xxx.netlify.app` 或 `你的用户名.github.io`（不带 https://）。

### 7. 把自己设为管理员
1. 打开网站，点「注册」，注册你自己的账号
2. 登入后打开左上角菜单 →「我的资料」，复制「会员编号」
3. 回到 Firebase 控制台 → Firestore Database → 数据 →「开始收集」（Start collection）
   - 集合 ID：`admins`
   - 文档 ID：贴上你的会员编号
   - 随便加一个字段，例如 `role` = `admin`（字符串），保存
4. 刷新网站，右上角会出现「管理员 · + 添加活动」，菜单里也会多出「会员名单」

想让别人一起当管理员，就用同样的方法把他们的会员编号加进 `admins`。

### 8. 发布活动、分享网址
点「添加活动」发布第一场活动，然后把网址发给朋友，让他们自己注册就行。

---

## 费用

| 项目 | 费用 |
|---|---|
| Firebase 账号登录（用户名 + 密码） | 免费 |
| Firestore 数据库 | 免费额度：约 1 GB 存储、每天约 5 万次读取、2 万次写入，俱乐部规模用不完 |
| Netlify / GitHub Pages 托管 | 免费 |
| 自己的网址（例如 txgameclub.com） | 可选，大约每年 10 美元左右 |

没有短信验证，所以没有短信费用。免费额度以 Firebase 官网的最新说明为准。

## 常见问题

**会员忘记密码怎么办？**
网站没有邮箱和短信，所以无法自助找回。管理员可以在 Firebase 控制台 → Authentication → 用户 中删除该账号，
再到 Firestore 删除 `users` 和 `publicProfiles` 里对应的文档，然后请会员用同一个用户名重新注册。

**电话号码会被验证吗？**
不会。会员填什么就记什么（这是取消 OTP 的代价）。

**firebase-config.js 里的内容会被别人看到，安全吗？**
这些值本来就是公开的，每个 Firebase 网站都会在网页里带着它们。数据由 `firestore.rules` 保护：
别人看不到会员的电话和游戏 ID，也不能改活动或别人的报名。

**在电脑上直接双击 index.html 打不开？**
网站需要通过网址打开（第 5 步）。本地预览可以在文件夹里运行 `python3 -m http.server`，再打开 <http://localhost:8000>。
