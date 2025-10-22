const API_BASE = "http://localhost:8000"; // update if deployed

const uploadBtn = document.getElementById("uploadBtn");
const pdfInput = document.getElementById("pdfFile");
const analyzePageBtn = document.getElementById("analyzePageBtn");
const askBtn = document.getElementById("askBtn");
const questionBox = document.getElementById("question");
const responseBox = document.getElementById("responseBox");
const statusBar = document.getElementById("statusBar");

// Check backend health on popup load
async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    if (response.ok) {
      setStatus("✅ Connected to ScreenPilot backend", true);
    } else {
      setStatus("❌ Backend connection failed", false);
    }
  } catch (err) {
    setStatus("❌ Backend not running - start server first", false);
  }
}

// Initialize popup
document.addEventListener('DOMContentLoaded', () => {
  checkBackendHealth();
});

function setStatus(msg, success = true) {
  statusBar.innerText = msg;
  statusBar.style.color = success ? "green" : "red";
}

// PDF Upload
uploadBtn.addEventListener("click", async () => {
  const file = pdfInput.files[0];
  if (!file) {
    setStatus("Please select a PDF first.", false);
    return;
  }

  setStatus("Uploading document...");
  try {
    // Use background script to handle the request
    const response = await chrome.runtime.sendMessage({
      action: 'uploadPDF',
      data: { file: file, filename: file.name }
    });
    
    if (response.success) {
      setStatus(`✅ Uploaded successfully: ${response.data.message}`);
    } else {
      setStatus("Upload failed: " + response.error, false);
    }
  } catch (err) {
    setStatus("Upload failed: " + err.message, false);
  }
});

// Analyze Current Page
analyzePageBtn.addEventListener("click", async () => {
  setStatus("Extracting page text...");
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.scripting.executeScript(
      {
        target: { tabId: tabs[0].id },
        func: () => document.body.innerText.slice(0, 50000), // limit to 50k chars
      },
      async (results) => {
        const pageText = results[0].result;
        setStatus("Sending page data to backend...");
        try {
          // Use background script to handle the request
          const response = await chrome.runtime.sendMessage({
            action: 'uploadWebpage',
            data: { text: pageText, url: tabs[0].url }
          });
          
          if (response.success) {
            setStatus(`✅ Page indexed (${response.data.chunks_indexed} chunks)`);
          } else {
            setStatus("Page analysis failed: " + response.error, false);
          }
        } catch (err) {
          setStatus("Page analysis failed: " + err.message, false);
        }
      }
    );
  });
});

// Ask AI
askBtn.addEventListener("click", async () => {
  const question = questionBox.value.trim();
  if (!question) return setStatus("Enter a question first.", false);

  responseBox.innerText = "Thinking...";
  setStatus("Querying backend...");
  
  try {
    // Use background script to handle the request
    const response = await chrome.runtime.sendMessage({
      action: 'askQuestion',
      data: { question }
    });
    
    if (response.success) {
      responseBox.innerText = response.data.answer || "No answer returned.";
      setStatus("AI analysis complete");
    } else {
      responseBox.innerText = "Error: " + response.error;
      setStatus("Request failed", false);
    }
  } catch (err) {
    responseBox.innerText = "Error: " + err.message;
    setStatus("Request failed", false);
  }
});