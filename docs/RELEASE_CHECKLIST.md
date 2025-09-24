# PyPI Release Checklist

Use this checklist before publishing a new release to PyPI.

## ✅ Pre-Release Checklist

### 📋 Code Quality
- [ ] All tests pass locally: `python -m pytest tests/ -v`
- [ ] No linting errors: `flake8 . --count --statistics`
- [ ] Code is properly formatted
- [ ] All dependencies are up to date
- [ ] Documentation is updated

### 📝 Version Management
- [ ] Version number follows semantic versioning (X.Y.Z)
- [ ] Version is updated in `pyproject.toml`
- [ ] CHANGELOG.md is updated with new features/fixes
- [ ] Git working directory is clean (no uncommitted changes)
- [ ] Currently on `main` branch

### 🔧 Package Configuration
- [ ] `pyproject.toml` contains correct metadata
- [ ] `requirements.txt` is up to date
- [ ] `MANIFEST.in` includes all necessary files
- [ ] `LICENSE` file is present
- [ ] `README.md` contains installation instructions

### 🧪 Testing
- [ ] Package builds without errors: `python -m build`
- [ ] Package passes twine check: `python -m twine check dist/*`
- [ ] Tested with fresh virtual environment
- [ ] Command line interface works: `stock-recommender AAPL`

## 🚀 Release Process

### Automatic Release (Recommended)
1. [ ] Run preparation script: `./scripts/prepare_release.sh X.Y.Z --dry-run`
2. [ ] If dry run passes, run: `./scripts/prepare_release.sh X.Y.Z`
3. [ ] Go to GitHub Releases page
4. [ ] Create new release for tag `vX.Y.Z`
5. [ ] Add release notes
6. [ ] Publish release
7. [ ] Monitor GitHub Actions for automatic PyPI publishing

### Manual Release (Fallback)
1. [ ] Update version in `pyproject.toml`
2. [ ] Commit and tag: `git tag vX.Y.Z`
3. [ ] Push: `git push origin main --tags`
4. [ ] Build: `python -m build`
5. [ ] Check: `python -m twine check dist/*`
6. [ ] Upload to TestPyPI: `python -m twine upload --repository testpypi dist/*`
7. [ ] Test installation from TestPyPI
8. [ ] Upload to PyPI: `python -m twine upload dist/*`

## 📊 Post-Release Checklist

### 🔍 Verification
- [ ] Package appears on PyPI: https://pypi.org/project/us-stock-recommender/
- [ ] Installation works: `pip install us-stock-recommender`
- [ ] Command line works: `stock-recommender --help`
- [ ] Import works: `python -c "import stock_recommender; print('OK')"`

### 📢 Communication
- [ ] Update project documentation
- [ ] Announce release on relevant platforms
- [ ] Update any dependent projects
- [ ] Monitor for user feedback

### 🏷️ GitHub
- [ ] Release is created on GitHub
- [ ] Release notes are complete
- [ ] GitHub Actions completed successfully
- [ ] Package artifacts are attached to release

## 🚨 Rollback Plan

If issues are discovered after release:

1. [ ] Identify the problem
2. [ ] Create hotfix branch if needed
3. [ ] Prepare patch version (X.Y.Z+1)
4. [ ] Follow release process for patch
5. [ ] Consider yanking problematic version from PyPI if critical

## 📞 Support

- **GitHub Issues**: https://github.com/lvyongyu/us-stock-recommender/issues
- **PyPI Help**: https://pypi.org/help/
- **Packaging Guide**: https://packaging.python.org/

---

**Note**: Always test releases on TestPyPI first before publishing to production PyPI.
