# 🔐📁 FiNo - Secure File Sharing via IPFS + Nostr

**FiNo** (File + Nostr) is a decentralized, secure file sharing tool that combines IPFS storage with Nostr messaging for truly anonymous and censorship-resistant file transfers.

## 🌟 Features

- **🔐 End-to-End Encryption**: AES-256-GCM + ECDH key exchange
- **🌐 Decentralized**: No central servers, works globally
- **🆓 Completely Free**: No API keys, no registration required
- **⚡ Real-Time**: Instant file sharing via Nostr DMs
- **🔒 Privacy-Focused**: No central servers, no tracking
- **🗜️ Smarter Transfers**: Files are compressed (gzip) before encryption by default
- **🎨 Beautiful CLI**: Rich-powered output with panels, colors and emojis

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
sudo brew services start ipfs  # macOS
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

### 7. Show version
```bash
fino --version
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

### **Behavior & Defaults**
- Files are automatically compressed with gzip before encryption to reduce transfer size (media like .mp4/.jpg may not shrink).
- IPFS announce (provider routing) is performed in the background to minimize blocking; global discoverability may take a few seconds after send.

### **How It's Free**
- **IPFS**: Community-run network, no company owns it
- **Nostr**: Decentralized messaging protocol, no company owns it
- **No API keys**: You're not using anyone's service
- **No registration**: You're just using open protocols

## 🔐 Security Features

- **AES-256-GCM**: Military-grade file encryption
- **ECDH**: Perfect forward secrecy for metadata
- **Zero-knowledge**: No one can see your files except the intended recipient
- **End-to-end encryption**: Files encrypted before transmission
- **Compress-before-encrypt**: Reduces plaintext patterns and metadata hints before encryption, and shrinks size for faster, cheaper transfers
- **Decentralized**: No central point of failure

## 📦 Installation Details

### Requirements
- Python 3.8+
- IPFS daemon
- Internet connection

## 🚨 Important Notes

- **Experimental software** - Use at your own risk
- **Keep your nsec private** - Never share your private key
- **Backup your keys** - If you lose them, you can't access your files
- **IPFS persistence** - Files may be removed if not pinned by someone

## ⚡ Performance Tips

- Start the IPFS daemon before sending to keep it "warm": `ipfs daemon`
- Your sender upload speed is the main bottleneck for total time; compression helps most for text/JSON/CSV, not for videos/images/ZIPs.
- Receivers may need a few seconds after you send for background DHT announce to propagate; if a fetch fails immediately, retry once.

## 🔗 Useful Links

- [IPFS Documentation](https://docs.ipfs.io/)
- [Nostr Protocol](https://github.com/nostr-protocol/nostr)
- [FiNo GitHub](https://github.com/arnispen/pyfino)

## 📄 License

MIT License - see LICENSE file for details.

---

**⚠️ Disclaimer**: This is experimental software for innovation research only. Use responsibly and in accordance with local laws.
