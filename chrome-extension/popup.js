// ScreenPilot Chrome Extension - Popup Script
// Handles PDF upload and AI question functionality

document.addEventListener('DOMContentLoaded', function() {
  // DOM elements
  const pdfInput = document.getElementById('pdfInput');
  const fileInfo = document.getElementById('fileInfo');
  const uploadBtn = document.getElementById('uploadBtn');
  const questionInput = document.getElementById('questionInput');
  const askBtn = document.getElementById('askBtn');
  const responseArea = document.getElementById('responseArea');
  const statusText = document.getElementById('statusText');

  // State
  let uploadedFile = null;
  let isUploading = false;
  let isAsking = false;

  // Initialize
  updateStatus('Ready to upload documents');

  // PDF Input Handler
  pdfInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    
    if (file) {
      if (file.type !== 'application/pdf') {
        showError('Please select a PDF file');
        return;
      }
      
      if (file.size > 10 * 1024 * 1024) { // 10MB limit
        showError('File size must be less than 10MB');
        return;
      }
      
      uploadedFile = file;
      fileInfo.textContent = `Selected: ${file.name} (${formatFileSize(file.size)})`;
      fileInfo.style.display = 'block';
      uploadBtn.disabled = false;
      updateStatus('Ready to upload');
    } else {
      uploadedFile = null;
      fileInfo.style.display = 'none';
      uploadBtn.disabled = true;
    }
  });

  // Upload Button Handler
  uploadBtn.addEventListener('click', async function() {
    if (!uploadedFile || isUploading) return;
    
    setUploadLoading(true);
    updateStatus('Uploading PDF...');
    
    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
      }
      
      const result = await response.json();
      
      // Success
      showSuccess('PDF uploaded successfully!');
      askBtn.disabled = false;
      updateStatus('Ready to ask questions');
      
    } catch (error) {
      console.error('Upload error:', error);
      showError(`Upload failed: ${error.message}`);
      updateStatus('Upload failed');
    } finally {
      setUploadLoading(false);
    }
  });

  // Ask Button Handler
  askBtn.addEventListener('click', async function() {
    const question = questionInput.value.trim();
    
    if (!question || isAsking) return;
    
    setAskLoading(true);
    updateStatus('Analyzing with AI...');
    showResponseLoading();
    
    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: question
        })
      });
      
      if (!response.ok) {
        throw new Error(`AI request failed: ${response.status} ${response.statusText}`);
      }
      
      const result = await response.json();
      
      // Display AI response
      if (result.answer) {
        showResponse(result.answer);
        updateStatus('AI analysis complete');
      } else {
        throw new Error('No answer received from AI');
      }
      
    } catch (error) {
      console.error('Ask error:', error);
      showResponseError(`Error: ${error.message}`);
      updateStatus('Analysis failed');
    } finally {
      setAskLoading(false);
    }
  });

  // Helper Functions
  function setUploadLoading(loading) {
    isUploading = loading;
    uploadBtn.disabled = loading || !uploadedFile;
    
    if (loading) {
      uploadBtn.classList.add('loading');
    } else {
      uploadBtn.classList.remove('loading');
    }
  }

  function setAskLoading(loading) {
    isAsking = loading;
    askBtn.disabled = loading || !questionInput.value.trim();
    
    if (loading) {
      askBtn.classList.add('loading');
    } else {
      askBtn.classList.remove('loading');
    }
  }

  function showResponse(text) {
    responseArea.innerHTML = `<div class="response-text">${text}</div>`;
  }

  function showResponseError(message) {
    responseArea.innerHTML = `<div class="response-error">${message}</div>`;
  }

  function showResponseLoading() {
    responseArea.innerHTML = '<div class="response-loading">AI is analyzing your question...</div>';
  }

  function showSuccess(message) {
    fileInfo.textContent = message;
    fileInfo.style.background = '#e8f5e8';
    fileInfo.style.color = '#27ae60';
  }

  function showError(message) {
    fileInfo.textContent = message;
    fileInfo.style.background = '#fdf2f2';
    fileInfo.style.color = '#e74c3c';
    fileInfo.style.display = 'block';
  }

  function updateStatus(message) {
    statusText.textContent = message;
  }

  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // Enable ask button when question is entered
  questionInput.addEventListener('input', function() {
    askBtn.disabled = !questionInput.value.trim() || isAsking;
  });

  // Keyboard shortcuts
  questionInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.ctrlKey) {
      askBtn.click();
    }
  });
});
