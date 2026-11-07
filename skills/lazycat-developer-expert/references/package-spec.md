# package.yml：LPK V2 元数据与权限

本文件是常用项摘要，写配置前先执行 `references/spec-sync.md`。完整依据：[官方 package 规范](https://developer.lazycat.cloud/spec/package.html)。本技能仅支持 LPK V2，要求 **lzcos >=1.5.0、lzc-cli >=2.0.0**；遇到 V1 项目先迁移，不提供 V1 打包。

2026-11-07 重新读取官方 raw（master）；原文 SHA-256：`464056bd9ba621e55ac8506c256a94ebad5b8d8f06752c156a8d27cce154cf14`。

## 1. 文件边界

`package`、`version`、`name`、`description`、`author`、`license`、`homepage`、`admin_only`、`hidden_from_launcher`、`min_os_version`、`unsupported_platforms`、`locales`、`permissions`、`import_resources` 写入 **package.yml**，不要写到 V2 manifest 顶层。

- `package`、`version` 是最小必填字段；包 ID 和 `application.subdomain` 不是一回事。
- `version` 用字符串；建议语义化版本。`unsupported_platforms` 的取值依据目标平台规范，不凭示例猜测。
- `hidden_from_launcher`（>=1.5.3）只隐藏启动器入口，不改变地址、权限或部署行为。
- `min_os_version` 应不低于实际使用能力的最低版本。
- 本技能的完整应用产物必须包含 `locales.zh-CN` 与 `locales.en-US`；平台支持的顶层回退不能替代本仓库要求的完整双语内容。

## 2. 中英文本地化与使用须知

官方 schema 允许省略 `locales` 及其中字段；**本仓库交付规则更严格**，完整应用配置必须满足：

1. `locales.zh-CN` 与 `locales.en-US` 都有非空 `name`、`description`，两种语言内容准确对应；产品专名可保持原名，描述必须提供实际翻译。不能只写其中一组、空串或占位翻译。
2. 顶层 `name` / `description` 作为平台回退值保留；不依赖回退来省略任一语言。其他语言可按需追加。
3. 已声明 `application.entries` 时，按目标版本官方 `entries.<id>.title` 规则补齐两种语言的入口标题，入口 ID 必须一致。
4. **用户未明确要求时，省略 manifest 顶层 `usage` 和所有 `locales.<lang>.usage`，也不添加空串。**它是首次访问时渲染的使用须知，不是默认生成的应用介绍、版权声明或部署日志。
5. 用户明确要求使用须知后，按其要求填写 manifest 顶层 `usage`，并在 `package.yml.locales.zh-CN/en-US` 同时填写对应译文；不把本地化配置放回 V2 manifest。编辑现有项目时保留用户已有内容，不擅自删除或扩写。
6. 只展示权限、资源或构建覆盖的局部片段可保持局部；一旦输出完整应用包，或合并为最终 `package.yml`，必须通过以上检查。`package_override.locales` 是顶层整体替换，应同时保留完整双语信息。

使用须知及入口标题的官方字段见[manifest 本地化](https://developer.lazycat.cloud/spec/manifest.html#i18n)。

## 3. 最小权限

`permissions` 是**开发者声明**，不是最终授权结果。官方 schema 中可省略，但技能生成配置时必须审计所有功能所需权限：未声明权限不能使用，未知 ID 非法，同一 ID 不得同时在 required/optional 中出现。无权限需求时可以显式声明空列表，不能为了“保险”把全部权限设为 required。

| 类别 | 常用合法 ID |
| --- | --- |
| 网络 | `net.internet`、`net.lan`、`net.host`、`net.admin` |
| 文稿/媒体 | `document.private`、`document.read`、`document.write`、`media.read`、`media.write` |
| 设备 | `device.dri.render`、`device.dri.master`、`device.usb`、`device.kvm`、`device.block`、`vt.display` |
| 挂载 | `fuse.mount`（>=1.6.1） |
| 跨应用数据 | `appvar.other.read`、`appvar.other.write` |
| 高危运行时覆盖 | `compose.override` |
| 电源 | `power.shutdown.inhibit` |
| LightOS | `lightos.use`、`lightos.manage` |
| 通知 | `user.notify`（>=1.6.0） |

- `document.private`：`/lzcapp/documents/$uid`，按用户隔离，卸载默认不删除；只放用户可理解、可管理的文件。数据库、索引、内部配置放 `/lzcapp/var`，不滥用文稿权限。
- `fuse.mount`：系统注入 `/lzcinit/fusermount3` 并把 `/lzcinit` 加入 PATH；优先于直接 privileged。
- `vt.display`：还需 `application.vt: true`，且所有 service 不得使用 sysbox-runc。
- `user.notify`：容器内注入 `/lzcinit/notify-send`；不是客户端权限或配额声明。
- HTTP 代表用户访问自身/其他应用的 `lzcapp.self_delegate` / `lzcapp.user_delegate`，定义在[应用间访问专题](https://developer.lazycat.cloud/advanced-app-interconnect.html)。通用权限表与专题存在覆盖范围差异：按目标系统实际支持核实，不把跨应用数据文件权限当成 HTTP 委托权限。

## 4. 静态站元数据例子

```yaml
# package.yml
package: cloud.lazycat.app.demo
version: "1.0.0"
name: 示例静态站
description: 由 LPK 内容提供的静态页面
min_os_version: "1.5.0"
locales:
  zh-CN:
    name: 示例静态站
    description: 由 LPK 内容提供的静态页面
  en-US:
    name: Demo Static Site
    description: A static page served from LPK content
permissions:
  required: []
  optional: []
```

这里没有申请互联网或文稿权限，因为示例只托管包内内容。移植实际应用时按功能补充权限，不机械照抄空列表。

## 5. 导入资源（>=1.5.2）

```yaml
# package.yml 的可选片段
import_resources:
  - kind: skills
  - kind: mcp-providers
```

每个 kind 只能出现一次，系统只投影已声明类型：

- payload：`/lzcapp/run/resources/<kind>/<package-id>/<resource-id>/...`
- 汇总摘要：`/lzcapp/run/resources/.digest/<kind>/summary`
- 单资源摘要：`/lzcapp/run/resources/.digest/<kind>/<package-id>/<resource-id>/digest`

投影只读；不能假定存在额外 catalog。声明资源导入不等于获取其他应用的 HTTP/业务权限。导出与校验细节请读取 `references/resource-export.md`。
