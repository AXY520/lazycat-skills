# Lazycat Skills

面向 AI 编程助手的懒猫微服应用开发技能集，用于将源码、Docker 镜像或 Compose 项目移植为 **LPK V2** 应用，并处理路由、认证、部署参数、文件选择器和应用上架。

本技能集仅支持 LPK V2，要求 **lzcos >= 1.5.0、lzc-cli >= 2.0.0**。遇到旧项目时先迁移到 V2，不提供 LPK V1 打包或降级方案。新能力仍须逐项核对最低系统版本。

## 安装与使用

在应用项目目录中安装当前维护的版本：

```bash
npx skills add AXY520/lazycat-skills
```

按安装器提示选择所用的 AI 助手和技能。安装后可以直接提出需求，例如：

> 把当前 Compose 项目移植成懒猫 LPK V2 应用，保留原有数据，补齐中英文 locales，并检查上架所需的免密登录与文件选择器接入。

不确定该用哪个技能时，先使用 `lazycat-developer-expert`；只做打包时使用 `lazycat-lpk-builder`。仓库更新后需要同步更新已安装的技能，旧副本不会自动获得新规则。

## 默认产物规范

以下是本技能集的交付约束，适用于完整应用产物：

1. **只生成 LPK V2。** 静态元数据和权限写入 `package.yml`，服务、路由和注入写入 `lzc-manifest.yml`；构建配置写入 `lzc-build.yml`，开发态差异写入 `lzc-build.dev.yml`。
2. **中英文 locales 必须完整。** `package.yml` 必须同时填写 `locales.zh-CN`、`locales.en-US`，每组都包含非空、内容对应的 `name` 与 `description`。产品专名可以保持原名，描述应有实际翻译；顶层回退值不能代替任一语言。已声明应用入口时，入口标题也按官方规则补齐两种语言。
3. **usage 仅按用户明确要求添加。** 默认省略 manifest 顶层 `usage` 和所有 `locales.*.usage`，也不生成空字段。用户要求使用须知时再填写对应中英文内容；已有用户内容按原意保留，不擅自扩写。交付说明、使用指南和部署日志不会自动变成首次访问提示。
4. **上架前完成适配和验证。** 按当前官方审核要求检查资料、镜像、登录、持久化及功能适配。有上传／下载功能时，必须接入官方网盘文件选择器并实际验证。

平台 schema 中部分字段是可选的；本技能集对双语元数据和默认交互采用上述更严格的产物约束。只展示权限或资源的局部片段可以保持局部，合并为完整应用配置时仍须满足全部规则。

完整配置可参考 [LPK V2 静态站示例](skills/lazycat-developer-expert/examples/static-site/README.md)；元数据细则见 [package 规范摘要](skills/lazycat-lpk-builder/references/package-spec.md)。

## 上架与文件选择器

有上传／下载功能的商店应用必须按[官方自动拦截文件选择器说明](https://developer.lazycat.cloud/lazycat-file-picker-auto-intercept.html)接入网盘与本地文件选择。

技能内的[文件选择器接入指南](skills/lazycat-lpk-builder/references/file-picker.md)包含官方脚本下载、browser inject、同源 request bridge、共享目录 `Owner` 转发和验收步骤。两条 inject 必须同时配置，并验证本地文件、自己的网盘文件及共享可写目录。目录选择、普通 HTTP 下载等未被脚本覆盖的入口需单独适配。

上架还需要核对镜像来源、免密登录、首次安装与升级、数据持久化、启动和响应速度等要求，详见[上架检查与发布流程](skills/lazycat-lpk-builder/references/store-publish.md)。构建、安装和商店发布是不同操作，执行范围按用户授权确定。

## 技能列表

- `lazycat-developer-expert`: 开发总入口，按需求加载配置、路由、认证和上架规范。
- `lazycat-lpk-builder`: 源码、Docker 镜像与 Compose 移植，LPK V2 配置、构建和验收。
- `lazycat-dynamic-deploy`: 安装参数、Go 模板、browser/request/response 注入与文件选择器。
- `lazycat-advanced-routing`: HTTP 路由、域名前缀、Host、TCP/UDP 转发与访问边界。
- `lazycat-auth-integration`: OIDC、身份 Header、用户组、API Token 与应用间用户委托。
- `lazycat-aipod-developer`: AI Pod 资源、Orin/Thor 配置、浏览器插件和启动进度。
- `lazycat-android-webview-bridge`: Android 宿主提示和下载提示等 WebView 桥接能力。

总入口与专题技能均按需读取参考文档；六个涉及平台配置的技能各自携带规范校准工具，可独立安装。Android WebView 桥接技能仅处理 Android 宿主能力。

## 官方规范校准

写配置或执行构建、部署前，AI 应先确认目标系统与 CLI 版本，读取所在技能的 `references/spec-sync.md`，获取官方原文并比对本地快照。

来源优先级为[官方文档源仓库](https://gitee.com/lazycatcloud/lzc-developer-doc)、[官方开发手册](https://developer.lazycat.cloud/)、技能内参考快照。工具会记录实际来源和原文 SHA-256，拒绝 HTTP 错误、空正文及冒充 Markdown 的 HTML 页面；在线来源均不可用时明确声明使用离线快照。AI Pod 还需核对独立专题。

通用手册最近一次完整同步基线为 `82702da425c5f5324318fc2a75b9ef20bb1311af`（2026-10-30）；2026-11-07 另行在线核对了 package、manifest、文件选择器和上架补充条款，原文摘要见对应参考页与 [CHANGELOG](CHANGELOG.md)。参考文档会过期，使用时仍须重新校准。

## 仓库维护

`skills/<技能名>/` 是技能源码，`SKILL.md` 定义执行规则，`references/` 提供按需加载的规范。`skills/<技能名>.skill` 是由源码生成的 ZIP 分发包，修改技能后必须同步更新。

使用 Python >= 3.10、Node >= 20，在仓库根目录执行：

```bash
python3 -m pip install -r scripts/requirements-check.txt
python3 -B -m unittest discover -s scripts/tests -p 'test_*.py' -v
node scripts/build-skills.mjs
python3 -B scripts/check-repo.py
node scripts/build-skills.mjs --check
```

检查覆盖普通 YAML、双语应用示例、默认 usage、Bash 语法、共享副本、文档引用、安全边界和分发包一致性。Go template 与 `#@build` 片段需另做真实渲染验证；本地检查通过不能代替真机安装、升级或功能测试。

修改共享参考文档时同步全部副本，变更记录写入 [CHANGELOG](CHANGELOG.md) 的 Unreleased。维护约束见 [AGENTS.md](AGENTS.md)。本仓库基于 [whoamihappyhacking/lazycat-skills](https://github.com/whoamihappyhacking/lazycat-skills) 维护。
