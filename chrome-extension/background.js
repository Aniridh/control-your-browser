// ScreenPilot Chrome Extension - Background Service Worker
// Handles extension lifecycle and communication between components

console.log('ScreenPilot background service worker loaded');

// Extension installation handler
chrome.runtime.onInstalled.addListener((details) => {
  console.log('ScreenPilot extension installed:', details.reason);
  
  // Set default settings
  chrome.storage.sync.set({
    backendUrl: 'http://localhost:8000',
    sidebarEnabled: true,
    autoUpload: false
  });
});

// Handle messages from content scripts and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log('Background received message:', request);
  
  switch (request.action) {
    case 'uploadPDF':
      handlePDFUpload(request.data, sendResponse);
      return true; // Keep message channel open for async response
      
    case 'askQuestion':
      handleQuestion(request.data, sendResponse);
      return true;
      
    case 'uploadWebpage':
      handleWebpageUpload(request.data, sendResponse);
      return true;
      
    case 'checkBackendHealth':
      checkBackendHealth(sendResponse);
      return true;
      
    case 'toggleSidebar':
      toggleSidebar(request.data, sender.tab.id);
      sendResponse({ success: true });
      break;
      
    default:
      sendResponse({ error: 'Unknown action' });
  }
});

// Handle PDF upload to backend
async function handlePDFUpload(data, sendResponse) {
  try {
    const { file, filename } = data;
    
    // Convert file to FormData
    const formData = new FormData();
    formData.append('file', file, filename);
    
    // Get backend URL from storage
    const settings = await chrome.storage.sync.get(['backendUrl']);
    const backendUrl = settings.backendUrl || 'http://localhost:8000';
    
    // Upload to backend
    const response = await fetch(`${backendUrl}/upload`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    sendResponse({ success: true, data: result });
    
  } catch (error) {
    console.error('PDF upload error:', error);
    sendResponse({ success: false, error: error.message });
  }
}

// Handle webpage upload
async function handleWebpageUpload(data, sendResponse) {
  try {
    const { text, url } = data;
    
    // Get backend URL from storage
    const settings = await chrome.storage.sync.get(['backendUrl']);
    const backendUrl = settings.backendUrl || 'http://localhost:8000';
    
    // Upload webpage content to backend
    const response = await fetch(`${backendUrl}/upload-web`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text, url })
    });
    
    if (!response.ok) {
      throw new Error(`Webpage upload failed: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    sendResponse({ success: true, data: result });
    
  } catch (error) {
    console.error('Webpage upload error:', error);
    sendResponse({ success: false, error: error.message });
  }
}

// Handle question asking
async function handleQuestion(data, sendResponse) {
  try {
    const { question, useGemini = false } = data;
    
    // Get backend URL from storage
    const settings = await chrome.storage.sync.get(['backendUrl']);
    const backendUrl = settings.backendUrl || 'http://localhost:8000';
    
    // Choose endpoint based on useGemini flag
    const endpoint = useGemini ? '/ask-gemini' : '/ask';
    
    // Send question to backend
    const response = await fetch(`${backendUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question })
    });
    
    if (!response.ok) {
      throw new Error(`Question failed: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    sendResponse({ success: true, data: result });
    
  } catch (error) {
    console.error('Question error:', error);
    sendResponse({ success: false, error: error.message });
  }
}

// Check backend health
async function checkBackendHealth(sendResponse) {
  try {
    const settings = await chrome.storage.sync.get(['backendUrl']);
    const backendUrl = settings.backendUrl || 'http://localhost:8000';
    
    const response = await fetch(`${backendUrl}/health`);
    
    if (response.ok) {
      const health = await response.json();
      sendResponse({ success: true, data: health });
    } else {
      sendResponse({ success: false, error: 'Backend not responding' });
    }
    
  } catch (error) {
    console.error('Health check error:', error);
    sendResponse({ success: false, error: error.message });
  }
}

// Toggle sidebar visibility
function toggleSidebar(data, tabId) {
  chrome.tabs.sendMessage(tabId, {
    action: 'toggleSidebar',
    data: data
  });
}

// Handle tab updates to inject content script if needed
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    // Inject content script for all pages
    chrome.scripting.executeScript({
      target: { tabId: tabId },
      files: ['content.js']
    }).catch(error => {
      // Ignore errors for restricted pages
      console.log('Could not inject content script:', error);
    });
  }
});

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
  // Toggle sidebar when extension icon is clicked
  chrome.tabs.sendMessage(tab.id, {
    action: 'toggleSidebar',
    data: { show: true }
  });
});
