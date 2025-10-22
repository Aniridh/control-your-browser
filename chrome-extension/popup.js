const API_BASE = "http://localhost:8000";

const pdfInput = document.getElementById("pdfInput");
const uploadBtn = document.getElementById("uploadBtn");
const askBtn = document.getElementById("askBtn");
const questionBox = document.getElementById("question");
const responseBox = document.getElementById("responseBox");

uploadBtn.addEventListener("click", async () => {
  const file = pdfInput.files[0];
  if (!file) return alert("Select a PDF file first.");

  const formData = new FormData();
  formData.append("file", file);

  responseBox.innerText = "Uploading and indexing PDF...";
  try {
    const res = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    responseBox.innerText = `✅ ${data.message}`;
  } catch (err) {
    responseBox.innerText = `❌ Upload failed: ${err}`;
  }
});

askBtn.addEventListener("click", async () => {
  const question = questionBox.value.trim();
  if (!question) return alert("Type a question first.");

  responseBox.innerText = "Thinking...";
  try {
    const res = await fetch(`${API_BASE}/ask`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question})
    });
    const data = await res.json();
    responseBox.innerText = data.answer;
    // send to overlay
    chrome.tabs.query({active: true, currentWindow: true}, tabs => {
      chrome.tabs.sendMessage(tabs[0].id, {type: "SHOW_OVERLAY", data: data.answer});
    });
  } catch (err) {
    responseBox.innerText = `❌ Error: ${err}`;
  }
});