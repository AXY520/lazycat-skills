# 应用商店上架与发布

来源：[发布流程](https://developer.lazycat.cloud/publish-app.html)、[上架审核指南](https://developer.lazycat.cloud/store-submission-guide.html)。提交前执行 `references/spec-sync.md` 并读取当前原文；以下是检查清单，不是“保证审核通过”。

本仓库只交付 LPK V2。上架前先检查完整中英文 `locales`，仅在用户明确要求时添加 `usage`；包含文件上传／下载功能时，文件拦截是必做接入项。

## 1. 准备与镜像

1. 注册[社区账号](https://lazycat.cloud/login?redirect=https://developer.lazycat.cloud/)，到[开发者中心](https://developer.lazycat.cloud/manage)申请开发者资格。
2. 核实镜像版本、架构、许可证、持久化和首次登录。普通外部镜像上架前依官方要求复制到 registry.lazycat.cloud，并在源 manifest 中替换为实际返回地址。
3. copy-image 在服务端 pull，不能上传仅存在于本机的私有镜像；内嵌镜像方案按当前商店政策另行核验，不假定免审。

```bash
# 官方演示镜像；实际提交使用已核实版本的目标镜像
lzc-cli appstore copy-image alpine:3.18
```

命令输出形如 `registry.lazycat.cloud/<社区用户名>/<镜像>:<内容tag>`。不要在可执行 shell 示例中把尖括号占位符当作真实参数，也不要把示例 tag 当作当前最新。

官方仓库限制：tag 按镜像 ID 固化；服务端强制 pull；镜像须公网可访问；未被商店应用引用的镜像可能被回收；仓库仅供微服使用，外部有访问限速。

## 2. 上架审核要求

1. **资料完备**：logo、名称、描述、截图齐全；package.yml 中 `locales.zh-CN` 与 `locales.en-US` 均须完整填写 `name`、`description`，已声明的入口标题也须有两种语言。`usage` 仅在用户明确要求时添加，届时同时提供中英文；未要求时不生成任何 usage 字段。
2. **可安装与加载**：测试首装、依赖可达、首次加载及加载响应。
3. **质量稳定**：无严重崩溃、闪退。
4. **速度**：启动、响应不超过五分钟；不要无限健康等待。
5. **场景适配**：硬件功能真机测试并提供型号；特殊场景实测；不支持应用内更新时去掉干扰性更新提示。
6. **场景有效**：有真实用户用途；开发库/中间件原则上不允许单独上架；工具应关联相关文件类型。
7. **数据持久化**：重启、升级后数据不丢；实例模式改变须数据迁移/恢复方案。
8. **免密登录**：支持 OIDC 或 inject 自动填充/学习等官方机制；用户首次/后续登录应满足官方弱感知体验要求。必须实际验证，不能只加一段 inject 就声称支持。
9. **上传／下载**：必须接入懒猫网盘自动拦截文件选择器，未接入无法上架。读取同技能 `references/file-picker.md`，同时配置 browser inject 与同源 request bridge，并验证共享目录 `Owner` 转发；覆盖范围外的文件入口需单独接入。依据：[上架审核补充要求](https://developer.lazycat.cloud/store-rule.html)、[自动拦截文件选择器](https://developer.lazycat.cloud/lazycat-file-picker-auto-intercept.html)。

免密依据：[OIDC](https://developer.lazycat.cloud/advanced-oidc.html)、[免密专题](https://developer.lazycat.cloud/advanced-inject-passwordless-login.html)。若上游需要业务账号，必须说明账号创建/凭据来源、隔离与改密路径，避免所有用户共享高权限账号。

主观审核还要求应用有实用性和合格界面；与已上架应用高度相似时原则上不通过，有显著创新或补足未满足需求的可酌情通过。仅英文界面／指南且缺少必要本地化的应用不予上架，热门且高质量项目由审核人员裁定；复杂应用须提供详尽用户指南；指南随交付文档提供，不据此自行新增首次访问的 `usage`。需要业务账号时，普通用户须能获取对应凭据。

## 3. 构建、验证与提交

**LPK V2 构建要求 lzc-cli >=2.0.0、lzcos >=1.5.0**。官方发布页中的 CLI 1.2.54 是历史 appstore 提交能力门槛，不能替代 V2 构建门槛。

```bash
lzc-cli --version
lzc-cli project release -o release.lpk
# 完成安装、升级、权限、免密登录、真实设备测试后，经用户授权再提交：
lzc-cli appstore publish ./release.lpk
```

不要因用户只让“构建/审核”就直接发布或安装；这些动作会影响远端状态。发布前交付校准来源、包名/版本、使用能力版本门槛、测试结论、未验证项与待授权动作。

高权限 override、硬件/特定模型兼容等必须说明风险并按官方要求沟通。违法、破解等不合规应用不能上架；不得宣称特殊权限功能一定通过审核。
