// ScreenPilot Chrome Extension - Popup Script
// Handles user interactions and communicates with content script and backend API

document.addEventListener('DOMContentLoaded', function() {
  const questionInput = document.getElementById('questionInput');
  const askButton = document.getElementById('askButton');
  const answerText = document.getElementById('answerText');
  const statusText = document.getElementById('statusText');

  // Handle Ask AI button click
  askButton.addEventListener('click', async function() {
    const question = questionInput.value.trim();
    
    if (!question) {
      showError('Please enter a question');
      return;
    }

    // Update UI to show loading state
    setLoadingState(true);
    updateStatus('Extracting page content...');

    try {
      // Step 1: Get the current active tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      if (!tab) {
        throw new Error('No active tab found');
      }

      updateStatus('Reading page content...');

      // Step 2: Send message to content script to extract page text
      const response = await chrome.tabs.sendMessage(tab.id, { 
        action: 'extractText' 
      });

      if (!response || !response.text) {
        throw new Error('Failed to extract text from page');
      }

      updateStatus('Sending to AI...');

      // Step 3: Send question and context to backend API
      const aiResponse = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question,
          context: response.text
        })
      });

      if (!aiResponse.ok) {
        throw new Error(`API request failed: ${aiResponse.status} ${aiResponse.statusText}`);
      }

      const aiData = await aiResponse.json();
      
      // Step 4: Display the AI response
      if (aiData.answer) {
        showAnswer(aiData.answer);
        updateStatus('AI analysis complete');
      } else {
        throw new Error('No answer received from AI');
      }

    } catch (error) {
      console.error('Error:', error);
      showError(`Error: ${error.message}`);
      updateStatus('Error occurred');
    } finally {
      setLoadingState(false);
    }
  });

  // Handle Enter key in textarea (Ctrl+Enter to submit)
  questionInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.ctrlKey) {
      askButton.click();
    }
  });

  // Helper functions
  function setLoadingState(isLoading) {
    askButton.disabled = isLoading;
    askButton.textContent = isLoading ? 'Analyzing...' : 'Ask AI';
    questionInput.disabled = isLoading;
  }

  function showAnswer(answer) {
    answerText.textContent = answer;
    answerText.className = 'answer-text';
  }

  function showError(message) {
    answerText.textContent = message;
    answerText.className = 'answer-text error';
  }

  function updateStatus(message) {
    statusText.textContent = message;
  }

  // Initialize status
  updateStatus('Ready to analyze this page');
});
