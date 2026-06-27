const attempts = document.getElementById("attempts");
const attemptsBox = document.querySelector(".remaining-attempts");
const check = document.querySelector(".submit-button");
const resultImg = document.getElementById("game-result-img");

const game = {
    attempts_left: 9, // 남은 횟수
    answer: [], //정답
    gameover: false, // 게임 종료
    strike_count: 0, // 스트라이크 횟수 초기화
    ball_count: 0, // 볼 횟수 초기화
    out_count: 0 // 아웃 카운트 초기화
};

const input_num = [
    document.getElementById("number1"),
    document.getElementById("number2"),
    document.getElementById("number3")
];

function updateUI() {
    attempts.textContent = game.attempts_left;
    attemptsBox.style.display = "none";
}

function create_answer() {
    game.answer = [];

    while (game.answer.length < 3) {
        const randomNumber = Math.floor(Math.random() * 10);
        const alreadyExists = game.answer.includes(randomNumber);

        if (alreadyExists === false) {
            game.answer.push(randomNumber);
        }
    }
}

function makeResultLine(userNumbers) {
    const results = document.getElementById("results");
    const resultLine = document.createElement("div");
    const leftText = document.createElement("span");
    const colonText = document.createElement("span");
    const rightText = document.createElement("span");

    resultLine.className = "check-result";
    resultLine.style.width = "100%";
    resultLine.style.display = "grid";
    resultLine.style.gridTemplateColumns = "repeat(3, 1fr)";
    resultLine.style.alignItems = "center";
    leftText.className = "left";
    rightText.className = "right";
    rightText.style.display = "inline-flex";
    rightText.style.alignItems = "center";
    rightText.style.gap = "8px";

    leftText.textContent = userNumbers.join(" ");
    colonText.textContent = ":";
    colonText.style.textAlign = "center";

    resultLine.appendChild(leftText);
    resultLine.appendChild(colonText);
    resultLine.appendChild(rightText);
    results.appendChild(resultLine);

    return rightText;
}

function printOut(userNumbers) {
    const rightText = makeResultLine(userNumbers);
    const outText = document.createElement("span");

    outText.textContent = "O";
    outText.className = "num-result out";
    outText.style.display = "inline-flex";
    outText.style.alignItems = "center";
    outText.style.justifyContent = "center";
    outText.style.width = "30px";
    outText.style.height = "35px";
    outText.style.padding = "0";

    rightText.appendChild(outText);
}

function printStrikeBall(strike, ball, userNumbers) {
    const rightText = makeResultLine(userNumbers);
    const strikeCount = document.createElement("span");
    const strikeText = document.createElement("span");
    const ballCount = document.createElement("span");
    const ballText = document.createElement("span");

    strikeCount.textContent = strike;
    strikeText.textContent = "S";
    strikeText.className = "num-result strike";
    strikeText.style.display = "inline-flex";
    strikeText.style.alignItems = "center";
    strikeText.style.justifyContent ="center";
    strikeText.style.width = "30px";
    strikeText.style.height = "35px";
    strikeText.style.padding = "0";

    ballCount.textContent = ball;
    ballText.textContent = "B";
    ballText.className = "num-result ball";
    ballText.style.display = "inline-flex";
    ballText.style.alignItems = "center";
    ballText.style.justifyContent = "center";
    ballText.style.width = "30px";
    ballText.style.height = "35px";
    ballText.style.padding = "0";

    rightText.appendChild(strikeCount);
    rightText.appendChild(strikeText);
    rightText.appendChild(ballCount);
    rightText.appendChild(ballText);
}

function clearInput() {
    for (let i = 0; i < input_num.length; i++) {
        input_num[i].value = "";
    }
}

function check_numbers() {
    if (game.gameover) {
        return;
    }

    let hasEmptyInput = false;

    for (let j = 0; j < input_num.length; j++) {
        if (input_num[j].value === "") {
            hasEmptyInput = true;
        }
    }

    if (hasEmptyInput) {
        clearInput();
        return;
    }

    game.strike_count = 0;
    game.ball_count = 0;
    game.out_count = 0;

    const userNumbers = [];

    for (let i = 0; i < 3; i++) {
        const userNumber = Number(input_num[i].value);

        userNumbers.push(userNumber);

        if (userNumber === game.answer[i]) {
            game.strike_count++;
        } else if (game.answer.includes(userNumber)) {
            game.ball_count++;
        } else {
            game.out_count++;
        }
    }

    game.attempts_left--;
    updateUI();

    if (game.strike_count === 0 && game.ball_count === 0) {
        printOut(userNumbers);
    } else {
        printStrikeBall(game.strike_count, game.ball_count, userNumbers);
    }

    if (game.strike_count === 3) {
        resultImg.src = "success.png";
        game.gameover = true;
        check.disabled = true;
    } else if (game.attempts_left === 0) {
        resultImg.src = "fail.png";
        game.gameover = true;
        check.disabled = true;
    }

    clearInput();
}

window.check_numbers = check_numbers;
create_answer();
updateUI();
clearInput();


