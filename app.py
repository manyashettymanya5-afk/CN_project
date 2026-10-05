from flask import Flask, render_template, request, jsonify
import os
import socket
import struct
import threading

from config import TCP_PORT, WEB_PORT
from tcp_receiver import start_tcp_server
from lan_discovery import start_discovery_service, discover_devices, get_local_ip


# ============================================================
# FILEPULSE APPLICATION
# ============================================================

app = Flask(__name__)

# Folder for temporary uploaded files
TEMP_FOLDER = "temporary_uploads"

os.makedirs(TEMP_FOLDER, exist_ok=True)


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():
    try:
        local_ip = get_local_ip()
    except Exception:
        local_ip = "Unknown"

    return render_template(
        "index.html",
        local_ip=local_ip,
        tcp_port=TCP_PORT
    )


# ============================================================
# DISCOVER FILEPULSE DEVICES
# ============================================================

@app.route("/discover", methods=["GET"])
def discover():
    try:
        devices = discover_devices()

        return jsonify({
            "success": True,
            "devices": devices
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e),
            "devices": []
        }), 500


# ============================================================
# SEND FILE
# ============================================================

@app.route("/send", methods=["POST"])
def send_file():

    # Check receiver IP
    receiver_ip = request.form.get("receiver_ip")

    if not receiver_ip:
        return jsonify({
            "success": False,
            "message": "Receiver IP is missing."
        }), 400

    # Receiver TCP port
    receiver_port = request.form.get(
        "receiver_port",
        str(TCP_PORT)
    )

    try:
        receiver_port = int(receiver_port)
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid receiver port."
        }), 400

    # Check file
    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "No file selected."
        }), 400

    uploaded_file = request.files["file"]

    if uploaded_file.filename == "":
        return jsonify({
            "success": False,
            "message": "No file selected."
        }), 400

    # --------------------------------------------------------
    # Save uploaded file temporarily
    # --------------------------------------------------------

    filename = os.path.basename(uploaded_file.filename)

    temp_path = os.path.join(
        TEMP_FOLDER,
        filename
    )

    # Prevent accidental overwrite
    base, extension = os.path.splitext(filename)
    counter = 1

    while os.path.exists(temp_path):
        filename = f"{base}_{counter}{extension}"
        temp_path = os.path.join(
            TEMP_FOLDER,
            filename
        )
        counter += 1

    try:
        uploaded_file.save(temp_path)

        # ----------------------------------------------------
        # Send file using TCP
        # ----------------------------------------------------

        success, message = send_file_to_receiver(
            receiver_ip,
            receiver_port,
            temp_path,
            filename
        )

        return jsonify({
            "success": success,
            "message": message
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": f"Transfer failed: {str(e)}"
        }), 500

    finally:

        # Delete temporary file
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass


# ============================================================
# TCP FILE TRANSFER
# ============================================================

def send_file_to_receiver(
    receiver_ip,
    receiver_port,
    file_path,
    filename
):
    """
    Sends a file to another FilePulse computer using TCP.

    Protocol:

    4 bytes  -> filename length
    N bytes  -> filename
    8 bytes  -> file size
    N bytes  -> file data
    """

    try:

        # ----------------------------------------------------
        # Get file size
        # ----------------------------------------------------

        file_size = os.path.getsize(file_path)

        # ----------------------------------------------------
        # Create TCP socket
        # ----------------------------------------------------

        client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        client_socket.settimeout(30)

        print(
            f"Connecting to {receiver_ip}:{receiver_port}..."
        )

        client_socket.connect(
            (receiver_ip, receiver_port)
        )

        print("Connected to receiver.")

        # ----------------------------------------------------
        # Prepare filename
        # ----------------------------------------------------

        filename_bytes = filename.encode("utf-8")

        filename_length = len(filename_bytes)

        # ----------------------------------------------------
        # Send filename length
        # ----------------------------------------------------

        client_socket.sendall(
            struct.pack(
                "!I",
                filename_length
            )
        )

        # ----------------------------------------------------
        # Send filename
        # ----------------------------------------------------

        client_socket.sendall(
            filename_bytes
        )

        # ----------------------------------------------------
        # Send file size
        # ----------------------------------------------------

        client_socket.sendall(
            struct.pack(
                "!Q",
                file_size
            )
        )

        # ----------------------------------------------------
        # Send file data
        # ----------------------------------------------------

        bytes_sent = 0

        with open(file_path, "rb") as file:

            while True:

                data = file.read(4096)

                if not data:
                    break

                client_socket.sendall(data)

                bytes_sent += len(data)

        print(
            f"File sent: {bytes_sent} bytes"
        )

        # ----------------------------------------------------
        # Wait for receiver confirmation
        # ----------------------------------------------------

        try:

            response = client_socket.recv(1024)

            response = response.decode(
                "utf-8",
                errors="ignore"
            )

        except socket.timeout:

            client_socket.close()

            return (
                False,
                "File was sent, but receiver confirmation was not received."
            )

        client_socket.close()

        # ----------------------------------------------------
        # Check receiver response
        # ----------------------------------------------------

        if response == "FILE_RECEIVED":

            print("Receiver confirmed file.")

            return (
                True,
                "File transferred successfully."
            )

        else:

            return (
                False,
                f"Receiver returned: {response}"
            )

    except ConnectionRefusedError:

        return (
            False,
            "Connection refused. Make sure FilePulse is running on the receiver computer."
        )

    except socket.timeout:

        return (
            False,
            "Connection timed out. Check the network and firewall."
        )

    except OSError as e:

        return (
            False,
            f"Network error: {str(e)}"
        )

    except Exception as e:

        return (
            False,
            f"Transfer error: {str(e)}"
        )


# ============================================================
# START FILEPULSE SERVICES
# ============================================================

def start_filepulse():

    print()
    print("=" * 55)
    print("              FILEPULSE")
    print("      Local Network Data Transfer System")
    print("=" * 55)

    # --------------------------------------------------------
    # Get local IP
    # --------------------------------------------------------

    try:
        local_ip = get_local_ip()
    except Exception:
        local_ip = "Unknown"

    print()
    print(f"Local IP: {local_ip}")
    print(f"Web server port: {WEB_PORT}")
    print(f"TCP transfer port: {TCP_PORT}")

    # --------------------------------------------------------
    # Start TCP receiver
    # --------------------------------------------------------

    tcp_thread = threading.Thread(
        target=start_tcp_server,
        daemon=True
    )

    tcp_thread.start()

    print(
        f"TCP receiver running on port {TCP_PORT}"
    )

    # --------------------------------------------------------
    # Start LAN discovery
    # --------------------------------------------------------

    start_discovery_service()

    print(
        "LAN discovery service started."
    )

    print()
    print(
        f"Open FilePulse at:"
    )

    print(
        f"http://localhost:{WEB_PORT}"
    )

    print()
    print(
        "For another computer on the same LAN:"
    )

    if local_ip != "Unknown":
        print(
            f"http://{local_ip}:{WEB_PORT}"
        )

    print()
    print("=" * 55)
    print("FilePulse is running...")
    print("Press CTRL + C to stop.")
    print("=" * 55)
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    start_filepulse()

    app.run(
        host="0.0.0.0",
        port=WEB_PORT,
        debug=False,
        threaded=True
    )