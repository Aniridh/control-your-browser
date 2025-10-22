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
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`${API_BASE}/upload`, { 
      method: "POST", 
      body: formData 
    });
    
    if (res.ok) {
      const data = await res.json();
      setStatus(`✅ Uploaded successfully: ${data.message}`);
    } else {
      const errorData = await res.json();
      setStatus(`Upload failed: ${errorData.detail || res.statusText}`, false);
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
        func: () => {
          // Extract text from the page
          const text = document.body.innerText || document.body.textContent || '';
          const title = document.title || '';
          const url = window.location.href;
          
          // Clean up the text
          const cleanText = text.replace(/\s+/g, ' ').trim();
          
          // Combine title and content
          const fullText = `${title}\n\n${cleanText}`.slice(0, 50000);
          
          return {
            text: fullText,
            url: url,
            title: title,
            length: fullText.length
          };
        },
      },
      async (results) => {
        const result = results[0].result;
        const pageText = result.text;
        const url = result.url;
        
        if (!pageText || pageText.length < 10) {
          setStatus("❌ No readable text found on this page", false);
          return;
        }
        
        setStatus(`Extracted ${result.length} characters from: ${result.title}`);
        
        try {
          const res = await fetch(`${API_BASE}/upload-web`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: pageText, url: url })
          });
          
          if (res.ok) {
            const data = await res.json();
            setStatus(`✅ Page indexed (${data.chunks_indexed} chunks)`);
          } else {
            const errorData = await res.json();
            setStatus(`Page analysis failed: ${errorData.detail || res.statusText}`, false);
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
    const res = await fetch(`${API_BASE}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    
    if (res.ok) {
      const data = await res.json();
      responseBox.innerText = data.answer || "No answer returned.";
      setStatus("AI analysis complete");
    } else {
      const errorData = await res.json();
      responseBox.innerText = `Error: ${errorData.detail || res.statusText}`;
      setStatus("Request failed", false);
    }
  } catch (err) {
    responseBox.innerText = "Error: " + err.message;
    setStatus("Request failed", false);
  }
});