# PyPI Publishing Guide

This guide explains how to publish the US Stock Recommender package to PyPI.

## 📋 Prerequisites

### 1. PyPI Account Setup
1. Create accounts on both [PyPI](https://pypi.org/account/register/) and [TestPyPI](https://test.pypi.org/account/register/)
2. Enable 2FA (Two-Factor Authentication) on both accounts
3. Generate API tokens:
   - PyPI: Go to Account Settings → API tokens → Add API token
   - TestPyPI: Go to Account Settings → API tokens → Add API token

### 2. GitHub Secrets Configuration
Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

```
PYPI_API_TOKEN=pypi-your-production-token-here
TEST_PYPI_API_TOKEN=pypi-your-test-token-here
```

## 🚀 Publishing Methods

### Method 1: Automatic Release (Recommended)

This is the recommended approach using GitHub Actions:

1. **Prepare the release:**
   ```bash
   # Test the release preparation (dry run)
   ./scripts/prepare_release.sh 1.0.1 --dry-run
   
   # Actually prepare the release
   ./scripts/prepare_release.sh 1.0.1
   ```

2. **Create GitHub Release:**
   - Go to [GitHub Releases](https://github.com/lvyongyu/us-stock-recommender/releases)
   - Click "Create a new release"
   - Select the tag (e.g., `v1.0.1`)
   - Fill in the release title and description
   - Click "Publish release"

3. **Automatic Publishing:**
   - GitHub Actions will automatically run tests
   - If tests pass, the package will be published to PyPI
   - Check the Actions tab for progress

### Method 2: Manual Publishing

If you prefer to publish manually:

1. **Install build tools:**
   ```bash
   pip install build twine
   ```

2. **Build the package:**
   ```bash
   python -m build
   ```

3. **Check the package:**
   ```bash
   python -m twine check dist/*
   ```

4. **Upload to TestPyPI (recommended first):**
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

5. **Test installation from TestPyPI:**
   ```bash
   pip install --index-url https://test.pypi.org/simple/ us-stock-recommender
   ```

6. **Upload to PyPI:**
   ```bash
   python -m twine upload dist/*
   ```

## 📦 Package Structure

The package is configured with modern Python packaging standards:

```
us-stock-recommender/
├── pyproject.toml          # Modern Python packaging configuration
├── MANIFEST.in             # Additional files to include
├── LICENSE                 # MIT License
├── README.md              # Package description
├── src/                   # Source code
├── stock_recommender.py   # Main entry point
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## 🔧 Configuration Files

### pyproject.toml
Contains all package metadata, dependencies, and build configuration:
- Package name: `us-stock-recommender`
- Python version requirement: `>=3.8`
- All dependencies from `requirements.txt`
- Entry point: `stock-recommender` command
- Development and testing dependencies

### MANIFEST.in
Specifies additional files to include in the distribution:
- Documentation files
- License
- Configuration files
- Excludes cache files and development artifacts

## 🧪 Testing the Package

### Local Testing
```bash
# Install in development mode
pip install -e .

# Run tests
python -m pytest tests/

# Test the command line interface
stock-recommender AAPL
```

### TestPyPI Testing
```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ us-stock-recommender

# Test functionality
python -c "import stock_recommender; print('Package imported successfully')"
```

## 🏷️ Version Management

### Semantic Versioning
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Version Update Process
1. Update version in `pyproject.toml`
2. Commit the change
3. Create a git tag: `git tag v1.0.1`
4. Push tag: `git push origin v1.0.1`

## 📊 Package Information

### Package Details
- **Name**: `us-stock-recommender`
- **Description**: A comprehensive US stock recommendation system
- **Author**: Eric (lvyongyu)
- **License**: MIT
- **Python Support**: 3.8+
- **Categories**: Finance, Investment, Machine Learning

### Installation
After publishing, users can install with:
```bash
pip install us-stock-recommender
```

### Usage
```bash
# Command line usage
stock-recommender AAPL

# Python usage
from stock_recommender import main
```

## 🚨 Troubleshooting

### Common Issues

1. **Version already exists on PyPI:**
   - Increment the version number
   - Re-run the release preparation script

2. **Package name conflict:**
   - The name `us-stock-recommender` should be unique
   - If conflict occurs, consider `us-stock-recommender-ai` or similar

3. **GitHub Actions failing:**
   - Check the Actions tab for detailed logs
   - Verify all secrets are correctly set
   - Ensure tests pass locally first

4. **Import errors after installation:**
   - Check the package structure in `pyproject.toml`
   - Verify all dependencies are correctly specified

### Testing Commands
```bash
# Test package building
python -m build

# Test package checking
python -m twine check dist/*

# Test installation from wheel
pip install dist/us_stock_recommender-*.whl

# Test uninstallation
pip uninstall us-stock-recommender
```

## 📈 Monitoring

### After Publishing
- Check [PyPI package page](https://pypi.org/project/us-stock-recommender/)
- Monitor download statistics
- Watch for user feedback and issues
- Update documentation as needed

### Package Maintenance
- Regular dependency updates
- Security vulnerability monitoring
- Python version compatibility updates
- Feature enhancements based on user feedback

---

## 🔗 Useful Links

- [PyPI Project Page](https://pypi.org/project/us-stock-recommender/)
- [TestPyPI Project Page](https://test.pypi.org/project/us-stock-recommender/)
- [GitHub Repository](https://github.com/lvyongyu/us-stock-recommender)
- [GitHub Actions Workflows](https://github.com/lvyongyu/us-stock-recommender/actions)
- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)

---

*This guide covers the complete PyPI publishing workflow. For questions or issues, please open an issue on the GitHub repository.*
