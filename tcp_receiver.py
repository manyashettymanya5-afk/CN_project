import socket
import os
import struct
import threading
from datetime import datetime

from config import TCP_PORT, BUFFER_SIZE


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

RECEIVED_FOLDER = os.path.join(
    BASE_DIR,
    "received_files"
)

os.makedirs(
    RECEIVED_FOLDER,
    exist_ok=True
)


def receive_exact(sock, size):

    data = b""

    while len(data) < size:

        chunk = sock.recv(
            size - len(data)
        )

        if not chunk:

            raise ConnectionError(
                "Connection closed unexpectedly."
            )

        data += chunk

    return data


def receive_file(
    client_socket,
    client_address
):

    try:

      

        filename_length_data = receive_exact(
            client_socket,
            4
        )

        filename_length = struct.unpack(
            "!I",
            filename_length_data
        )[0]


      

        filename_data = receive_exact(
            client_socket,
            filename_length
        )

        filename = filename_data.decode(
            "utf-8"
        )

        filename = os.path.basename(
            filename
        )


      

        file_size_data = receive_exact(
            client_socket,
            8
        )

        file_size = struct.unpack(
            "!Q",
            file_size_data
        )[0]



        file_path = os.path.join(
            RECEIVED_FOLDER,
            filename
        )

        name, extension = os.path.splitext(
            filename
        )

        counter = 1

        while os.path.exists(file_path):

            new_filename = (
                f"{name}_{counter}"
                f"{extension}"
            )

            file_path = os.path.join(
                RECEIVED_FOLDER,
                new_filename
            )

            counter += 1


        

        received = 0

        with open(
            file_path,
            "wb"
        ) as file:

            while received < file_size:

                remaining = (
                    file_size - received
                )

                chunk_size = min(
                    BUFFER_SIZE,
                    remaining
                )

                data = client_socket.recv(
                    chunk_size
                )

                if not data:

                    raise ConnectionError(
                        "Connection lost."
                    )

                file.write(data)

                received += len(data)


        print("\n" + "=" * 55)
        print("FILE RECEIVED SUCCESSFULLY")
        print("=" * 55)

        print(
            "Sender IP :",
            client_address[0]
        )

        print(
            "File      :",
            os.path.basename(file_path)
        )

        print(
            "Size      :",
            file_size,
            "bytes"
        )

        print(
            "Saved at  :",
            file_path
        )

        print(
            "Time      :",
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        print("=" * 55)


        # Confirmation
        client_socket.sendall(
            b"FILE_RECEIVED"
        )


    except Exception as error:

        print(
            "Receiving error:",
            error
        )

        try:

            client_socket.sendall(
                b"TRANSFER_FAILED"
            )

        except:
            pass

    finally:

        client_socket.close()


def start_tcp_server():

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind(
        ("0.0.0.0", TCP_PORT)
    )

    server_socket.listen(10)

    print(
        f"TCP receiver listening on "
        f"port {TCP_PORT}"
    )

    while True:

        client_socket, client_address = (
            server_socket.accept()
        )

        print(
            f"\nIncoming connection from "
            f"{client_address[0]}"
        )

        thread = threading.Thread(
            target=receive_file,
            args=(
                client_socket,
                client_address
            ),
            daemon=True
        )

        thread.start()
