# 🔐📁 FiNo - Secure File Sharing via IPFS + Nostr

**FiNo** (File + Nostr) is a decentralized, secure file sharing tool that combines IPFS storage with Nostr messaging for truly anonymous and censorship-resistant file transfers.

## 🌟 Features

- **🔐 End-to-End Encryption**: AES-256-CBC + ECDH key exchange
- **🌐 Decentralized**: No central servers, works globally
- **🆓 Completely Free**: No API keys, no registration required
- **⚡ Real-Time**: Instant file sharing via Nostr DMs
- **🔒 Privacy-Focused**: No central servers, no tracking

## 🚀 Quick Start

### 1. Install FiNo
```bash
pip install pyfino
```

### 2. Install IPFS (one-time setup)
```bash
# macOS
brew install ipfs

# Linux
curl -O https://dist.ipfs.io/go-ipfs/v0.36.0/go-ipfs_v0.36.0_linux-amd64.tar.gz
tar -xvzf go-ipfs_v0.36.0_linux-amd64.tar.gz
sudo mv go-ipfs/ipfs /usr/local/bin/

# Windows
# Download from https://ipfs.io/docs/install/
```

### 3. Initialize IPFS (one-time setup)
```bash
ipfs init
brew services start ipfs  # macOS
# or: ipfs daemon &  # Linux/Windows
```

### 4. Generate your keys
```bash
fino gen-key
```

### 5. Send a file
```bash
fino send document.pdf --to npub1abc... --from nsec1xyz...
```

### 6. Receive files
```bash
fino receive --from nsec1xyz...
```

## 🤔 How It Works (ELI5)

### **The Problem**
- Traditional file sharing needs central servers (Google Drive, Dropbox)
- These can be shut down, censored, or hacked
- They know who you are and what you're sharing

### **The Solution**
FiNo splits file sharing into two parts:

1. **📁 File Storage (IPFS)**
   - Files are stored on a global network (like a giant, distributed hard drive)
   - No single point of failure
   - Files are accessible from anywhere in the world
   - **Free forever** - no company owns it

2. **📨 File Location (Nostr)**
   - The "address" of your file is sent via Nostr (like a decentralized email)
   - Only the person you send it to can find the file
   - No central server controls the messages

### **How It's Free**
- **IPFS**: Community-run network, no company owns it
- **Nostr**: Decentralized messaging protocol, no company owns it
- **No API keys**: You're not using anyone's service
- **No registration**: You're just using open protocols



## 🌍 Global File Sharing

### How It Works Across Countries
1. **Sender** encrypts file → uploads to IPFS → sends metadata via Nostr
2. **IPFS Network** stores file globally accessible
3. **Receiver** gets metadata via Nostr → downloads from IPFS → decrypts

### Why It Works Everywhere
- **IPFS**: Files are replicated across the global network
- **Nostr**: Messages are relayed through multiple servers worldwide
- **No borders**: Decentralized protocols don't respect national boundaries

## 🔐 Security Features

- **AES-256-CBC**: Military-grade file encryption
- **ECDH**: Perfect forward secrecy for metadata
- **Zero-knowledge**: No one can see your files except the intended recipient
- **End-to-end encryption**: Files encrypted before transmission
- **Decentralized**: No central point of failure

## 📦 Installation Details

### Requirements
- Python 3.8+
- IPFS daemon
- Internet connection

### Dependencies
- `cryptography`: Encryption
- `pynostr`: Nostr protocol
- `requests`: HTTP requests
- `rich`: Beautiful CLI
- `typer`: Command-line interface

## 🚨 Important Notes

- **Experimental software** - Use at your own risk
- **Keep your nsec private** - Never share your private key
- **Backup your keys** - If you lose them, you can't access your files
- **IPFS persistence** - Files may be removed if not pinned by someone

## 🔗 Useful Links

- [IPFS Documentation](https://docs.ipfs.io/)
- [Nostr Protocol](https://github.com/nostr-protocol/nostr)
- [FiNo GitHub](https://github.com/yourusername/fino)

## 📄 License

MIT License - see LICENSE file for details.

---

**⚠️ Disclaimer**: This is experimental software for innovation research only. Use responsibly and in accordance with local laws.
