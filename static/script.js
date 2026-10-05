const receiverSelect =
    document.getElementById(
        "receiverSelect"
    );


const refreshButton =
    document.getElementById(
        "refreshButton"
    );


const discoveryStatus =
    document.getElementById(
        "discoveryStatus"
    );


const fileInput =
    document.getElementById(
        "fileInput"
    );


const selectedFile =
    document.getElementById(
        "selectedFile"
    );


const fileName =
    document.getElementById(
        "fileName"
    );


const fileSize =
    document.getElementById(
        "fileSize"
    );


const sendButton =
    document.getElementById(
        "sendButton"
    );


const transferStatus =
    document.getElementById(
        "transferStatus"
    );


const progressContainer =
    document.getElementById(
        "progressContainer"
    );


const progressFill =
    document.getElementById(
        "progressFill"
    );


const progressText =
    document.getElementById(
        "progressText"
    );


const progressStatus =
    document.getElementById(
        "progressStatus"
    );




async function discoverReceivers() {

    receiverSelect.innerHTML = "";

    const searchingOption =
        document.createElement(
            "option"
        );

    searchingOption.textContent =
        "Searching for systems...";

    searchingOption.value = "";

    receiverSelect.appendChild(
        searchingOption
    );


    discoveryStatus.textContent =
        "Searching your LAN...";

    refreshButton.disabled = true;


    try {

        const response =
            await fetch(
                "/discover"
            );


        const result =
            await response.json();


        receiverSelect.innerHTML =
            "";


        if (
            !result.devices ||
            result.devices.length === 0
        ) {

            const option =
                document.createElement(
                    "option"
                );

            option.value = "";

            option.textContent =
                "No FilePulse systems found";

            receiverSelect.appendChild(
                option
            );


            discoveryStatus.textContent =
                "No receivers found. Make sure FilePulse is running on another computer connected to the same LAN.";

            return;
        }


        const defaultOption =
            document.createElement(
                "option"
            );

        defaultOption.value = "";

        defaultOption.textContent =
            "Select a receiver...";

        receiverSelect.appendChild(
            defaultOption
        );


        result.devices.forEach(
            function(device) {

                const option =
                    document.createElement(
                        "option"
                    );


                option.value =
                    device.ip;


                option.dataset.port =
                    device.port;


                option.textContent =
                    `${device.name} — ${device.ip}`;


                receiverSelect.appendChild(
                    option
                );

            }
        );


        discoveryStatus.textContent =
            `${result.devices.length} receiver(s) found on your LAN.`;


    } catch (error) {

        receiverSelect.innerHTML =
            "";

        const option =
            document.createElement(
                "option"
            );

        option.textContent =
            "Discovery failed";

        receiverSelect.appendChild(
            option
        );


        discoveryStatus.textContent =
            "Could not search the LAN.";
    }


    refreshButton.disabled = false;
}




refreshButton.addEventListener(
    "click",
    discoverReceivers
);




fileInput.addEventListener(
    "change",
    function() {

        const file =
            fileInput.files[0];


        if (!file) {
            return;
        }


        selectedFile.style.display =
            "flex";


        fileName.textContent =
            file.name;


        fileSize.textContent =
            formatFileSize(
                file.size
            );
    }
);




function formatFileSize(bytes) {

    if (bytes < 1024) {

        return (
            bytes +
            " Bytes"
        );
    }


    if (bytes < 1024 * 1024) {

        return (
            bytes / 1024
        ).toFixed(2) +
        " KB";
    }


    if (
        bytes <
        1024 * 1024 * 1024
    ) {

        return (
            bytes /
            (1024 * 1024)
        ).toFixed(2) +
        " MB";
    }


    return (
        bytes /
        (1024 * 1024 * 1024)
    ).toFixed(2) +
    " GB";
}





sendButton.addEventListener(
    "click",
    function() {

        const selectedOption =
            receiverSelect
                .options[
                    receiverSelect.selectedIndex
                ];


        const receiverIP =
            receiverSelect.value;


        const receiverPort =
            selectedOption
                ?.dataset
                ?.port || "5000";


        const file =
            fileInput.files[0];


        /* Check receiver */

        if (!receiverIP) {

            showStatus(
                "Please select a receiver system.",
                "error"
            );

            return;
        }


        /* Check file */

        if (!file) {

            showStatus(
                "Please select a file.",
                "error"
            );

            return;
        }


        const formData =
            new FormData();


        formData.append(
            "receiver_ip",
            receiverIP
        );


        formData.append(
            "receiver_port",
            receiverPort
        );


        formData.append(
            "file",
            file
        );


        /* UI */

        sendButton.disabled =
            true;


        sendButton.textContent =
            "Sending...";


        progressContainer.style.display =
            "block";


        progressFill.style.width =
            "0%";


        progressText.textContent =
            "0%";


        progressStatus.textContent =
            "Uploading to FilePulse...";


        showStatus(
            `Connecting to ${receiverIP}...`,
            "sending"
        );


        /* XHR */

        const xhr =
            new XMLHttpRequest();


        xhr.open(
            "POST",
            "/send",
            true
        );


    

        xhr.upload.addEventListener(
            "progress",
            function(event) {

                if (
                    event.lengthComputable
                ) {

                    const percent =
                        Math.round(
                            (
                                event.loaded /
                                event.total
                            ) * 100
                        );


                    progressFill.style.width =
                        percent + "%";


                    progressText.textContent =
                        percent + "%";


                    progressStatus.textContent =
                        "Sending file over LAN...";
                }
            }
        );


        /* Response */

        xhr.onload =
            function() {

                sendButton.disabled =
                    false;


                sendButton.textContent =
                    "🚀 Send File";


                try {

                    const result =
                        JSON.parse(
                            xhr.responseText
                        );


                    if (
                        result.success
                    ) {

                        progressFill.style.width =
                            "100%";


                        progressText.textContent =
                            "100%";


                        progressStatus.textContent =
                            "Transfer completed";


                        showStatus(
                            "✓ File transferred successfully!",
                            "success"
                        );


                    } else {

                        showStatus(
                            "✕ " +
                            result.message,
                            "error"
                        );
                    }


                } catch {

                    showStatus(
                        "Invalid server response.",
                        "error"
                    );
                }
            };


        /* Error */

        xhr.onerror =
            function() {

                sendButton.disabled =
                    false;


                sendButton.textContent =
                    "🚀 Send File";


                showStatus(
                    "Network error occurred.",
                    "error"
                );
            };


        xhr.send(
            formData
        );
    }
);

function showStatus(
    message,
    type
) {

    transferStatus.textContent =
        message;


    if (type === "success") {

        transferStatus.style.color =
            "#16a34a";

        transferStatus.style.background =
            "#dcfce7";

    } else if (
        type === "error"
    ) {

        transferStatus.style.color =
            "#dc2626";

        transferStatus.style.background =
            "#fee2e2";

    } else {

        transferStatus.style.color =
            "#475569";

        transferStatus.style.background =
            "#f1f5f9";
    }
}



discoverReceivers();
