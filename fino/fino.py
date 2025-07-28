import argparse
import sys
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file if present

from fino.profiles import init_profile, profile_exists
from fino.contacts import (
    add_contact,
    remove_contact,
    get_contact,
    list_contacts,
)
from fino.send import send_file
from fino.receive import receive_file
from fino.history import list_received_files


def main():
    parser = argparse.ArgumentParser(
        prog="fino",
        description="FiNo — Secure File Sharing with IPFS + Nostr",
    )
    parser.add_argument(
        "--profile",
        required=True,
        help="Active profile name (e.g., alice, bob)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # -----------------------------
    # init
    subparsers.add_parser("init", help="Create a new user profile")

    # -----------------------------
    # contact commands
    contact_parser = subparsers.add_parser("contact", help="Manage your contacts")
    contact_subparsers = contact_parser.add_subparsers(dest="subcommand")

    contact_add = contact_subparsers.add_parser("add", help="Add a contact")
    contact_add.add_argument("name", help="Contact name")
    contact_add.add_argument("--npub", required=True, help="Nostr public key")

    contact_show = contact_subparsers.add_parser("show", help="Show contact info")
    contact_show.add_argument("name", help="Contact name")

    contact_list = contact_subparsers.add_parser("list", help="List all contacts")

    contact_remove = contact_subparsers.add_parser("remove", help="Remove a contact")
    contact_remove.add_argument("name", help="Contact name")

    # -----------------------------
    # send
    send_parser = subparsers.add_parser("send", help="Encrypt and send a file")
    send_parser.add_argument("--file", required=True, help="Path to file to send")
    send_parser.add_argument("--to", help="Recipient name or npub (optional if interactive)")
    send_parser.add_argument("--pinata-jwt", required=False, help="Pinata JWT (from .env or env var)")

    # -----------------------------
    # receive
    receive_parser = subparsers.add_parser("receive", help="Receive encrypted files")
    receive_parser.add_argument("--relay", help="Optional relay URL override")
    receive_parser.add_argument(
        "--auto-save",
        action="store_true",
        help="Auto-save received file without prompting",
    )

    # -----------------------------
    # files list
    files_parser = subparsers.add_parser("files", help="View received file history")
    files_sub = files_parser.add_subparsers(dest="subcommand")

    files_list = files_sub.add_parser("list", help="List received files")
    files_list.add_argument("--limit", type=int, help="Show only latest N files")

    # -----------------------------
    # Parse args
    args = parser.parse_args()

    # Validate profile (except for init)
    if args.command != "init" and not profile_exists(args.profile):
        print(f"❌ Profile '{args.profile}' does not exist.")
        print(f"👉 Run: fino --profile {args.profile} init")
        sys.exit(1)

    # -----------------------------
    # Dispatch
    if args.command == "init":
        try:
            init_profile(args.profile)
        except Exception as e:
            print(f"❌ Failed to initialize profile: {e}")
            sys.exit(1)

    elif args.command == "contact":
        if args.subcommand == "add":
            try:
                add_contact(args.name, args.npub, profile=args.profile)
            except Exception as e:
                print(f"❌ Could not add contact: {e}")
                sys.exit(1)

        elif args.subcommand == "show":
            try:
                npub = get_contact(args.name, profile=args.profile)
                print(f"👤 {args.name}: {npub}")
            except Exception as e:
                print(f"❌ {e}")
                sys.exit(1)

        elif args.subcommand == "list":
            try:
                contacts = list_contacts(profile=args.profile)
                if not contacts:
                    print("📭 No contacts found.")
                else:
                    for name, npub in contacts.items():
                        print(f"👤 {name}: {npub}")
            except Exception as e:
                print(f"❌ {e}")
                sys.exit(1)

        elif args.subcommand == "remove":
            try:
                remove_contact(args.name, profile=args.profile)
            except Exception as e:
                print(f"❌ {e}")
                sys.exit(1)

        else:
            contact_parser.print_help()

    elif args.command == "send":
        try:
            send_file(
                file_path=args.file,
                from_profile=args.profile,
                recipient=args.to,
                pinata_jwt=args.pinata_jwt,
            )
        except Exception as e:
            print(f"❌ Send failed: {e}")
            sys.exit(1)

    elif args.command == "receive":
        try:
            receive_file(
                profile=args.profile,
                relay_url=args.relay,
                auto_save=args.auto_save,
            )
        except Exception as e:
            print(f"❌ Receive failed: {e}")
            sys.exit(1)

    elif args.command == "files":
        if args.subcommand == "list":
            history = list_received_files(profile=args.profile, limit=args.limit)
            if not history:
                print("📭 No received files.")
            else:
                print(f"\n📁 Received files for profile '{args.profile}':\n")
                for h in history:
                    print(f"📦 {h['filename']} | CID: {h['cid']}")
                    print(f"    🔗 {h['ipfs_url']}")
                    print(f"    🧑 From: {h['sender']}")
                    print(f"    🕒 {h['timestamp']}\n")
        else:
            files_parser.print_help()

    else:
        parser.print_help()
