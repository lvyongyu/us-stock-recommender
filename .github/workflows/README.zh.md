# GitHub Actions 工作流说明

本项目使用多个 GitHub Actions 工作流来处理不同阶段的自动化任务。

> **English Version**: [README.md](./README.md) | **中文版本**: README.zh.md

## 📋 工作流概览

### 1. `ci.yml` - 持续集成
**触发条件**：
- 推送到 `main` 或 `develop` 分支
- 对 `main` 分支的 Pull Request

**功能**：
- ✅ 在多个 Python 版本 (3.8-3.12) 上运行测试
- 🔍 代码质量检查 (flake8)
- 📦 构建包并上传构建产物
- 🔄 确保代码质量和兼容性

### 2. `test-build.yml` - 测试构建
**触发条件**：
- 推送到 `main` 分支（仅当关键文件改变）
- Pull Request
- 手动触发

**功能**：
- 🧪 快速测试构建
- 📝 验证包配置
- 🔧 可选择发布到 TestPyPI（仅手动触发）

### 3. `release.yml` - 正式发布
**触发条件**：
- 创建 GitHub Release

**功能**：
- ✅ 全面测试（多版本 Python）
- 📦 构建正式包
- 🚀 发布到 PyPI
- 📎 上传构建产物到 Release

## 🔄 完整发布流程

### 开发阶段
1. **代码提交** → 触发 `ci.yml`
2. **Pull Request** → 触发 `ci.yml` 和 `test-build.yml`
3. **合并到 main** → 触发 `ci.yml`

### 发布阶段
1. **准备发布**：
   ```bash
   ./scripts/prepare_release.sh 1.0.1
   ```

2. **创建 GitHub Release** → 自动触发 `release.yml`
   - 运行全套测试
   - 自动发布到 PyPI
   - 上传构建产物

## 🔐 所需的 Secrets

在 GitHub 仓库设置中配置以下 Secrets：

```
PYPI_API_TOKEN=pypi-your-production-token
TEST_PYPI_API_TOKEN=pypi-your-test-token  # 可选
```

### 如何获取 API Token：
1. 访问 [PyPI](https://pypi.org/account/register/) 或 [TestPyPI](https://test.pypi.org/account/register/)
2. 注册并启用 2FA
3. 去 Account Settings → API tokens → Add API token
4. 复制生成的 token 到 GitHub Secrets

## 🎯 工作流选择建议

### 如果您想要：
- **简单发布**：只保留 `ci.yml` 和 `release.yml`
- **测试驱动**：保留所有三个工作流
- **最小配置**：只保留 `release.yml`

### 推荐配置（当前）：
```
.github/workflows/
├── ci.yml          # 持续集成和质量检查
├── test-build.yml  # 可选的测试构建
└── release.yml     # 正式发布
```

## 📊 状态徽章

可以在 README.md 中添加状态徽章：

```markdown
![CI](https://github.com/lvyongyu/us-stock-recommender/actions/workflows/ci.yml/badge.svg)
![Release](https://github.com/lvyongyu/us-stock-recommender/actions/workflows/release.yml/badge.svg)
```

## 🔧 自定义配置

### 修改触发条件
如果您想修改工作流触发条件，编辑对应文件的 `on:` 部分。

### 调整 Python 版本
在 `strategy.matrix.python-version` 中修改支持的 Python 版本列表。

### 更改发布条件
可以修改 `release.yml` 来支持不同的触发条件，如标签推送。

---

**注意**：第一次设置时，请确保所有 Secrets 都正确配置，并在 TestPyPI 上进行测试发布。
