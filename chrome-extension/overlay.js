// ScreenPilot Chrome Extension - Overlay Script
// Creates a floating suggestion box on the page

(function() {
  if (document.getElementById("screenpilot-overlay")) return;

  const box = document.createElement("div");
  box.id = "screenpilot-overlay";
  box.innerHTML = `
    <div class="header">📘 ScreenPilot</div>
    <div id="screenpilot-text">Waiting for AI response...</div>
    <button id="screenpilot-close">✕</button>
  `;
  document.body.appendChild(box);

  document.getElementById("screenpilot-close").onclick = () => box.remove();

  window.addEventListener("message", (event) => {
    if (event.data.type === "SCREENPILOT_RESPONSE") {
      document.getElementById("screenpilot-text").innerText = event.data.data;
    }
  });
})();