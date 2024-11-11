// Language selection
let selectedLanguage = 'English';

function selectLanguage(language) {
    selectedLanguage = language;
    document.getElementById('languagebutton').textContent = language;
}

// Handle question submission
document.getElementById('submit--question').addEventListener('click', function() {
    const questionInput = document.getElementById('questionInput');
    const answerBody = document.getElementById('answerBody');
    const markdown = document.getElementById('markdown');
    const question = questionInput.value.trim();

    if (!question) return; // Exit if no question is provided

    // Display user's question
    const userMessageDiv = document.createElement('div');
    userMessageDiv.classList.add('message--div', 'mx-5');
    userMessageDiv.innerHTML = `<p class="user--message message">${question}</p>`;
    answerBody.appendChild(userMessageDiv);
    
    // Send question to server
    fetch('http://127.0.0.1:8000/get_answer/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'question': question, 'language': selectedLanguage })
    })
    .then(response => response.json())
    .then(data => {
        let modelMessage = data.answer || "No answer received";
        

        // Create a div for the answer
        const modelMessageDiv = document.createElement('div');
        modelMessageDiv.classList.add('user--model', 'message', 'mx-5', 'text-light');

        // Insert the formatted HTML into the div
        modelMessageDiv.innerHTML = modelMessage;
        
        // Append the answer to the body
        answerBody.appendChild(modelMessageDiv);
    })
    .catch(error => {
        console.error('Error:', error);
        const errorDiv = document.createElement('p');
        errorDiv.classList.add('error--message', 'text-danger', 'mx-5');
        errorDiv.textContent = "An error occurred while fetching the answer.";
        answerBody.appendChild(errorDiv);
    });
    
    questionInput.value = ''; // Clear the input field
});
function convertToMarkdown(text) {
  return `## ${text}`; // Simple conversion: turning text into a Markdown heading
}

// File upload handling
const fileUpload = document.getElementById('file-upload');
const fileList = document.getElementById('file-list');
const processPdfButton = document.getElementById('process--pdf');
const pdfArray = [];

fileUpload.addEventListener('change', function() {
  // Add new files to pdfArray without clearing existing files
  Array.from(fileUpload.files).forEach(file => {
      if (!pdfArray.some(existingFile => existingFile.name === file.name)) {
          pdfArray.push(file); // Only add unique files
      }
  });

  fileList.innerHTML = '';

  pdfArray.forEach(file => {
      const fileDiv = document.createElement('div');
      fileDiv.className = "text-white input--display d-flex align-items-center justify-content-around mt-2";
      fileDiv.style.backgroundColor = "#2c2c2c";

      fileDiv.innerHTML = `
          <div id="${file.name}" class="${file.name}">
            <div class="file_info" id="file_info #{}">
                ${file.name}
            </div>
          </div>
      `;
      fileList.appendChild(fileDiv);
  });
});

// Process PDF files
processPdfButton.addEventListener('click', function() {
    if (pdfArray.length) {
        const formData = new FormData();
        pdfArray.forEach(file => formData.append('pdfs', file));

        fetch('http://127.0.0.1:8000/get_embedding/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('PDF embedded successfully');
            alert('PDFs processed successfully!');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing the PDFs.');
        });
    } else {
        alert('Please select at least one PDF file.');
    }
});


document.addEventListener('DOMContentLoaded', function() {
    // Add copy buttons to all code blocks
    document.querySelectorAll('.markdown-content pre').forEach(block => {
        const button = document.createElement('button');
        button.className = 'code-copy-button';
        button.textContent = 'Copy';
        
        button.addEventListener('click', () => {
            const code = block.querySelector('code').textContent;
            navigator.clipboard.writeText(code).then(() => {
                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = 'Copy';
                }, 2000);
            });
        });
        
        block.appendChild(button);
    });
});