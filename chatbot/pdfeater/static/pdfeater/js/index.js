const fileInput = document.getElementById('fileInput');
const questionInput = document.getElementById('questionInput');
const languageInput = document.getElementById('languageDropdown');
const submitButton = document.getElementById('submit--question');
const answerBody = document.getElementById('answerBody');
const process = document.getElementById('processFilesBtn');
const fileList = document.getElementById('fileList');
const languagebutton = document.getElementById('languagebutton');
languages = [
    "English",
    "Hindi",
    "Spanish",
    "French",
    "German",
    "Italian",
]

let language = languageDropdown.getAttribute('default-value');

languageInput.querySelectorAll('li').forEach(item => {
    item.addEventListener('click', () => {
        language = item.textContent;
        languagebutton.textContent = language;
    });
});

document.getElementById('uploadBox').addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', () => {
    fileList.innerHTML = '';
    for (const file of fileInput.files) {
        const fileItem = document.createElement('div');
        fileItem.textContent = file.name;
        fileList.appendChild(fileItem);
    }
});
process.addEventListener('click', () => {
        const formData = new FormData();
        for (const file of fileInput.files) {
            formData.append('files', file);
        }
        formData.append('language', language);
        console.log("Processing files...");

        fetch('/upload_and_process/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Files processed successfully!');
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error processing files');
        });
    });

    // Handle Q&A

function handleQuestion() {
        const question = questionInput.value.trim();
        if (question) {
            console.log('Sending question:', question);
            appendMessage(question, 'user');
            questionInput.value = '';

            fetch('/get_answer/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question , 'language': language })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Received response:', data);
                if (data.answer) {
                    appendMessage(data.answer, 'ai');
                } else {
                    appendMessage('No answer received from the server', 'ai');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                appendMessage('Error getting answer', 'ai');
            });
        }
    }

function appendMessage(message, type) {
    console.log('Appending message:', message, 'Type:', type);
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type === 'user' ? 'user--message' : 'user--model'}`;
    messageDiv.classList.add('markdown-body');
    messageDiv.innerHTML = marked.parse(message);
    answerBody.appendChild(messageDiv);
    answerBody.scrollTop = answerBody.scrollHeight;
}

submitButton.addEventListener('click', handleQuestion);
questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleQuestion();
});

