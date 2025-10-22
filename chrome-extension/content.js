// ScreenPilot Chrome Extension - Content Script
// Listens for AI answers and injects overlay

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "SHOW_OVERLAY") {
    if (!document.getElementById("screenpilot-overlay")) {
      const script = document.createElement("script");
      script.src = chrome.runtime.getURL("overlay.js");
      (document.head || document.documentElement).appendChild(script);
    }
    window.postMessage({type: "SCREENPILOT_RESPONSE", data: msg.data}, "*");
  }
});