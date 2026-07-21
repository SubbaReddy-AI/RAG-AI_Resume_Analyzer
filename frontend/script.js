// =========================================
// FASTAPI URL
// =========================================

const API_URL = "https://rag-ai-resume-analyzers.onrender.com\models";
// =========================================
// GET HTML ELEMENTS
// =========================================
const dropZone =
    document.getElementById(
        "drop-zone"
    );

const fileInput =
    document.getElementById(
        "resume-file"
    );

const fileInfo =
    document.getElementById(
        "file-info"
    );

const fileName =
    document.getElementById(
        "file-name"
    );

const fileSize =
    document.getElementById(
        "file-size"
    );

const removeFileButton =
    document.getElementById(
        "remove-file"
    );

const uploadButton =
    document.getElementById(
        "upload-button"
    );

const uploadMessage =
    document.getElementById(
        "upload-message"
    );


const analysisEmpty =
    document.getElementById(
        "analysis-empty"
    );

const analysisLoading =
    document.getElementById(
        "analysis-loading"
    );

const analysisResult =
    document.getElementById(
        "analysis-result"
    );


const questionInput =
    document.getElementById(
        "question-input"
    );

const sendButton =
    document.getElementById(
        "send-button"
    );

const chatMessages =
    document.getElementById(
        "chat-messages"
    );


const apiStatus =
    document.getElementById(
        "api-status"
    );

const statusDot =
    document.getElementById(
        "status-dot"
    );


// Selected resume file
let selectedFile = null;


// Resume uploaded status
let resumeUploaded = false;


// =========================================
// CHECK FASTAPI CONNECTION
// =========================================

async function checkAPI() {

    try {

        const response =
            await fetch(
                `${API_URL}/`
            );


        if (!response.ok) {

            throw new Error(
                "API connection failed"
            );

        }


        apiStatus.textContent =
            "API Connected";


        statusDot.classList.add(
            "connected"
        );


        statusDot.classList.remove(
            "disconnected"
        );


    } catch (error) {

        apiStatus.textContent =
            "API Disconnected";


        statusDot.classList.add(
            "disconnected"
        );


        statusDot.classList.remove(
            "connected"
        );

    }

}


// Check API when page loads
checkAPI();


// =========================================
// CLICK DROP ZONE
// =========================================

dropZone.addEventListener(
    "click",
    () => {

        fileInput.click();

    }
);


// =========================================
// SELECT FILE
// =========================================

fileInput.addEventListener(
    "change",
    () => {

        if (
            fileInput.files.length > 0
        ) {

            handleFile(
                fileInput.files[0]
            );

        }

    }
);


// =========================================
// DRAG OVER
// =========================================

dropZone.addEventListener(
    "dragover",
    (event) => {

        event.preventDefault();

        dropZone.classList.add(
            "drag-over"
        );

    }
);


// =========================================
// DRAG LEAVE
// =========================================

dropZone.addEventListener(
    "dragleave",
    () => {

        dropZone.classList.remove(
            "drag-over"
        );

    }
);


// =========================================
// DROP FILE
// =========================================

dropZone.addEventListener(
    "drop",
    (event) => {

        event.preventDefault();

        dropZone.classList.remove(
            "drag-over"
        );


        const file =
            event.dataTransfer.files[0];


        if (file) {

            handleFile(file);

        }

    }
);


// =========================================
// HANDLE SELECTED FILE
// =========================================

function handleFile(file) {

    if (
        file.type !==
        "application/pdf"
    ) {

        showUploadMessage(
            "Please select a PDF file.",
            "error"
        );

        return;

    }


    selectedFile = file;


    fileName.textContent =
        file.name;


    fileSize.textContent =
        formatFileSize(
            file.size
        );


    fileInfo.classList.remove(
        "hidden"
    );


    uploadButton.disabled =
        false;


    hideUploadMessage();

}


// =========================================
// FORMAT FILE SIZE
// =========================================

function formatFileSize(bytes) {

    if (bytes < 1024) {

        return `${bytes} Bytes`;

    }


    if (
        bytes <
        1024 * 1024
    ) {

        return (
            bytes / 1024
        ).toFixed(1)
            + " KB";

    }


    return (
        bytes /
        (1024 * 1024)
    ).toFixed(1)
        + " MB";

}


// =========================================
// REMOVE FILE
// =========================================

removeFileButton.addEventListener(
    "click",
    () => {

        selectedFile = null;


        fileInput.value =
            "";


        fileInfo.classList.add(
            "hidden"
        );


        uploadButton.disabled =
            true;


        hideUploadMessage();

    }
);


// =========================================
// UPLOAD AND ANALYZE RESUME
// =========================================

uploadButton.addEventListener(
    "click",
    async () => {

        if (!selectedFile) {

            return;

        }


        const formData =
            new FormData();


        formData.append(
            "file",
            selectedFile
        );


        // Show loading
        analysisEmpty.classList.add(
            "hidden"
        );


        analysisResult.classList.add(
            "hidden"
        );


        analysisLoading.classList.remove(
            "hidden"
        );


        uploadButton.disabled =
            true;


        uploadButton.innerHTML =
            "<span>Analyzing...</span>";


        try {

            const response =
                await fetch(
                    `${API_URL}/upload`,
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Upload failed"
                );

            }


            // Hide loading
            analysisLoading.classList.add(
                "hidden"
            );


            // Show result
            analysisResult.classList.remove(
                "hidden"
            );


            analysisResult.textContent =
                data.analysis;


            showUploadMessage(
                "Resume analyzed successfully!",
                "success"
            );


            // Enable chat
            resumeUploaded =
                true;


            questionInput.disabled =
                false;


            sendButton.disabled =
                false;


            questionInput.placeholder =
                "Ask something about your resume...";


        } catch (error) {


            analysisLoading.classList.add(
                "hidden"
            );


            analysisEmpty.classList.remove(
                "hidden"
            );


            showUploadMessage(
                error.message,
                "error"
            );


        } finally {


            uploadButton.disabled =
                false;


            uploadButton.innerHTML =
                `
                <span>
                    Analyze Resume
                </span>

                <span>
                    →
                </span>
                `;

        }

    }
);


// =========================================
// SEND QUESTION
// =========================================

async function sendQuestion() {

    const question =
        questionInput.value.trim();


    if (
        !question ||
        !resumeUploaded
    ) {

        return;

    }


    // Add user message
    addMessage(
        question,
        "user"
    );


    questionInput.value =
        "";


    sendButton.disabled =
        true;


    // Temporary AI message
    const loadingMessage =
        addMessage(
            "Thinking...",
            "ai"
        );


    try {

        const response =
            await fetch(
                `${API_URL}/ask`,
                {

                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            question:
                                question
                        })

                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Failed to get answer"
            );

        }


        loadingMessage
            .querySelector(
                ".message-content"
            )
            .textContent =
            data.answer;


    } catch (error) {


        loadingMessage
            .querySelector(
                ".message-content"
            )
            .textContent =
            "Error: "
            + error.message;

    } finally {


        sendButton.disabled =
            false;


        questionInput.focus();

    }

}


// =========================================
// SEND BUTTON
// =========================================

sendButton.addEventListener(
    "click",
    sendQuestion
);


// =========================================
// ENTER KEY
// =========================================

questionInput.addEventListener(
    "keydown",
    (event) => {

        if (
            event.key ===
            "Enter"
        ) {

            sendQuestion();

        }

    }
);


// =========================================
// SUGGESTION BUTTONS
// =========================================

document
    .querySelectorAll(
        ".suggestion"
    )
    .forEach(
        button => {

            button.addEventListener(
                "click",
                () => {

                    if (
                        !resumeUploaded
                    ) {

                        return;

                    }


                    questionInput.value =
                        button.textContent
                            .trim();


                    sendQuestion();

                }
            );

        }
    );


// =========================================
// ADD CHAT MESSAGE
// =========================================

function addMessage(
    text,
    type
) {

    const message =
        document.createElement(
            "div"
        );


    message.classList.add(
        "chat-message"
    );


    if (
        type === "user"
    ) {

        message.classList.add(
            "user-message"
        );

    } else {

        message.classList.add(
            "ai-message"
        );

    }


    const avatar =
        type === "user"
            ? "YOU"
            : "AI";


    message.innerHTML =
        `
        <div class="message-avatar">
            ${avatar}
        </div>

        <div class="message-content">
        </div>
        `;


    message
        .querySelector(
            ".message-content"
        )
        .textContent =
        text;


    chatMessages.appendChild(
        message
    );


    chatMessages.scrollTop =
        chatMessages.scrollHeight;


    return message;

}


// =========================================
// SHOW UPLOAD MESSAGE
// =========================================

function showUploadMessage(
    text,
    type
) {

    uploadMessage.textContent =
        text;


    uploadMessage.className =
        `message ${type}`;

}


// =========================================
// HIDE UPLOAD MESSAGE
// =========================================

function hideUploadMessage() {

    uploadMessage.className =
        "message hidden";

}
