import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 8080;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const WINNING_COMBOS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], // Rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8], // Columns
    [0, 4, 8], [2, 4, 6]             // Diagonals
];

function checkWinner(board) {
    for (let combo of WINNING_COMBOS) {
        const [a, b, c] = combo;
        if (board[a] && board[a] === board[b] && board[a] === board[c]) {
            return board[a];
        }
    }
    if (!board.includes(null)) {
        return 'Draw';
    }
    return null;
}

// In-memory game state
let gameState = {
    board: Array(9).fill(null),
    currentPlayer: 'X',
    winner: null,
    gameOver: false
};

app.get('/api/state', (req, res) => {
    res.json(gameState);
});

app.post('/api/move', (req, res) => {
    const { position } = req.body;

    // Validate move
    if (gameState.gameOver || gameState.board[position] !== null || position < 0 || position > 8) {
        return res.json({ success: false, state: gameState });
    }

    // Apply move
    gameState.board[position] = gameState.currentPlayer;
    
    // Check win/draw
    const winner = checkWinner(gameState.board);
    if (winner) {
        gameState.winner = winner;
        gameState.gameOver = true;
    } else {
        // Switch turn
        gameState.currentPlayer = gameState.currentPlayer === 'X' ? 'O' : 'X';
    }

    res.json({ success: true, state: gameState });
});

app.post('/api/reset', (req, res) => {
    gameState = {
        board: Array(9).fill(null),
        currentPlayer: 'X',
        winner: null,
        gameOver: false
    };
    res.json(gameState);
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
