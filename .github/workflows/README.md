# GitHub Actions Workflows

This project uses multiple GitHub Actions workflows to handle automated tasks at different stages.

> **English Version**: README.md | **中文版本**: [README.zh.md](./README.zh.md)

## 📋 Workflows Overview

### 1. `ci.yml` - Continuous Integration
**Triggers**:
- Push to `main` or `develop` branch
- Pull Requests to `main` branch

**Features**:
- ✅ Run tests on multiple Python versions (3.8-3.12)
- 🔍 Code quality checks (flake8)
- 📦 Build packages and upload artifacts
- 🔄 Ensure code quality and compatibility

### 2. `test-build.yml` - Test Build
**Triggers**:
- Push to `main` branch (only when key files change)
- Pull Requests
- Manual trigger

**Features**:
- 🧪 Quick build testing
- 📝 Validate package configuration
- 🔧 Optional publish to TestPyPI (manual trigger only)

### 3. `release.yml` - Production Release
**Triggers**:
- GitHub Release creation

**Features**:
- ✅ Comprehensive testing (multi-version Python)
- 📦 Build production packages
- 🚀 Publish to PyPI
- 📎 Upload build artifacts to Release

## 🔄 Complete Release Process

### Development Phase
1. **Code Commit** → Triggers `ci.yml`
2. **Pull Request** → Triggers `ci.yml` and `test-build.yml`
3. **Merge to main** → Triggers `ci.yml`

### Release Phase
1. **Prepare Release**:
   ```bash
   ./scripts/prepare_release.sh 1.0.1
   ```

2. **Create GitHub Release**:
   - Go to GitHub Releases page
   - Create release with tag `v1.0.1`
   - Add release notes
   - Publish → Automatically triggers `release.yml`

3. **Monitor Release**:
   - Check Actions tab for workflow progress
   - Verify PyPI publication
   - Test installation: `pip install us-stock-recommender`

## 🔐 Required Secrets

Configure in Repository Settings → Secrets and variables → Actions:

| Secret Name | Purpose | Where to Get |
|-------------|---------|--------------|
| `PYPI_API_TOKEN` | PyPI production publishing | [PyPI Account Settings](https://pypi.org/manage/account/) |
| `TEST_PYPI_API_TOKEN` | TestPyPI testing | [TestPyPI Account Settings](https://test.pypi.org/manage/account/) |

## 📊 Workflow Dependencies

```
Development Flow:
Push/PR → ci.yml → test-build.yml (optional)

Release Flow:
Create Release → release.yml → PyPI Publication
```

## 🚨 Troubleshooting

### Common Issues
1. **Test Failures**: Check CI logs for specific errors
2. **Build Failures**: Verify `pyproject.toml` configuration
3. **PyPI Upload Failures**: 
   - Check API token validity
   - Ensure version number is unique
   - Verify package name availability

### Manual Interventions
- **Skip CI**: Add `[skip ci]` to commit message
- **Force Rebuild**: Re-run failed workflows from Actions tab
- **Emergency Release**: Use manual trigger in `release.yml`

## 📚 Related Documentation

- [PyPI Publishing Guide](../docs/PYPI_PUBLISHING_GUIDE.md)
- [Release Checklist](../docs/RELEASE_CHECKLIST.md)
- [Strategy Analysis](../docs/STRATEGY_ANALYSIS.md)

## 🔍 Monitoring & Analytics

### Key Metrics to Monitor
- ✅ Test pass rates across Python versions
- 📦 Build success rates
- 🚀 Release deployment frequency
- 📈 PyPI download statistics

### Best Practices
- Always test locally before pushing
- Use TestPyPI for pre-release testing
- Follow semantic versioning (Major.Minor.Patch)
- Keep dependencies updated
- Monitor security vulnerabilities

---

**Quick Start**: For your first release, follow the [Release Checklist](../docs/RELEASE_CHECKLIST.md) step by step.

*For detailed publishing instructions, see [PyPI Publishing Guide](../docs/PYPI_PUBLISHING_GUIDE.md)*
