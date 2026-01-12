const questions = document.querySelectorAll('.question-box');
const paletteBtns = document.querySelectorAll('.palette-btn');

let current = 0;

/* SHOW QUESTION */
function showQuestion(index) {
    questions.forEach(q => q.classList.remove('active'));
    paletteBtns.forEach(b => b.classList.remove('active'));

    questions[index].classList.add('active');
    paletteBtns[index].classList.add('active');

    document.getElementById('prevBtn').style.display =
        index === 0 ? 'none' : 'inline-block';

    document.getElementById('nextBtn').style.display =
        index === questions.length - 1 ? 'none' : 'inline-block';

    document.getElementById('submitBtn').classList.toggle(
        'hidden',
        index !== questions.length - 1
    );

    current = index;
}

/* BUTTONS */
document.getElementById('nextBtn').onclick = () => showQuestion(current + 1);
document.getElementById('prevBtn').onclick = () => showQuestion(current - 1);

function goToQuestion(index) {
    showQuestion(index);
}
const paletteButtons = document.querySelectorAll('.palette-btn');

paletteButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const index = parseInt(btn.dataset.index);
        goToQuestion(index);
    });
});


/* MARK ANSWERED */
document.querySelectorAll('input[type=radio]').forEach(radio => {
    radio.addEventListener('change', () => {
        paletteBtns[current].classList.add('answered');
    });
});
// ================= TIMER =================



/* TIMER */
let timeLeft = duration;
const timerEl = document.getElementById('time');

const timer = setInterval(() => {
    let min = Math.floor(timeLeft / 60);
    let sec = timeLeft % 60;
    timerEl.textContent = `${min}:${sec < 10 ? '0' : ''}${sec}`;

    if (timeLeft-- <= 0) {
        clearInterval(timer);
        document.getElementById('examForm').submit();
    }
}, 1000);


function startTimer() {
    const interval = setInterval(() => {

        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;

        timerEl.textContent =
            String(minutes).padStart(1, '0') + ':' +
            String(seconds).padStart(1, '0');

        if (timeLeft <= 0) {
            clearInterval(interval);
            alert("⏰ Time is up! Exam will be submitted automatically.");
            document.getElementById('examForm').submit();
        }

        timeLeft--;
    }, 1000);
}

startTimer();
showQuestion(0);

// ================= PREVENT REFRESH =================
window.onbeforeunload = function () {
    return "Exam is in progress. Leaving will submit the exam.";
};

// Disable back button
history.pushState(null, null, location.href);
window.onpopstate = function () {
    history.go(1);
};

const options = document.querySelectorAll('input[type=radio]');

options.forEach(option => {
    option.addEventListener('change', () => {
        const qBox = option.closest('.question-box');
        const index = qBox.dataset.index;
        document.querySelectorAll('.palette-btn')[index].classList.add('attempted');
    });
});

