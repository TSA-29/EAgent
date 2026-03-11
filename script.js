let userAnswers = {};
let examData = null;

function normalizeAnswer(value) {
    return String(value || '').trim().toUpperCase();
}

async function send() {
    const input = document.getElementById('input');
    const chat = document.getElementById('chat');
    const message = input.value.trim();
    if (!message) return;

    chat.innerHTML += `<div class="message user"><div class="user-bubble">${message}</div></div>`;
    input.value = '';
    chat.scrollTop = chat.scrollHeight;

    try {
        const res = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        const data = await res.json();

        if (data.type === 'greeting') {
            let html = '<div class="message agent"><div class="agent-bubble">';
            html += data.message.replace(/\n/g, '<br>');
            html += '<button class="practice-btn" onclick="startPractice()">Practice Now</button>';
            html += '</div></div>';
            chat.innerHTML += html;
        }
        chat.scrollTop = chat.scrollHeight;
    } catch (e) {
        chat.innerHTML += `<div class="error">Error: ${e.message}</div>`;
    }
}

async function startPractice() {
    const chat = document.getElementById('chat');
    userAnswers = {};

    try {
        const res = await fetch('/start_practice', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await res.json();

        console.log('Raw response:', data);
        let parsedExam = null;
        let jsonData = data.data;

        if (jsonData && typeof jsonData === 'object') {
            parsedExam = jsonData;
        } else {
            jsonData = String(jsonData || '');

            if (jsonData.includes('```json')) {
                jsonData = jsonData.split('```json')[1].split('```')[0].trim();
            } else if (jsonData.includes('```')) {
                jsonData = jsonData.split('```')[1].split('```')[0].trim();
            }

            const jsonMatch = jsonData.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                jsonData = jsonMatch[0];
            }

            console.log('Parsed JSON string:', jsonData);
            parsedExam = JSON.parse(jsonData);
        }

        examData = parsedExam;
        console.log('Exam data:', examData);

        if (!examData.questions || examData.questions.length === 0) {
            throw new Error('No questions found in response');
        }

        displayExam(examData);
        chat.scrollTop = chat.scrollHeight;
    } catch (e) {
        console.error('Parse error:', e);
        chat.innerHTML += '<div class="error">Error loading exam. Check console for details.</div>';
    }
}

function displayExam(data) {
    const chat = document.getElementById('chat');
    let html = '<div class="exam-container">';
    html += '<h2 class="exam-title">English Practice Test</h2>';

    data.questions.forEach((q, index) => {
        const displayId = q.id != null ? q.id : index + 1;
        html += `<div class="question-card" id="q${index}">`;
        html += `<div class="question-title">Question ${displayId}</div>`;
        html += `<div class="question-text">${q.question}</div>`;
        html += '<div class="options">';

        ['A', 'B', 'C', 'D'].forEach((opt) => {
            const inputId = `q${index}${opt}`;
            const optionText = q.options && q.options[opt] ? q.options[opt] : '';
            html += `<div class="option" data-q-index="${index}" data-option="${opt}" onclick="selectAnswer(${index}, '${opt}')">`;
            html += `<input type="radio" name="q${index}" id="${inputId}" value="${opt}">`;
            html += `<label for="${inputId}">${opt}. ${optionText}</label>`;
            html += '</div>';
        });

        html += '</div></div>';
    });

    html += '<button class="submit-btn" onclick="submitAnswers()">Submit Answers</button>';
    html += '</div>';
    chat.innerHTML += html;
}

function selectAnswer(questionIndex, option) {
    userAnswers[questionIndex] = option;

    document.querySelectorAll(`.option[data-q-index="${questionIndex}"]`).forEach((optionEl) => {
        const isSelected = optionEl.dataset.option === option;
        optionEl.classList.toggle('selected', isSelected);

        const input = optionEl.querySelector('input[type="radio"]');
        if (input) input.checked = isSelected;
    });
}

function submitAnswers() {
    if (!examData || !examData.questions) return;

    const allAnswered = examData.questions.every((_, index) => index in userAnswers);
    if (!allAnswered) {
        alert('Please answer all questions before submitting.');
        return;
    }

    let correct = 0;
    examData.questions.forEach((q, index) => {
        const userAnswer = normalizeAnswer(userAnswers[index]);
        const correctAnswer = normalizeAnswer(q.answer);
        if (userAnswer === correctAnswer) correct++;
    });

    displayResults(correct, examData.questions.length);
}

function displayResults(correct, total) {
    const chat = document.getElementById('chat');
    let html = '<div class="results-container">';
    html += `<h2 class="score">Score: ${correct} / ${total}</h2>`;

    examData.questions.forEach((q, index) => {
        const displayId = q.id != null ? q.id : index + 1;
        const userAnswer = normalizeAnswer(userAnswers[index]);
        const correctAnswer = normalizeAnswer(q.answer);
        const isCorrect = userAnswer === correctAnswer;

        html += `<div class="result-card ${isCorrect ? 'correct' : 'incorrect'}">`;
        html += `<div class="question-title">Question ${displayId}</div>`;
        html += `<div class="question-text">${q.question}</div>`;
        html += '<div class="answer-info">';
        html += `<div>Your answer: ${userAnswer || '-'} ${isCorrect ? '(correct)' : '(wrong)'}</div>`;
        if (!isCorrect) {
            html += `<div class="correct-answer">Correct answer: ${correctAnswer || '-'}</div>`;
        }
        html += '</div></div>';
    });

    html += '</div>';
    chat.innerHTML += html;
    chat.scrollTop = chat.scrollHeight;
}

document.getElementById('input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') send();
});
