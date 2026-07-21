// =========================================
// FASTAPI URL
// =========================================
const API_URL = "http://localhost:8000";

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

// State Variables
let selectedFile = null;
let resumeUploaded = false;

// =========================================
// CHECK FASTAPI CONNECTION
// =========================================
async function checkAPI() {
    try {
        const response = await fetch(`${API_URL}/health`);

        if (!response.ok) {
            throw new Error("API connection failed");
        }

        apiStatus.textContent = "API Connected";
        statusDot.classList.add("connected");
        statusDot.classList.remove("disconnected");
    } catch (error) {
        console.error(error);
        apiStatus.textContent = "API Disconnected";
        statusDot.classList.add("disconnected");
        statusDot.classList.remove("connected");
    }
}

checkAPI();

// =========================================
// DRAG & DROP & FILE SELECTION
// =========================================
dropZone.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
    if (fileInput.files.length > 0) {
        handleFile(fileInput.files[0]);
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

// =========================================
// HANDLE SELECTED FILE
// =========================================
function handleFile(file) {
    if (file.type !== "application/pdf" && !file.name.endsWith(".pdf")) {
        showUploadMessage("Please select a valid PDF file.", "error");
        return;
    }

    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);

    fileInfo.classList.remove("hidden");
    uploadButton.disabled = false;
    hideUploadMessage();
}

function formatFileSize(bytes) {
    if (bytes < 1024) return `${bytes} Bytes`;
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
}

removeFileButton.addEventListener("click", () => {
    selectedFile = null;
    fileInput.value = "";
    fileInfo.classList.add("hidden");
    uploadButton.disabled = true;
    hideUploadMessage();
});

// =========================================
// UPLOAD AND ANALYZE RESUME
// =========================================
uploadButton.addEventListener("click", async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("file", selectedFile);

    // Show loading UI
    analysisEmpty.classList.add("hidden");
    analysisResult.classList.add("hidden");
    analysisLoading.classList.remove("hidden");

    uploadButton.disabled = true;
    uploadButton.innerHTML = "<span>Analyzing...</span>";

    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Upload failed");
        }

        // Hide loading and show results
        analysisLoading.classList.add("hidden");
        analysisResult.classList.remove("hidden");

        // Format object responses cleanly if analysis is structured JSON
        analysisResult.textContent =
            typeof data.analysis === "object"
                ? JSON.stringify(data.analysis, null, 2)
                : data.analysis;

        showUploadMessage("Resume analyzed successfully!", "success");

        // Enable Chat Input
        resumeUploaded = true;
        questionInput.disabled = false;
        sendButton.disabled = false;
        questionInput.placeholder = "Ask something about your resume...";
    } catch (error) {
        analysisLoading.classList.add("hidden");
        analysisEmpty.classList.remove("hidden");
        showUploadMessage(error.message, "error");
    } finally {
        uploadButton.disabled = false;
        uploadButton.innerHTML = `
            <span>Analyze Resume</span>
            <span>→</span>
        `;
    }
});

// =========================================
// CHAT FUNCTIONALITY
// =========================================
async function sendQuestion() {
    const question = questionInput.value.trim();

    if (!question || !resumeUploaded) return;

    addMessage(question, "user");
    questionInput.value = "";
    sendButton.disabled = true;

    const loadingMessage = addMessage("Thinking...", "ai");

    try {
        const response = await fetch(`${API_URL}/ask`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ question }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Failed to get answer");
        }

        loadingMessage.querySelector(".message-content").textContent = data.answer;
    } catch (error) {
        loadingMessage.querySelector(".message-content").textContent =
            "Error: " + error.message;
    } finally {
        sendButton.disabled = false;
        questionInput.focus();
    }
}

sendButton.addEventListener("click", sendQuestion);

questionInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        sendQuestion();
    }
});

document.querySelectorAll(".suggestion").forEach((button) => {
    button.addEventListener("click", () => {
        if (!resumeUploaded) return;
        questionInput.value = button.textContent.trim();
        sendQuestion();
    });
});

// =========================================
// CHAT MESSAGE HELPERS
// =========================================
function addMessage(text, type) {
    const message = document.createElement("div");
    message.classList.add("chat-message");
    message.classList.add(type === "user" ? "user-message" : "ai-message");

    const avatar = type === "user" ? "YOU" : "AI";

    message.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content"></div>
    `;

    message.querySelector(".message-content").textContent = text;
    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    return message;
}

function showUploadMessage(text, type) {
    uploadMessage.textContent = text;
    uploadMessage.className = `message ${type}`;
}

function hideUploadMessage() {
    uploadMessage.className = "message hidden";
}