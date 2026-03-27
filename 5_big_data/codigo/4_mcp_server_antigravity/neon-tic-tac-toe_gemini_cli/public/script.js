document.addEventListener('DOMContentLoaded', () => {
    const cells = document.querySelectorAll('.cell');
    const statusText = document.getElementById('status-text');
    const resetBtn = document.getElementById('reset-btn');

    // Fetch the current game state from the server
    async function fetchState() {
        try {
            const res = await fetch('/api/state');
            const state = await res.json();
            updateUI(state);
        } catch (err) {
            console.error('Error fetching state:', err);
        }
    }

    // Make a move on the server
    async function makeMove(index) {
        try {
            const res = await fetch('/api/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ position: parseInt(index) })
            });
            const data = await res.json();
            
            if (data.success) {
                updateUI(data.state);
            }
        } catch (err) {
            console.error('Error making move:', err);
        }
    }

    // Reset the game on the server
    async function resetGame() {
        try {
            const res = await fetch('/api/reset', { method: 'POST' });
            const state = await res.json();
            updateUI(state);
        } catch (err) {
            console.error('Error resetting game:', err);
        }
    }

    // Update DOM based on state
    function updateUI(state) {
        // Update board cells
        state.board.forEach((cellValue, index) => {
            const cell = cells[index];
            cell.textContent = cellValue;
            
            // Clear previous neon classes
            cell.className = 'cell'; 
            
            // Add new neon classes based on player
            if (cellValue === 'X') {
                cell.classList.add('player-x');
            } else if (cellValue === 'O') {
                cell.classList.add('player-o');
            }
        });

        // Clear previous status classes
        statusText.className = 'status-text'; 

        // Update status text based on game over or current turn
        if (state.gameOver) {
            if (state.winner === 'Draw') {
                statusText.textContent = "SYSTEM TIE";
                statusText.classList.add('game-over-draw');
            } else {
                statusText.textContent = `PLAYER ${state.winner} WINS`;
                statusText.classList.add(state.winner === 'X' ? 'game-over-x' : 'game-over-o');
            }
        } else {
            statusText.textContent = `PLAYER ${state.currentPlayer}'S TURN`;
            statusText.classList.add(state.currentPlayer === 'X' ? 'turn-x' : 'turn-o');
        }
    }

    // Attach click listeners to all board cells
    cells.forEach(cell => {
        cell.addEventListener('click', () => {
            const index = cell.getAttribute('data-index');
            makeMove(index);
        });
    });

    // Attach click listener to reset button
    resetBtn.addEventListener('click', resetGame);

    // Initial state fetch
    fetchState();
});
