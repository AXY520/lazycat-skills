# LPK V2 打包与移植流程

本文件与 lazycat-lpk-builder/SKILL.md 的核心流程同步；详细字段以本技能携带的共享 references 为准，不依赖同时安装其他技能。

## 0. 规范校准

写/改 package、manifest、build 或执行 build/deploy/release 前，**必须读取并执行 `references/spec-sync.md`**。记录目标 lzcos/CLI 版本，获取官方原文，核对快照并声明差异。基线 lzcos >=1.5.0 + lzc-cli >=2.0.0，各新能力另核验门槛；网络失败只能显式声明快照降级，不能声称校准成功。

## 应用产物约束

- **仅支持 LPK V2**：V1 项目先迁移到 V2；目标低于 lzcos 1.5.0 或 lzc-cli 2.0.0 时说明升级要求，不生成 V1 包或降级配置。
- **完整中英文本地化**：完整 `package.yml` 必须填写 `locales.zh-CN` 与 `locales.en-US`，两种语言均有非空且语义对应的 `name`、`description`；不能用顶层回退代替。已声明入口的标题也按官方本地化规则补齐两种语言。
- **usage 由用户选择**：仅在用户明确要求使用须知时添加 manifest 顶层 `usage` 及 `locales.*.usage`，届时同时提供中英文；默认连空字段也不添加。保留用户已有内容，不擅自扩写。
- **上架前落实适配**：核对当前审核要求；有上传／下载功能时必须接入[官方网盘文件拦截](https://developer.lazycat.cloud/lazycat-file-picker-auto-intercept.html)，同时配置 browser inject 与同源 request bridge，实际验证本地文件、网盘及共享目录。

## 1. 需求与配置

分析架构、端口/协议、镜像入口/UID、依赖、内部数据与用户文件、业务鉴权和最小权限。按需读取：

| 文件/问题 | 参考 |
| --- | --- |
| package.yml：身份、版本、权限 | `references/package-spec.md` |
| lzc-manifest.yml：运行结构 | `references/manifest-spec.md` |
| lzc-build.yml / lzc-build.dev.yml | `references/build-spec.md` |
| 静态资源导入/导出 | `references/resource-export.md` |
| 权限、初始化、持久化、探针 | `references/troubleshooting.md` |
| 发布与审核要求 | `references/store-publish.md` |
| 上传／下载接入网盘文件选择器 | `references/file-picker.md` |

V2 静态元数据、权限、import_resources 不放 manifest 顶层。dev 只保留差异；package_override 按顶层整体覆盖；image-only 可不带内容归档。buildscript 不得调用 project build。

## 2. 打包、验收与授权

```bash
lzc-cli --version
lzc-cli project release -o release.lpk
```

核查 Build config、tar 内 package.yml/manifest.yml、content 与 resource/镜像 lock。带 #@build/Go template 的文件按真实阶段渲染后严格检查，不接受重复键或把模板替换为任意值后就宣称应用可运行。

只有授权后安装/开发部署：

```bash
lzc-cli app install ./release.lpk
lzc-cli project deploy
```

验证首装、升级、重启、数据、权限、免密登录与业务接口。用 `lzc-cli docker` 查看应用；需微服名时执行 `lzc-cli box default`。本地校验和真实部署必须分开报告。

## 3. 护栏

- 内部数据放 var，可重建缓存放 cache；用户文件使用有权限的 `/lzcapp/documents/$uid`；不默认旧 home 挂载。
- 数字 run_as（>=1.6.0）需兼容镜像入口，不与同 service 的 user/setup_script 混用；不默认 root/privileged。
- routes 默认裁前缀，保留用 upstreams；非 HTTP 用 ingress，不随意接管 80/443。
- 开发机代理需要 via.client 和 ctx.dev.id，参见 build-spec 的完整模板。
- 服务 `.lzcapp` DNS 不是用户委托入口；代表真实用户互访读取 `references/app-interconnect.md`。
- public_path 不代替业务鉴权；远端发布、提权和凭据操作须明确授权。

交付写明校准来源/摘要、目标版本、包位置、实际验证、未验证项与需授权动作。
