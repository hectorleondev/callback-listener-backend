# uv Package Manager Integration

The CallbackListener backend now uses [uv](https://docs.astral.sh/uv/) - a lightning-fast Python package manager written in Rust.

## 🚀 Why uv?

- **10-100x faster** than pip for package installation
- **Reliable dependency resolution** with conflict detection
- **Better caching** for faster repeated installs
- **Modern Python tooling** with excellent UX

## 📦 Installation

### Install uv (one-time setup)
```bash
# macOS, Linux, WSL
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with homebrew
brew install uv

# Or with pip
pip install uv
```

### Verify installation
```bash
uv --version
# uv 0.7.9 (13a86a23b 2025-05-30)
```

## 🛠️ Usage with CallbackListener

### Basic Operations
```bash
# Install all dependencies (uses uv automatically)
make install

# Add a new package
make add-package pkg=requests

# Remove a package  
make remove-package pkg=requests

# Update all dependencies
make update-deps

# Sync exact dependencies
make sync-deps
```

### Manual uv Commands
```bash
# Install dependencies directly
uv pip install -r requirements.txt

# Add package and update requirements
uv add requests
uv pip freeze > requirements.txt

# Create virtual environment
uv venv
source .venv/bin/activate
```

## 🐳 Docker Integration

The Docker build now uses uv for package installation:

```dockerfile
# Install uv in Docker
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Install packages (much faster than pip)
RUN uv pip install --system --no-cache -r requirements.txt
```

**Performance improvement**: 57 packages installed in 90ms vs several minutes with pip!

## 🔄 Migration from pip

No changes needed! All existing workflows continue to work:

- `requirements.txt` files work unchanged
- Virtual environments work the same way
- `make install` automatically uses uv
- Docker builds are faster and more reliable

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `make install` | Install all dependencies |
| `make add-package pkg=name` | Add new package |
| `make remove-package pkg=name` | Remove package |
| `make update-deps` | Update all dependencies |
| `make sync-deps` | Sync exact versions |
| `make create-venv` | Create virtual environment |

## 🎯 Benefits for Development

1. **Faster setup**: New developers can get started in seconds
2. **Reliable builds**: Better dependency resolution prevents conflicts
3. **Better caching**: Repeated installs are nearly instant
4. **Modern tooling**: Better error messages and progress indicators

## 🔧 Configuration

The Makefile automatically detects your environment:
- Uses `--system` flag when not in virtual environment
- Uses uv directly when in virtual environment
- Fallback to pip if uv is not available

No configuration needed - it just works!

## 📚 Learn More

- [uv Documentation](https://docs.astral.sh/uv/)
- [uv GitHub Repository](https://github.com/astral-sh/uv)
- [Migration Guide](https://docs.astral.sh/uv/guides/migration/)
