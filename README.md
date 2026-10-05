# FilePulse – Local Network Data Transfer System

## 1. Project Overview

FilePulse is a LAN-based file transfer system that allows users to transfer files between computers connected to the same local network without using the internet.

The system automatically discovers other computers running FilePulse on the same network and displays them as available receivers. The user can select a receiver, choose a file, and transfer it securely using TCP socket communication.

---

## 2. Problem Statement

Transferring files between computers usually depends on internet-based services, USB drives, or cloud storage.

FilePulse provides a simple local solution where users can transfer files directly between computers connected to the same LAN without requiring internet access or external storage devices.

---

## 3. Objectives

- Transfer files between computers on the same LAN.
- Discover available FilePulse systems automatically.
- Avoid manually entering the receiver IP address.
- Support files such as PDFs, images, documents, videos, and other file types.
- Use TCP/IP socket programming for reliable file transfer.
- Provide a simple web-based user interface.
- Store received files automatically on the receiver computer.

---

## 4. Main Features

### Automatic LAN Discovery

FilePulse searches for other FilePulse systems running on the same local network.

### Receiver Selection

Available computers are displayed in a dropdown list using their device name and IP address.

### File Selection

The user can select any required file from the computer.

### TCP File Transfer

The selected file is transferred between computers using TCP socket communication.

### Automatic File Storage

Received files are automatically stored in the `received_files` folder.

### Web Interface

The system provides a simple browser-based interface for discovering devices and sending files.

---

## 5. Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- TCP/IP
- UDP
- Socket Programming

---

## 6. System Architecture

FilePulse uses a client-server architecture.

```text
              Local Area Network
                     │
        ┌────────────┴────────────┐
        │                         │
   Computer A                 Computer B
    Sender                    Receiver
        │                         │
        │── UDP Discovery ───────>│
        │<── Device Information ──│
        │                         │
        │──── TCP File Transfer ─>│
        │                         │
        │                    received_files/
