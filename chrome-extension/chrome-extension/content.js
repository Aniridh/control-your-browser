// ScreenPilot Chrome Extension - Content Script
// Runs on every webpage to extract visible text content

// Listen for messages from popup script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractText') {
    try {
      // Extract visible text from the page
      const pageText = extractVisibleText();
      
      // Send response back to popup
      sendResponse({
        success: true,
        text: pageText,
        url: window.location.href,
        title: document.title
      });
    } catch (error) {
      console.error('Error extracting text:', error);
      sendResponse({
        success: false,
        error: error.message
      });
    }
  }
  
  // Return true to indicate we will send a response asynchronously
  return true;
});

/**
 * Extract visible text content from the current page
 * @returns {string} Extracted text content (limited to ~5000 characters)
 */
function extractVisibleText() {
  // Get all visible text from the body
  let text = document.body.innerText || document.body.textContent || '';
  
  // Clean up the text
  text = text
    .replace(/\s+/g, ' ')  // Replace multiple whitespace with single space
    .replace(/\n\s*\n/g, '\n')  // Remove empty lines
    .trim();
  
  // Limit to approximately 5000 characters to avoid API limits
  if (text.length > 5000) {
    text = text.substring(0, 5000) + '...';
  }
  
  // Add page metadata for context
  const metadata = `\n\n--- Page Context ---\nURL: ${window.location.href}\nTitle: ${document.title}`;
  
  return text + metadata;
}

// Optional: Log when content script loads (for debugging)
console.log('ScreenPilot content script loaded on:', window.location.href);
