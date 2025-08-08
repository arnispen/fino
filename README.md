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
- Pinata API key (for IPFS storage - **only needed for sending**)

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

### 2. Configure Pinata (IPFS Storage) - **Only for Sending**

Create a `.env` file in the project root:

```env
PINATA_JWT=your_pinata_jwt_token_here
```

Or use the `--pinata-jwt` flag with the send command.

> **Note**: Pinata JWT is only required for sending files (uploading to IPFS). Receiving files doesn't require any API keys.

## 📖 **Usage**

### Sending Files

```bash
# Send a file to a recipient
fino send \
  --file ./secret_document.pdf \
  --to npub1recipient_public_key_here \
  --from nsec1your_private_key_here

# With custom Pinata JWT
fino send \
  --file ./secret_document.pdf \
  --to npub1recipient_public_key_here \
  --from nsec1your_private_key_here \
  --pinata-jwt your_jwt_token_here
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

## 📦 **Installation from PyPI**

```bash
# Install the package
pip install fino-file-sharing

# Generate keys
fino gen-key

# Send a file
fino send --file document.pdf --to npub1... --from nsec1...

# Receive files
fino receive --from nsec1...
```

## 🤝 **Contributing**

This is a proof-of-concept project. Contributions are welcome for:

- Bug fixes and improvements
- Documentation enhancements
- Security audits and recommendations
- Feature suggestions

Please read [DEVELOPMENT.md](DEVELOPMENT.md) for development setup and guidelines.

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ **Disclaimer**

This software is provided as-is for educational and research purposes. The authors make no guarantees about security, reliability, or suitability for any purpose. Use at your own risk.

---

**FiNo** - Exploring the future of decentralized file sharing, one proof-of-concept at a time. 🔐📁
