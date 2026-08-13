# Windows 构建说明

## 已验证环境

- Windows x64
- Visual Studio Build Tools 2022
- MSVC 19.44 / v143
- Windows SDK 10.0.26100.0
- Visual Studio 内置 CMake 3.31.6

建议使用 Visual Studio 自带的 CMake，或将 `cmake.exe` 放在可访问路径中。
不要使用 CMake 4.x 构建旧版第三方依赖。

## 构建命令

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\build-windows.ps1 `
  -ToolchainRoot "C:\Program Files\Microsoft Visual Studio\2022\BuildTools" `
  -BuildDir "$env:TEMP\VSP-Chinese-build" `
  -Jobs 1
```

构建目录应放在仓库外，避免污染 Git 工作区。脚本完成后，运行目录位于 `dist\OpenVSP-3.51.2-zh-CN-win64`。

## 运行时词典

程序优先读取 `vsp.exe` 同级目录下的 `translations\zh-CN.json`。Windows 中文路径受支持，也可通过 `OPENVSP_TRANSLATIONS` 环境变量指定词典绝对路径。

## 常见问题

- `C1060 编译器堆空间不足`：使用 `-Jobs 1`，不要恢复全局 `/MP`。
- CMake 4.x 策略错误：使用 Visual Studio 自带的 CMake 3.31.6。
- GUI 未显示中文：确认 `translations\zh-CN.json` 与 `vsp.exe` 的相对位置正确。
- 缺少 DLL：必须分发完整 `dist\OpenVSP-3.51.2-zh-CN-win64` 目录，而不是单独复制 `vsp.exe`。
