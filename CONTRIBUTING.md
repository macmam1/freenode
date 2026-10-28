# Contributing to FreeNode

Thank you for considering contributing! This document explains the workflow.

## 🎯 Core Principles

1. **Archive Everything** — Never delete old test results
2. **Test Before Merge** — Every platform must have a test result
3. **Document Everything** — If it's not documented, it doesn't exist
4. **Modular Design** — One module, one responsibility

## 📝 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b platform/render-test
```

### 2. Make Changes

- Add platform detection logic to `src/core/detector.py`
- Update strategy in `src/core/stratifier.py`
- Test on target platform
- Document in `docs/test-registry/`

### 3. Test

```bash
python cli.py diagnose    # Detect environment
python cli.py init        # Generate profile
python cli.py test <platform>  # Run test
```

### 4. Commit

```bash
git add .
git commit -m "feat: add <platform> detection"
# or
git commit -m "test: <platform> <result>"
```

### 5. Push

```bash
git push origin <branch>
```

### 6. Pull Request

- Target: `main` branch
- Title: `[type] description`
- Include test results

## 🧪 Adding New Platform

### 1. Add detection logic

```python
# src/core/detector.py
def _detect_platform(self, r):
    if 'NEWPLATFORM_ENV' in str(r):
        return 'newplatform'
```

### 2. Update Stratifier

```python
# src/core/stratifier.py
PLATFORM_CLASSES = {
    'containerized': [..., 'newplatform'],
}
```

### 3. Add strategy

```python
def load_platform_strategies():
    return {
        'newplatform': {
            'class': 'containerized',
            'modules': ['keepalive', 'tunnel'],
            'tunnel': ['sshx', 'cloudflare'],
            'keepalive_interval': 600,
            'notes': 'Platform-specific notes'
        }
    }
```

### 4. Test on platform

```bash
python cli.py test newplatform
```

### 5. Document result

Create file: `docs/test-registry/newplatform-YYYY-MM-DD.md`

## 📋 Test Registry Rules

1. **Never delete** old test files
2. **Always archive** results in `docs/test-registry/`
3. **Tag every test** commit: `test-<platform>-<date>`
4. **Document failures** as well as successes
5. **Include logs** when available

## 🏷️ Commit Message Convention

```
<type>: <subject>

Types:
- feat: new feature
- fix: bug fix
- docs: documentation
- test: test addition
- refactor: code refactoring
- platform: platform-specific addition
```

## 🔒 Security Guidelines

- Never commit secrets, tokens, or credentials
- Use environment variables
- Use `.gitignore` to exclude sensitive files
- Mask sensitive data in logs

## 🤝 Questions?

Open an issue on GitHub or reach out via discussions.

---

**License:** MIT — See `LICENSE` for details.
