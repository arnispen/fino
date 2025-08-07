# Development Guide

This document provides information for developers who want to contribute to or extend the FiNo proof-of-concept project.

## 🏗️ **Project Structure**

```
fino/
├── src/fino/                 # Main source code
│   ├── __init__.py
│   ├── main.py              # CLI entry point
│   ├── encryption.py        # AES file encryption/decryption
│   ├── ipfs.py              # IPFS upload/download via Pinata
│   ├── nostr.py             # Nostr DM handling with custom ECDH
│   ├── utils.py             # Utility functions
│   └── commands/            # CLI command implementations
│       ├── __init__.py
│       ├── gen_key.py       # Key generation
│       ├── send.py          # File sending
│       └── receive.py       # File receiving
├── tests/                   # Test suite
├── pyproject.toml          # Project configuration
├── requirements.txt        # Runtime dependencies
└── README.md              # Project documentation
```

## 🛠️ **Development Setup**

### Prerequisites

- Python 3.8+
- Git
- Pinata API key (for IPFS testing)

### Installation

```bash
# Clone the repository
git clone https://github.com/arnispen/fino.git
cd fino

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Environment Configuration

Create a `.env` file in the project root:

```env
PINATA_JWT=your_pinata_jwt_token_here
```

## 🧪 **Manual Testing**

```bash
# Generate test keys
fino gen-key

# Test file sending (requires two terminals)
# Terminal 1: Start receiver
fino receive --from nsec1receiver_key

# Terminal 2: Send file
fino send --file test.txt --to npub1receiver_key --from nsec1sender_key
```

## 🔧 **Code Quality**

### Formatting

```bash
# Format code with Black
black src/

# Check formatting
black --check src/
```

### Linting

```bash
# Run flake8
flake8 src/

# Run mypy for type checking
mypy src/
```

### Pre-commit Hooks

Consider setting up pre-commit hooks for automatic code quality checks:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install
```

## 🏗️ **Architecture Overview**

### Core Components

1. **Encryption Module** (`encryption.py`)
   - AES-256-CBC file encryption/decryption
   - Random key and nonce generation
   - PKCS7 padding

2. **IPFS Module** (`ipfs.py`)
   - Pinata API integration
   - File upload/download
   - CID handling

3. **Nostr Module** (`nostr.py`)
   - Custom ECDH encryption for cross-key communication
   - Nostr DM event creation and handling
   - WebSocket relay communication

4. **CLI Commands** (`commands/`)
   - Typer-based command-line interface
   - User-friendly output and error handling

### Key Design Decisions

1. **Custom ECDH Encryption**: Bypasses pynostr's broken cross-key encryption
2. **Hybrid Architecture**: Combines Nostr's real-time messaging with IPFS's persistent storage
3. **CLI-First Design**: Developer-friendly interface for rapid prototyping
4. **Modular Structure**: Clear separation of concerns for easy extension

## 🔐 **Security Considerations**

### Current Implementation

- **File Encryption**: AES-256-CBC with random key/nonce
- **Metadata Encryption**: Custom ECDH with HKDF key derivation
- **Key Management**: Nostr nsec/npub format
- **No Central Servers**: Fully decentralized via relays and IPFS

### Security Limitations

⚠️ **This is a proof-of-concept with known limitations:**

- No forward secrecy
- No perfect forward secrecy
- No replay protection
- No metadata privacy (relay operators can see DM events)
- No file integrity verification beyond IPFS hashing

### Recommended Improvements

1. **Add HMAC for integrity verification**
2. **Implement perfect forward secrecy**
3. **Add replay protection**
4. **Implement metadata privacy techniques**
5. **Add file streaming for large files**
6. **Implement multi-relay support**

## 🚀 **Extending the Project**

### Adding New Commands

1. Create a new file in `src/fino/commands/`
2. Implement the command using Typer
3. Register the command in `src/fino/main.py`

Example:

```python
# src/fino/commands/new_feature.py
import typer

app = typer.Typer(help="Description of new feature")

@app.command()
def new_feature():
    """Implementation of new feature."""
    pass
```

### Adding New IPFS Providers

1. Extend the `ipfs.py` module
2. Add provider-specific upload/download functions
3. Update the CLI to support provider selection

### Adding New Encryption Methods

1. Extend the `encryption.py` module
2. Implement new encryption/decryption functions
3. Add CLI options for encryption method selection

## 📝 **Contributing Guidelines**

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all functions
- Keep functions focused and small

### Testing

- Write tests for new features
- Ensure existing tests pass
- Add integration tests for end-to-end functionality

### Documentation

- Update README.md for user-facing changes
- Update this DEVELOPMENT.md for developer-facing changes
- Add inline comments for complex logic

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

## 🔮 **Future Development Ideas**

### Features

- **Multi-relay Support**: Automatic failover across multiple Nostr relays
- **Alternative IPFS Providers**: Support for other IPFS pinning services
- **Mobile Integration**: Native mobile apps for iOS/Android
- **Web Interface**: Browser-based file sharing interface
- **Group Sharing**: Multi-recipient file distribution
- **Streaming Support**: Large file streaming and resumable transfers

### Technical Improvements

- **Perfect Forward Secrecy**: Implement PFS for enhanced security
- **Metadata Privacy**: Techniques to hide DM metadata from relays
- **File Integrity**: HMAC verification for downloaded files
- **Resumable Transfers**: Support for large file transfers with resume capability
- **Compression**: Optional file compression before encryption

### Integration Ideas

- **Nostr Clients**: Integration with existing Nostr clients
- **IPFS Gateways**: Support for multiple IPFS gateways
- **Blockchain Integration**: Optional blockchain-based file verification
- **Decentralized Identity**: Integration with DID systems

## 📞 **Getting Help**

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub discussions for questions and ideas
- **Security**: Report security issues privately to the maintainers

---

**Remember**: This is a proof-of-concept project designed for innovation research and educational purposes. Always prioritize security and privacy in any production use cases. 