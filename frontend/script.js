// =========================================
// FASTAPI URL CONFIGURATION
// =========================================

/// =========================================
// FASTAPI URL CONFIGURATION
// =========================================

const API_URL =
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
        ? "http://localhost:8000"
        : "https://rag-ai-resume-analyzer-1.onrender.com";

console.log("API URL:", API_URL);


// =========================================
// GET HTML ELEMENTS
// =========================================

const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("resume-file");
const fileInfo = document.getElementById("file-info");
const fileName = document.getElementById("file-name");
const fileSize = document.getElementById("file-size");
const removeFileButton = document.getElementById("remove-file");
const uploadButton = document.getElementById("upload-button");
const uploadMessage = document.getElementById("upload-message");

const analysisEmpty = document.getElementById("analysis-empty");
const analysisLoading = document.getElementById("analysis-loading");
const analysisResult = document.getElementById("analysis-result");

const questionInput = document.getElementById("question-input");
const sendButton = document.getElementById("send-button");
const chatMessages = document.getElementById("chat-messages");

const apiStatus = document.getElementById("api-status");
const statusDot = document.getElementById("status-dot");


// =========================================
// STATE VARIABLES
// =========================================

let selectedFile = null;
let resumeUploaded = false;


// =========================================
// CHECK FASTAPI CONNECTION
// =========================================

async function checkAPI(retries = 3, delay = 3000) {

    if (apiStatus) {
        apiStatus.textContent = "Connecting to API...";
    }

    if (statusDot) {
        statusDot.classList.remove("connected");
        statusDot.classList.remove("disconnected");
    }

    for (let attempt = 1; attempt <= retries; attempt++) {

        try {

            console.log(
                `Checking API: ${API_URL}/health`
            );

            const response = await fetch(
                `${API_URL}/health`,
                {
                    method: "GET",
                    headers: {
                        "Accept": "application/json"
                    }
                }
            );

            if (!response.ok) {
                throw new Error(
                    `API returned status ${response.status}`
                );
            }

            const data = await response.json().catch(() => ({}));

            console.log("API connected:", data);

            if (apiStatus) {
                apiStatus.textContent = "API Connected";
            }

            if (statusDot) {
                statusDot.classList.add("connected");
                statusDot.classList.remove("disconnected");
            }

            return true;

        } catch (error) {

            console.warn(
                `API Connection Attempt ${attempt} failed:`,
                error
            );

            if (attempt < retries) {

                if (apiStatus) {
                    apiStatus.textContent =
                        `Waking up server... (${attempt}/${retries})`;
                }

                await new Promise(
                    resolve => setTimeout(resolve, delay)
                );
            }
        }
    }

    if (apiStatus) {
        apiStatus.textContent = "API Disconnected";
    }

    if (statusDot) {
        statusDot.classList.add("disconnected");
        statusDot.classList.remove("connected");
    }

    console.error(
        "Could not connect to FastAPI:",
        `${API_URL}/health`
    );

    return false;
}


// =========================================
// PAGE LOAD
// =========================================

document.addEventListener("DOMContentLoaded", () => {

    console.log("Frontend loaded");
    console.log("API URL:", API_URL);

    checkAPI();

});


// =========================================
// DRAG & DROP
// =========================================

if (dropZone) {

    dropZone.addEventListener("click", () => {

        if (fileInput) {
            fileInput.click();
        }

    });


    dropZone.addEventListener("dragover", (event) => {

        event.preventDefault();

        dropZone.classList.add("drag-over");

    });


    dropZone.addEventListener("dragleave", () => {

        dropZone.classList.remove("drag-over");

    });


    dropZone.addEventListener("drop", (event) => {

        event.preventDefault();

        dropZone.classList.remove("drag-over");

        const file = event.dataTransfer.files[0];

        if (file) {
            handleFile(file);
        }

    });

}


// =========================================
// FILE INPUT
// =========================================

if (fileInput) {

    fileInput.addEventListener("change", () => {

        if (fileInput.files.length > 0) {

            handleFile(
                fileInput.files[0]
            );

        }

    });

}


// =========================================
// HANDLE SELECTED FILE
// =========================================

function handleFile(file) {

    if (
        file.type !== "application/pdf" &&
        !file.name.toLowerCase().endsWith(".pdf")
    ) {

        showUploadMessage(
            "Please select a valid PDF file.",
            "error"
        );

        return;
    }


    selectedFile = file;


    if (fileName) {
        fileName.textContent = file.name;
    }


    if (fileSize) {
        fileSize.textContent =
            formatFileSize(file.size);
    }


    if (fileInfo) {
        fileInfo.classList.remove("hidden");
    }


    if (uploadButton) {
        uploadButton.disabled = false;
    }


    hideUploadMessage();

}


// =========================================
// FORMAT FILE SIZE
// =========================================

function formatFileSize(bytes) {

    if (bytes < 1024) {

        return `${bytes} Bytes`;

    }


    if (bytes < 1024 * 1024) {

        return (
            (bytes / 1024).toFixed(1) +
            " KB"
        );

    }


    return (
        (bytes / (1024 * 1024)).toFixed(1) +
        " MB"
    );

}


// =========================================
// REMOVE FILE
// =========================================

if (removeFileButton) {

    removeFileButton.addEventListener(
        "click",
        () => {

            selectedFile = null;

            if (fileInput) {
                fileInput.value = "";
            }

            if (fileInfo) {
                fileInfo.classList.add("hidden");
            }

            if (uploadButton) {
                uploadButton.disabled = true;
            }

            hideUploadMessage();

        }
    );

}


// =========================================
// UPLOAD AND ANALYZE RESUME
// =========================================

if (uploadButton) {

    uploadButton.addEventListener(
        "click",
        async () => {

            if (!selectedFile) {

                showUploadMessage(
                    "Please select a PDF resume first.",
                    "error"
                );

                return;
            }


            const formData = new FormData();

            formData.append(
                "file",
                selectedFile
            );


            // Show loading UI

            if (analysisEmpty) {
                analysisEmpty.classList.add("hidden");
            }

            if (analysisResult) {
                analysisResult.classList.add("hidden");
            }

            if (analysisLoading) {
                analysisLoading.classList.remove("hidden");
            }


            uploadButton.disabled = true;

            uploadButton.innerHTML =
                "<span>Analyzing...</span>";


            try {

                console.log(
                    "Uploading resume to:",
                    `${API_URL}/upload`
                );


                const response = await fetch(
                    `${API_URL}/upload`,
                    {
                        method: "POST",
                        body: formData
                    }
                );


                const data =
                    await response.json()
                        .catch(() => ({}));


                console.log(
                    "Upload response:",
                    data
                );


                if (!response.ok) {

                    throw new Error(
                        data.detail ||
                        `Upload failed (${response.status})`
                    );

                }


                // Hide loading

                if (analysisLoading) {
                    analysisLoading.classList.add("hidden");
                }


                // Show result

                if (analysisResult) {

                    analysisResult.classList.remove(
                        "hidden"
                    );


                    analysisResult.textContent =
                        typeof data.analysis === "object"
                            ? JSON.stringify(
                                data.analysis,
                                null,
                                2
                            )
                            : (
                                data.analysis ||
                                "Analysis completed successfully."
                            );

                }


                showUploadMessage(
                    "Resume analyzed successfully!",
                    "success"
                );


                // Enable chat

                resumeUploaded = true;


                if (questionInput) {

                    questionInput.disabled = false;

                    questionInput.placeholder =
                        "Ask something about your resume...";

                }


                if (sendButton) {
                    sendButton.disabled = false;
                }


            } catch (error) {

                console.error(
                    "Resume upload error:",
                    error
                );


                if (analysisLoading) {
                    analysisLoading.classList.add(
                        "hidden"
                    );
                }


                if (analysisEmpty) {
                    analysisEmpty.classList.remove(
                        "hidden"
                    );
                }


                showUploadMessage(
                    error.message ||
                    "Failed to analyze resume.",
                    "error"
                );


            } finally {

                uploadButton.disabled = false;

                uploadButton.innerHTML = `
                    <span>Analyze Resume</span>
                    <span>→</span>
                `;

            }

        }
    );

}


// =========================================
// CHAT FUNCTIONALITY
// =========================================

async function sendQuestion() {

    if (!questionInput) {
        return;
    }


    const question =
        questionInput.value.trim();


    if (!question) {
        return;
    }


    if (!resumeUploaded) {

        addMessage(
            "Please upload and analyze your resume first.",
            "ai"
        );

        return;
    }


    // Add user message

    addMessage(
        question,
        "user"
    );


    questionInput.value = "";


    if (sendButton) {
        sendButton.disabled = true;
    }


    const loadingMessage =
        addMessage(
            "Thinking...",
            "ai"
        );


    try {

        console.log(
            "Sending question to:",
            `${API_URL}/ask`
        );


        const response =
            await fetch(
                `${API_URL}/ask`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",

                        "Accept":
                            "application/json"
                    },

                    body: JSON.stringify({
                        question: question
                    })
                }
            );


        const data =
            await response.json()
                .catch(() => ({}));


        console.log(
            "Question response:",
            data
        );


        if (!response.ok) {

            throw new Error(
                data.detail ||
                `Failed to get answer (${response.status})`
            );

        }


        const answer =
            data.answer ||
            "No answer received from the API.";


        if (loadingMessage) {

            const content =
                loadingMessage.querySelector(
                    ".message-content"
                );


            if (content) {
                content.textContent = answer;
            }

        }


    } catch (error) {

        console.error(
            "Question error:",
            error
        );


        if (loadingMessage) {

            const content =
                loadingMessage.querySelector(
                    ".message-content"
                );


            if (content) {

                content.textContent =
                    "Error: " +
                    error.message;

            }

        }

    } finally {

        if (sendButton) {
            sendButton.disabled = false;
        }


        questionInput.focus();

    }

}


// =========================================
// SEND BUTTON
// =========================================

if (sendButton) {

    sendButton.addEventListener(
        "click",
        sendQuestion
    );

}


// =========================================
// ENTER KEY
// =========================================

if (questionInput) {

    questionInput.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendQuestion();

            }

        }
    );

}


// =========================================
// SUGGESTION BUTTONS
// =========================================

document
    .querySelectorAll(".suggestion")
    .forEach((button) => {

        button.addEventListener(
            "click",
            () => {

                if (!resumeUploaded) {

                    addMessage(
                        "Please upload and analyze your resume first.",
                        "ai"
                    );

                    return;
                }


                if (!questionInput) {
                    return;
                }


                questionInput.value =
                    button.textContent.trim();


                sendQuestion();

            }
        );

    });


// =========================================
// CHAT MESSAGE HELPER
// =========================================

function addMessage(text, type) {

    if (!chatMessages) {
        return null;
    }


    const message =
        document.createElement("div");


    message.classList.add(
        "chat-message"
    );


    message.classList.add(
        type === "user"
            ? "user-message"
            : "ai-message"
    );


    const avatar =
        type === "user"
            ? "YOU"
            : "AI";


    message.innerHTML = `
        <div class="message-avatar">
            ${avatar}
        </div>

        <div class="message-content"></div>
    `;


    const content =
        message.querySelector(
            ".message-content"
        );


    if (content) {
        content.textContent = text;
    }


    chatMessages.appendChild(
        message
    );


    chatMessages.scrollTop =
        chatMessages.scrollHeight;


    return message;

}


// =========================================
// UPLOAD MESSAGE
// =========================================

function showUploadMessage(
    text,
    type
) {

    if (!uploadMessage) {
        return;
    }


    uploadMessage.textContent =
        text;


    uploadMessage.className =
        `message ${type}`;

}


function hideUploadMessage() {

    if (!uploadMessage) {
        return;
    }


    uploadMessage.className =
        "message hidden";

}