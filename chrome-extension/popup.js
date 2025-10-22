const API_BASE = "http://localhost:8000"; // update if deployed

const uploadBtn = document.getElementById("uploadBtn");
const pdfInput = document.getElementById("pdfFile");
const analyzePageBtn = document.getElementById("analyzePageBtn");
const askBtn = document.getElementById("askBtn");
const questionBox = document.getElementById("question");
const responseBox = document.getElementById("responseBox");
const statusBar = document.getElementById("statusBar");

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

  const formData = new FormData();
  formData.append("file", file);

  setStatus("Uploading document...");
  try {
    const res = await fetch(`${API_BASE}/upload`, { method: "POST", body: formData });
    const data = await res.json();
    setStatus(`✅ Uploaded successfully: ${data.message}`);
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
          const res = await fetch(`${API_BASE}/upload-web`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: pageText, url: tabs[0].url })
          });
          const data = await res.json();
          setStatus(`✅ Page indexed (${data.chunks_indexed} chunks)`);
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
      body: JSON.stringify({ question, context: "" }),
    });
    const data = await res.json();
    responseBox.innerText = data.answer || data.detail || "No answer returned.";
    setStatus("AI analysis complete");
  } catch (err) {
    responseBox.innerText = "Error: " + err.message;
    setStatus("Request failed", false);
  }
});