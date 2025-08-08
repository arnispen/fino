# FiNo 🔐📁

> **Proof-of-Concept: Secure File Sharing via IPFS + Nostr DMs**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Status: Proof of Concept](https://img.shields.io/badge/Status-Proof%20of%20Concept-orange.svg)](https://github.com/arnispen/fino)

**FiNo** (File + Nostr) is an innovative proof-of-concept CLI tool that demonstrates secure, decentralized file sharing using the Nostr protocol and IPFS. This project explores the intersection of decentralized messaging and distributed file storage for private, censorship-resistant file transfers.

## 🚀 **Innovation Highlights**

- **🔐 End-to-End Encryption**: Custom ECDH-based encryption for cross-key communication
- **🌐 Decentralized Infrastructure**: Leverages Nostr relays and IPFS for distributed operation
- **📱 CLI-First Design**: Simple, powerful command-line interface
- **🔒 Privacy-Focused**: No central servers, no tracking, no metadata retention
- **⚡ Real-Time**: Instant file sharing via Nostr DMs with IPFS storage

## 🏗️ **Architecture Overview**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Sender    │    │   Nostr     │    │   Receiver  │
│             │    │   Relay     │    │             │
│ 1. Encrypt  │───▶│ 2. DM with  │───▶│ 3. Decrypt  │
│    File     │    │   Metadata  │    │   & Save    │
│ 2. Upload   │    │             │    │             │
│    to IPFS  │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌─────────────┐
                    │    IPFS     │
                    │   Storage   │
                    │             │
                    │ Encrypted   │
                    │   Files     │
                    └─────────────┘
```

## 🛠️ **Installation**

### Prerequisites

- Python 3.8 or higher
- Nostr key pair (nsec/npub)
- Pinata API key (for IPFS storage)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/arnispen/fino.git
cd fino

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies and CLI tool
pip install -r requirements.txt
pip install -e .
```

## 🔑 **Setup**

### 1. Generate Nostr Keys

```bash
# Generate a new key pair
fino gen-key

# This will output:
# nsec: nsec1...
# npub: npub1...
```

### 2. Configure Pinata (IPFS Storage)

Create a `.env` file in the project root:

```env
PINATA_JWT=your_pinata_jwt_token_here
```

Or use the `--pinata-jwt` flag with commands.

## 📖 **Usage**

### Sending Files

```bash
# Send a file to a recipient
fino send \
  --file ./secret_document.pdf \
  --to npub1recipient_public_key_here \
  --from nsec1your_private_key_here
```

### Receiving Files

```bash
# Listen for incoming files (saves to current directory by default)
# Only shows NEW files sent to you after starting the command
fino receive \
  --from nsec1your_private_key_here

# Save to specific directory
fino receive \
  --from nsec1your_private_key_here \
  --output-dir ./downloads
```

> Note: FiNo uses a built-in default relay configuration for simplicity and reliability.

### Key Management

```bash
# Generate new key pair
fino gen-key
```

## 🔐 **Security Features**

### Encryption Layers

1. **File Encryption**: AES-256-CBC with random key and nonce
2. **Metadata Encryption**: Custom ECDH-based encryption for cross-key communication
3. **Nostr DMs**: Standard Nostr kind 4 encrypted direct messages

### Privacy Guarantees

- ✅ **No Central Servers**: Fully decentralized via Nostr relays
- ✅ **No Metadata Tracking**: IPFS CIDs are encrypted in DMs
- ✅ **End-to-End Encryption**: Only sender and recipient can decrypt
- ✅ **Censorship Resistant**: Distributed across multiple relays and IPFS nodes
- ✅ **Filename Preservation**: Original filenames are preserved when files are received

## 🧪 **Proof-of-Concept Status**

⚠️ **Important**: This is a **proof-of-concept** project designed for:

- **Innovation Research**: Exploring decentralized file sharing concepts
- **Educational Purposes**: Understanding Nostr + IPFS integration
- **Developer Experimentation**: Testing new cryptographic approaches

**Not intended for production use** without significant security audits and hardening.

## 🏗️ **Technical Implementation**

### Core Components

- **`src/fino/encryption.py`**: AES file encryption/decryption
- **`src/fino/ipfs.py`**: IPFS upload/download via Pinata
- **`src/fino/nostr.py`**: Nostr DM handling with custom ECDH encryption
- **`src/fino/commands/`**: CLI command implementations

### Key Innovations

1. **Custom ECDH Encryption**: Bypasses pynostr's broken cross-key encryption
2. **Hybrid Architecture**: Combines Nostr's real-time messaging with IPFS's persistent storage
3. **CLI-First Design**: Developer-friendly interface for rapid prototyping

## 🧪 **Manual Testing**

```bash
# Test file sharing between two users
# Terminal 1: Start receiver
fino receive --from nsec1receiver_key

# Terminal 2: Send file
fino send --file test.txt --to npub1receiver_key --from nsec1sender_key
```

## 🤝 **Contributing**

This is an experimental project. Contributions are welcome for:

- **Security Improvements**: Cryptographic enhancements and audits
- **Feature Extensions**: Additional Nostr relay support, alternative IPFS providers
- **Documentation**: Better examples and use cases
- **Testing**: More comprehensive test coverage

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Code formatting
black src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/
```

## 📄 **License**

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 **Acknowledgments**

- **Nostr Protocol**: For decentralized messaging infrastructure
- **IPFS**: For distributed file storage
- **Pinata**: For IPFS pinning services
- **Cryptography Community**: For encryption standards and best practices

## 🔮 **Future Directions**

- **Multi-relay Support**: Automatic failover across multiple Nostr relays
- **Alternative IPFS Providers**: Support for other IPFS pinning services
- **Mobile Integration**: Native mobile apps for iOS/Android
- **Web Interface**: Browser-based file sharing interface
- **Group Sharing**: Multi-recipient file distribution
- **Streaming Support**: Large file streaming and resumable transfers

---

**Built with ❤️ for the decentralized future**

*This project demonstrates the potential of combining Nostr's real-time messaging with IPFS's distributed storage for secure, private file sharing without centralized infrastructure.*
