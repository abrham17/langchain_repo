console.log("Custom JavaScript is working!");
let selectedLanguage = 'English';

function selectLanguage(language) {
    selectedLanguage = language;
    document.getElementById('languagebutton').textContent = language;
}

const fileInput = document.getElementById('file--upload');
const pdfArray = [];
const fileNameDisplay = document.getElementById('file-name-display');
fileInput.addEventListener('change', function() {
    pdfArray.length = 0;
    Array.from(fileInput.files).forEach(file => pdfArray.push(file));
    fileNameDisplay.textContent = pdfArray.length ? pdfArray.map(file => file.name).join(', ') : 'No files selected';
});

document.getElementById('submit--question').addEventListener('click', function() {
    const questionInput = document.getElementById('questionInput');
    const question = questionInput.value.trim();
    if (!question) return;
    const userMessageDiv = document.createElement('div');
    userMessageDiv.classList.add('message--div', 'mx-5');
    userMessageDiv.innerHTML = `<p class="user--message message">${question}</p>`;
    answerBody.appendChild(userMessageDiv);

    fetch('http://127.0.0.1:8000/get_answer/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'question': question, 'language': selectedLanguage })
    })
    .then(response => response.json())
    .then(data => {
        const answerBody = document.getElementById('answerBody');
        const modelMessage = data.answer ? data.answer : "No answer received";
        const modelMessageDiv = document.createElement('p');
        modelMessageDiv.classList.add('user--model', 'message', 'mx-5' , 'text-light');
        modelMessageDiv.textContent = modelMessage;
        answerBody.appendChild(modelMessageDiv);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});

document.getElementById('process--pdf').addEventListener('click', function() {
    if (pdfArray.length) {
        const formData = new FormData();
        pdfArray.forEach(file => formData.append('pdfs', file));

        fetch('http://127.0.0.1:8000/get_embedding/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => console.log('PDF embedded successfully'))
        .catch(error => console.error('Error:', error));
    }
});

