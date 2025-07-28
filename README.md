# 🗂️ FiNo

> **FiNo** — Secure, decentralized file sharing via the command line using **IPFS** and **Nostr**.

FiNo (short for **File Nostr**) is a privacy-focused CLI tool that allows you to share encrypted files over decentralized infrastructure — no blockchain, no wallets, no nonsense.

It uses:
- 🔐 **AES-256-GCM** for local file encryption
- 🌐 **IPFS (via Pinata)** for decentralized file hosting
- 📡 **Nostr DMs (kind: 4)** for key exchange and file delivery

---

## 🚀 Quickstart

### 1. Clone & install

```bash
git clone https://github.com/yourname/fino.git
cd fino
pip install .
```

> ✅ Requires Python 3.8+

---

### 2. Set up your `.env`

```bash
cp .env.example .env
```

Add your Pinata JWT to `.env`:

```
PINATA_JWT=eyJhbGciOiJIUz...
```

---

### 3. Create profiles

```bash
fino --profile alice init
fino --profile bob init
```

Each profile has its own private/public keypair stored in `~/.fino/profiles`.

---

### 4. Share a file

```bash
fino --profile alice send --file ./secret.txt
```

You'll be prompted for the recipient (can be a contact name or raw `npub1...`).

---

### 5. Receive files

```bash
fino --profile bob receive
```

Files will be decrypted, saved locally, and added to your received file history.

---

## 💡 How It Works

```
Sender (Alice)
    |
    |-- Encrypts file with AES-256-GCM
    |-- Uploads to IPFS (Pinata)
    |-- Encrypts CID + key + nonce using recipient's Nostr pubkey
    |-- Sends as Nostr kind:4 DM
    |
Receiver (Bob)
    |
    |-- Listens for kind:4 messages
    |-- Decrypts payload using Nostr privkey
    |-- Downloads file from IPFS
    |-- Decrypts with AES key and nonce
```

---

## 🔐 Security Principles

- All files are encrypted client-side before upload
- No plaintext keys or data are shared via IPFS or Nostr
- Only the intended recipient (holding the private key) can decrypt the payload
- No blockchain, wallets, tokens, or accounts required

---

## 📦 Features

- [x] CLI-first, zero UI
- [x] Per-user profiles (`~/.fino/profiles`)
- [x] AES-GCM file encryption
- [x] IPFS uploads via Pinata JWT
- [x] Nostr direct message key exchange
- [x] Contact/address book per profile
- [x] File receipt logging and history view
- [x] Works locally or over Nostr relays
- [x] Fully extensible, clean Python modules

---

## 📁 Project Structure

```
fino/
├── fino.py              # CLI entry point
├── encryption.py        # AES-GCM logic
├── ipfs.py              # Pinata upload/download
├── nostr.py             # Nostr message logic
├── profiles.py          # Profile & key handling
├── contacts.py          # Contact management
├── receive.py           # Receive flow
├── send.py              # Send flow
├── history.py           # Received file log
├── utils.py             # Shared utils
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 🤝 Contributing

Pull requests are welcome!

If you spot a bug, UX issue, or want to suggest a feature:

- Open an [issue](https://github.com/yourname/fino/issues)
- Or fork and submit a PR

Please follow the style and modular layout already used in the repo.

---

## 📄 License

MIT — free for personal and commercial use.

---

## ❤️ Values

FiNo is built with the following principles:

- **Privacy-first**: You control your data, keys, and files
- **Zero-trust**: No reliance on centralized storage or identity
- **Simple UX**: Clarity and modularity over complexity
- **Hackable**: Easily test, fork, and extend

---

Made with 🐍 Python and ❤️ for decentralization.