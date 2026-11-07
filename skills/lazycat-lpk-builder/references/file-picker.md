# 网盘自动拦截文件选择器

有上传／下载功能的商店应用必须接入网盘自动拦截文件选择器。应用已有浏览器文件入口、希望通过 inject 接入而不修改上游源码时，使用本指南。审核规则见[官方上架补充要求](https://developer.lazycat.cloud/store-rule.html)。生成配置前先执行同技能 `references/spec-sync.md` 校准目标版本。

上架前必须执行第四节的功能验收；只下载脚本或只增加 browser inject，均不算完成接入。

## 一、准备脚本与构建内容

前置条件：目标 lzcos 支持 `browser` / `request` inject 和 `ctx.proxy`；字段及 API 见[官方脚本注入说明](https://developer.lazycat.cloud/advanced-injects.html)。

在应用项目根目录下载官方脚本：

```bash
mkdir -p content/lazycat-injects
curl -fL https://developer.lazycat.cloud/lazycat-injects/lzc-file-chooser-inject.js \
  -o content/lazycat-injects/lzc-file-chooser-inject.js
```

将脚本放入 `lzc-build.yml` 的 `contentdir` 指向的目录。例如使用上述目录时，构建配置设 `contentdir: ./content`，脚本打包后位于 `/lzcapp/pkg/content/lazycat-injects/lzc-file-chooser-inject.js`。已有构建目录的应用按原布局复制脚本，保留原有构建字段；详见[官方构建配置](https://developer.lazycat.cloud/spec/build.html)。

## 二、配置两条 inject

将以下片段合并进现有 `application.injects`，保留应用原有的 routes、services 和其他配置。request bridge 与 browser inject 必须同时配置：

```yml
application:
  injects:
    - id: lazycat-file-bridge
      on: request
      when:
        - /__lazycat_file_bridge/*
      do:
        - src: |
            const bridgePrefix = "/__lazycat_file_bridge";
            const requestHost = String(ctx.request.host || "")
              .split(":")[0]
              .toLowerCase();
            const firstDot = requestHost.indexOf(".");
            const method = String(ctx.request.method || "").toUpperCase();

            if (
              firstDot <= 0 ||
              !requestHost.endsWith(".heiyu.space") ||
              !["GET", "HEAD", "PUT"].includes(method)
            ) {
              ctx.response.send(
                ["GET", "HEAD", "PUT"].includes(method) ? 400 : 405,
                "Invalid LazyCat file bridge request",
              );
              return;
            }

            const boxDomain = requestHost.slice(firstDot + 1);
            const fileOrigin = "https://file." + boxDomain;
            const targetPath =
              "/files/home" + ctx.request.path.slice(bridgePrefix.length);

            ctx.headers.del("Origin");
            ctx.headers.del("Referer");
            ctx.proxy.to(fileOrigin, {
              path: targetPath,
              query: ctx.request.raw_query,
              use_target_host: true,
              timeout_ms: 120000,
              on_fail: "error",
            });
    - id: open-save-chooser
      on: browser
      when:
        - /*
      do:
        - src: file:///lzcapp/pkg/content/lazycat-injects/lzc-file-chooser-inject.js
          params:
            diskRoot: /_lzc/files/home
            fileBridgeRoot: /__lazycat_file_bridge
            locale: auto
            hooks:
              fileSystemAccess: true
              fileInput: true
              downloadAnchor: true
```

桥接目标由当前应用域名推导为 `file.<微服域名>.heiyu.space`，只接受 `GET` / `HEAD` / `PUT`。保留 Cookie、`Owner`、`If-None-Match`、`Content-Type`、请求正文和查询参数，使网盘鉴权及共享目录访问正常工作；不接受调用方任意指定代理目标。

## 三、覆盖范围与参数

- 打开：`showOpenFilePicker()` 和 `<input type="file">`；从网盘打开的句柄支持后续写回。
- 保存：`showSaveFilePicker()`，以及带 `download` 属性的 `blob:` / `data:` 链接；网盘使用 `saveAs` / `saveNames` 管理文件名，并显示上传进度。
- 当前只处理 `/files/home`。目录选择、普通 HTTP 下载、应用直接发起的 `fetch` / `PUT` 需要单独接入，不能假定自动覆盖。
- `fileBridgeRoot` 必须与 request inject 的 `bridgePrefix` 一致；`diskRoot` 默认 `/_lzc/files/home`。
- 参数位于 `do[].params`。`locale: auto` 按浏览器语言选择中文或英文；`text` 支持 `zh-CN` / `en-US` 分组以及顶层覆盖，顶层优先。
- `hooks.fileSystemAccess` / `hooks.fileInput` / `hooks.downloadAnchor` 默认均为 `true`。完整文案键与 `fallbackMime` 见官方原文。

## 四、验证与排错

1. 触发打开／保存，确认统一窗口内可选择“网盘文件／本地文件”；本地选择继续应用原流程。
2. 保存到网盘，确认建议文件名可修改，能看到上传进度。
3. 选择他人共享且可写的目录保存，确认请求走应用同源 `/__lazycat_file_bridge/`，并包含选择器返回的 `Owner`。
4. 缺少 request bridge 时，自己的目录可能仍可用，但共享目录会失败；请求仍走 `/_lzc/files/home/` 时检查脚本版本与桥接配置。
5. 新建文件携带 `If-None-Match: *` 时，`412 Precondition Failed` 才表示同名冲突，官方脚本追加序号重试；`409 Conflict` 表示路径或父目录冲突，直接报错。
6. `401` 或跳转登录页时，检查页面是否已登录及 bridge 是否保留 Cookie。文件名出现两个输入框时更新官方脚本，由选择器统一管理文件名。

## 官方来源

- [自动拦截文件选择器](https://developer.lazycat.cloud/lazycat-file-picker-auto-intercept.html)
- [上架审核补充规则](https://developer.lazycat.cloud/store-rule.html)
- 核对日期：2026-11-07；[官方 raw 原文](https://gitee.com/lazycatcloud/lzc-developer-doc/raw/master/docs/lazycat-file-picker-auto-intercept.md)，SHA-256：`6171dca4e0cf7134eaa710a0e02921c1fd02c3c54b056c58ae6fbe5e2ee81090`。
