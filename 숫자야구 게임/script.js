/*
2. 게임 초기화
    1. 시도 가능 횟수를 설정합니다.
        > 입력한 숫자를 확인할 때마다 1씩 감소합니다.
    2. 중복되지 않는 3개의 랜덤한 숫자를 설정합니다.
    3. html의 input과 결과창의 내용을 비웁니다.
3. 숫자 확인
    > `submit-button`에 onclick 이벤트로 연결되어 있는 `check_numbers()`를 구현해야 합니다.
    1. 입력되지 않은 input 이 있다면 숫자를 확인하지 않고 input 창만 비웁니다.
    2. 숫자 3개가 입력되었다면 결과를 확인합니다.
        1. 입력된 숫자들과 정답을 비교하여 결과를 생성하는 로직 만들기
        2. 생성된 결과에 따라 html 업데이트하기
        3. 게임이 끝났는지 체크하고 결과에 따라 이미지를 출력합니다. 게임이 끝나면 **확인하기** 버튼은 비활성화합니다.
            - 이미지는 id가 `game-result-img`  img 태그를 사용합니다.
            - 승리 시 `success.png` , 패배 시 `fail.png` 를 출력합니다.
*/


const maxAttempts = 9; // 시도 가능 횟수
let answerNumbers = []; // 정답 숫자
let currentAttempts = 0; // 현재 남은 횟수

const input1 = document.getElementById('number1');
const input2 = document.getElementById('number2');
const input3 = document.getElementById('number3');
const submitBtn = document.querySelector('.submit-button');
const resultImg = document.getElementById('game-result-img');
const attempts_show = document.getElementById('attempts');
const resultsDiv = document.getElementById('results');



// 게임 초기화
function initGame() {
    const numbers = [1,2,3,4,5,6,7,8,9];
    answerNumbers = [];
    // 1. 시도 가능 횟수 초기화, 화면에 표시
    currentAttempts = maxAttempts;
    attempts_show.innerText = currentAttempts;
    // 2. 중복되지 않는 3개의 랜덤한 숫자 설정
    for (let i = 0; i < 3; i++) {
        const index = Math.floor(Math.random() * numbers.length);
        answerNumbers.push(numbers[index]);
        numbers.splice(index, 1)
    }

    console.log('정답: ', answerNumbers);

    // 3. html의 input과 결과창의 내용을 비웁니다.
    trash();
    resultsDiv.innerHTML = "";
    resultImg.src = "";

}


// 숫자 확인 (onclick='check_numbers()'로 연결)
function check_numbers() {

    let num1 = input1.value;
    let num2 = input2.value;
    let num3 = input3.value;

    // 1. 입력되지 않은 input 이 있는지? -> 숫자를 확인하지 않고 input 창만 비웁니다.
    if (num1 == "" || num2 == "" || num3 == "") {
        alert('3자리 숫자를 입력하세요');
        // input 창 비우기
        trash();
        return;
    }

    // 2. 숫자 3개가 입력되었다면 결과를 확인
    // 시도 횟수 1 감소, 화면에 표시
    let inputNumbers = [Number(num1), Number(num2), Number(num3)];

    currentAttempts --;
    attempts_show.innerText = currentAttempts;

    // 1) 입력된 숫자들과 정답을 비교하여 결과 생성
    let strike = 0;
    let ball = 0;

    for (let i = 0; i < 3; i++) {
        if (inputNumbers[i] == answerNumbers[i]) {
            strike ++;
        } else if (answerNumbers.includes(inputNumbers[i])) {
            ball ++;
        } 
    }

    // 2) 결과에 따라 html 업데이트
    let resultRow = "";

    // 아웃(0 스트라이크, 0 볼)인 경우 -> 빨간색 O 
    if (strike === 0 && ball === 0) {
        resultRow = `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; font-family: 'Jua', sans-serif; font-size: 22px;">
                <span style="flex: 1; text-align: left; letter-spacing: 8px;">${num1}${num2}${num3}</span>
                <span style="width: 30px; text-align: center;">:</span>
                <div style="flex: 1; display: flex; justify-content: flex-end;">
                    <span style="display: inline-flex; justify-content: center; align-items: center; width: 26px; height: 26px; border-radius: 50%; background-color: #ff1a1a; color: white; font-weight: bold; font-size: 15px;">O</span>
                </div>
            </div>
        `;
    } else {
        // 스트라이크나 볼이 있는 경우 -> 초록색 S, 노란색 B 
        resultRow = `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 20px; font-family: 'Jua', sans-serif; font-size: 22px;">
                <span style="flex: 1; text-align: left; letter-spacing: 8px;">${num1}${num2}${num3}</span>
                <span style="width: 30px; text-align: center;">:</span>
                <div style="flex: 1; display: flex; justify-content: flex-end; align-items: center; gap: 6px;">
                    <span>${strike}</span>
                    <span style="display: inline-flex; justify-content: center; align-items: center; width: 26px; height: 26px; border-radius: 50%; background-color: #008a3b; color: white; font-weight: bold; font-size: 15px;">S</span>
                    <span>${ball}</span>
                    <span style="display: inline-flex; justify-content: center; align-items: center; width: 26px; height: 26px; border-radius: 50%; background-color: #ffeb00; color: black; font-weight: bold; font-size: 15px;">B</span>
                </div>
            </div>
        `;
    }
    resultsDiv.innerHTML += resultRow;

    // 3) 게임이 끝났는지? (3스트라이크-승리 or 시도 횟수0-패배)
    // - 이미지는 id가 `game-result-img`  img 태그를 사용합니다.
    // - 버튼 비활성화
    if (strike === 3) {
        // 승리 케이스
        resultImg.src = "success.png";
        resultImg.style.display = "block"; // 이미지 태그 보이기
        submitBtn.disabled = true;         // 확인하기 버튼 비활성화
        alert("정답입니다!");
    } else if (currentAttempts === 0) {
        // 패배 케이스 (시도 횟수를 다 씀)
        resultImg.src = "fail.png";
        resultImg.style.display = "block"; // 이미지 태그 보이기
        submitBtn.disabled = true;         // 확인하기 버튼 비활성화
        alert(`틀렸습니다! 정답은 ${answerNumbers.join(' ')} 이었습니다.`);
    } else {
        // 게임이 아직 끝나지 않았다면 -> 창 비움
        trash()
    }
}

function trash(){
    input1.value = "";
    input2.value = "";
    input3.value = "";
}


window.onload = initGame;