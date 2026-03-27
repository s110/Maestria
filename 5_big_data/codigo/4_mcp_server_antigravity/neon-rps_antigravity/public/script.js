let playerScore = 0;
let computerScore = 0;
let roundNumber = 1;
const WINNING_SCORE = 3;

const emojiMap = {
    'rock': '✊',
    'paper': '✋',
    'scissors': '✌️'
};

const choicesBtn = document.querySelectorAll('.choice-btn');
const playerDisplay = document.getElementById('player-display');
const computerDisplay = document.getElementById('computer-display');
const statusMessage = document.getElementById('status-message');
const playerScoreEl = document.getElementById('player-score');
const computerScoreEl = document.getElementById('computer-score');
const roundNumberEl = document.getElementById('round-number');
const gameOverBanner = document.getElementById('game-over-banner');
const gameOverText = document.getElementById('game-over-text');
const controls = document.getElementById('controls');

choicesBtn.forEach(btn => {
    btn.addEventListener('click', () => playRound(btn.dataset.choice));
});

async function playRound(playerChoice) {
    if (playerScore >= WINNING_SCORE || computerScore >= WINNING_SCORE) return;

    // Reset displays
    playerDisplay.classList.remove('winner-pulse');
    computerDisplay.classList.remove('winner-pulse');
    playerDisplay.style.borderColor = 'var(--neon-cyan)';
    computerDisplay.style.borderColor = 'var(--neon-magenta)';
    
    // Animate thinking
    statusMessage.textContent = "COMPUTER IS THINKING...";
    statusMessage.className = "status-message neon-yellow";
    playerDisplay.textContent = emojiMap[playerChoice];
    computerDisplay.textContent = '...';
    
    // Disable buttons
    choicesBtn.forEach(btn => btn.disabled = true);
    controls.style.opacity = '0.5';

    try {
        const response = await fetch('/api/play', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ playerChoice })
        });
        
        const data = await response.json();
        
        // Simulate a slight delay for dramatic effect
        setTimeout(() => {
            handleRoundResult(playerChoice, data.computerChoice, data.result);
        }, 800);

    } catch (error) {
        console.error('Error:', error);
        statusMessage.textContent = "ERROR CONNECTING TO SERVER";
        statusMessage.className = "status-message neon-magenta";
        choicesBtn.forEach(btn => btn.disabled = false);
        controls.style.opacity = '1';
    }
}

function handleRoundResult(playerChoice, computerChoice, result) {
    computerDisplay.textContent = emojiMap[computerChoice];
    
    if (result === 'win') {
        playerScore++;
        statusMessage.textContent = `YOU WON ROUND ${roundNumber}!`;
        statusMessage.className = "status-message neon-cyan";
        playerDisplay.classList.add('winner-pulse');
        playerDisplay.style.borderColor = '#fff';
    } else if (result === 'lose') {
        computerScore++;
        statusMessage.textContent = `COMPUTER WON ROUND ${roundNumber}!`;
        statusMessage.className = "status-message neon-magenta";
        computerDisplay.classList.add('winner-pulse');
        computerDisplay.style.borderColor = '#fff';
    } else {
        statusMessage.textContent = `ROUND ${roundNumber} IS A TIE!`;
        statusMessage.className = "status-message neon-yellow";
    }

    playerScoreEl.textContent = playerScore;
    computerScoreEl.textContent = computerScore;
    roundNumber++;
    roundNumberEl.textContent = roundNumber;

    if (playerScore >= WINNING_SCORE || computerScore >= WINNING_SCORE) {
        setTimeout(endGame, 1000);
    } else {
        setTimeout(() => {
            statusMessage.textContent = "AWAITING YOUR MOVE...";
            statusMessage.className = "status-message";
            choicesBtn.forEach(btn => btn.disabled = false);
            controls.style.opacity = '1';
        }, 1500);
    }
}

function endGame() {
    gameOverBanner.classList.remove('hidden');
    
    if (playerScore >= WINNING_SCORE) {
        gameOverText.textContent = "YOU WIN!";
        gameOverText.style.color = "var(--neon-cyan)";
        gameOverText.style.textShadow = "0 0 20px var(--neon-cyan), 0 0 40px var(--neon-cyan-dark)";
    } else {
        gameOverText.textContent = "SYSTEM DEFEAT";
        gameOverText.style.color = "var(--neon-magenta)";
        gameOverText.style.textShadow = "0 0 20px var(--neon-magenta), 0 0 40px var(--neon-magenta-dark)";
    }
}

function resetGame() {
    playerScore = 0;
    computerScore = 0;
    roundNumber = 1;
    
    playerScoreEl.textContent = playerScore;
    computerScoreEl.textContent = computerScore;
    roundNumberEl.textContent = roundNumber;
    
    playerDisplay.textContent = '?';
    computerDisplay.textContent = '?';
    playerDisplay.classList.remove('winner-pulse');
    computerDisplay.classList.remove('winner-pulse');
    playerDisplay.style.borderColor = 'var(--neon-cyan)';
    computerDisplay.style.borderColor = 'var(--neon-magenta)';
    
    statusMessage.textContent = "AWAITING YOUR MOVE...";
    statusMessage.className = "status-message";
    
    gameOverBanner.classList.add('hidden');
    choicesBtn.forEach(btn => btn.disabled = false);
    controls.style.opacity = '1';
}
