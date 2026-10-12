import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Racing Attack Game",
    page_icon="🏎",
    layout="centered"
)

st.title("🏎️ Racing Attack")
st.caption("Game đua xe Racing Attack phong cách Retro - Điều khiển hoàn toàn bằng bàn phím!")

game_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
  body {
    background: #111;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    font-family: 'Arial', sans-serif;
    color: #fff;
    padding: 10px;
  }
  .game-container {
    position: relative;
    box-shadow: 0 10px 30px rgba(0,0,0,0.8);
    border-radius: 8px;
    overflow: hidden;
    border: 3px solid #444;
  }
  #gameCanvas {
    display: block;
    background: #000;
    image-rendering: pixelated;
  }
  .difficulty-selector {
    display: flex;
    justify-content: center;
    gap: 10px;
    width: 360px;
    margin-top: 10px;
    margin-bottom: 5px;
  }
  .diff-btn {
    flex: 1;
    background: #333;
    color: #aaa;
    border: 2px solid #555;
    padding: 8px 0;
    font-size: 14px;
    font-weight: bold;
    border-radius: 6px;
    cursor: pointer;
    text-align: center;
    transition: all 0.2s;
  }
  .diff-btn.active {
    background: #FFD700;
    color: #000;
    border-color: #FFA500;
    box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
  }
  .instruction {
    margin-top: 12px;
    font-size: 13px;
    color: #aaa;
    text-align: center;
    background: #1a1a1a;
    padding: 10px 15px;
    border-radius: 6px;
    border: 1px solid #333;
    width: 360px;
  }
</style>
</head>
<body>

<div class="difficulty-selector">
  <div class="diff-btn" id="diffEasy" onclick="setDifficulty('easy')">🟢 Dễ</div>
  <div class="diff-btn active" id="diffMedium" onclick="setDifficulty('medium')">🟡 Vừa</div>
  <div class="diff-btn" id="diffHard" onclick="setDifficulty('hard')">🔴 Khó</div>
</div>

<div class="game-container">
  <canvas id="gameCanvas" width="360" height="480"></canvas>
</div>

<div class="instruction">
  🎮 <b>Cách chơi:</b> Dùng phím <b>◄ / ►</b> hoặc <b>A / D</b> để lái xe.<br>
  Nhấn phím <b>Space</b> hoặc <b>Enter</b> để Bắt đầu / Chơi lại.
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const ROAD_LEFT = 60;
const ROAD_RIGHT = 300;
const ROAD_WIDTH = 240;
const LANES = [90, 150, 210, 270];

// Tăng tần số xuất hiện xe cản trở (spawnRate) để đường đua đông đúc hơn, không bị trống trải
const DIFFICULTY_SETTINGS = {
  easy: { name: 'Dễ', initialSpeed: 3.5, speedInc: 0.4, spawnRate: 0.045 },
  medium: { name: 'Vừa', initialSpeed: 5.0, speedInc: 0.8, spawnRate: 0.065 },
  hard: { name: 'Khó', initialSpeed: 7.0, speedInc: 1.2, spawnRate: 0.090 }
};

let currentDiffKey = 'medium';

function setDifficulty(key) {
  currentDiffKey = key;
  document.querySelectorAll('.diff-btn').forEach(btn => btn.classList.remove('active'));
  if (key === 'easy') document.getElementById('diffEasy').classList.add('active');
  if (key === 'medium') document.getElementById('diffMedium').classList.add('active');
  if (key === 'hard') document.getElementById('diffHard').classList.add('active');
}

let player = { lane: 1, y: 390, width: 32, height: 50 };
let obstacles = [];
let score = 0;
let level = 1;
let speed = 5;
let gameOver = false;
let gameStarted = false;

const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
function playSound(freq, type, duration) {
  if (audioCtx.state === 'suspended') audioCtx.resume();
  try {
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = type;
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + duration);
  } catch(e){}
}

function drawCar(x, y, bodyColor, isPlayer=false) {
  ctx.fillStyle = '#111';
  ctx.fillRect(x - 17, y + 6, 4, 12);
  ctx.fillRect(x + 13, y + 6, 4, 12);
  ctx.fillRect(x - 17, y + 32, 4, 12);
  ctx.fillRect(x + 13, y + 32, 4, 12);

  ctx.fillStyle = bodyColor;
  ctx.fillRect(x - 13, y, 26, 48);

  if (isPlayer) {
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(x - 2, y, 4, 48);
  }

  ctx.fillStyle = '#111';
  ctx.fillRect(x - 10, y + 10, 20, 10);
  ctx.fillRect(x - 9, y + 32, 18, 6);

  if (isPlayer) {
    ctx.fillStyle = '#ffea00';
    ctx.fillRect(x - 11, y + 1, 5, 3);
    ctx.fillRect(x + 6, y + 1, 5, 3);
  } else {
    ctx.fillStyle = '#ff2222';
    ctx.fillRect(x - 11, y + 44, 5, 3);
    ctx.fillRect(x + 6, y + 44, 5, 3);
  }
}

let roadOffset = 0;
function drawEnvironment() {
  ctx.fillStyle = '#4CAF50';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Giảm số lượng cây 2 bên đường (khoảng cách 120 pixel)
  ctx.fillStyle = '#2E7D32';
  for (let y = -80 + (roadOffset % 120); y < canvas.height; y += 120) {
    ctx.beginPath();
    ctx.arc(30, y, 14, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(330, y, 14, 0, Math.PI * 2);
    ctx.fill();
  }

  ctx.fillStyle = '#E0E0E0';
  ctx.fillRect(ROAD_LEFT - 10, 0, 10, canvas.height);
  ctx.fillRect(ROAD_RIGHT, 0, 10, canvas.height);

  ctx.fillStyle = '#555555';
  ctx.fillRect(ROAD_LEFT, 0, ROAD_WIDTH, canvas.height);

  ctx.fillStyle = '#FFFFFF';
  roadOffset = (roadOffset + speed) % 30;
  for (let y = -30 + roadOffset; y < canvas.height; y += 30) {
    ctx.fillRect(LANES[0] + 30 - 2, y, 4, 15);
    ctx.fillRect(LANES[1] + 30 - 2, y, 4, 15);
    ctx.fillRect(LANES[2] + 30 - 2, y, 4, 15);
  }
}

const CAR_COLORS = ['#E53935', '#1E88E5', '#FB8C00', '#8E24AA', '#43A047'];

function spawnObstacle() {
  const laneIndex = Math.floor(Math.random() * LANES.length);
  const lastObs = obstacles[obstacles.length - 1];
  // Rút ngắn khoảng cách tối thiểu giữa các xe để tránh tạo khoảng trống quá xa
  if (!lastObs || lastObs.y > 65) {
    const randomColor = CAR_COLORS[Math.floor(Math.random() * CAR_COLORS.length)];
    obstacles.push({
      lane: laneIndex,
      x: LANES[laneIndex],
      y: -50,
      color: randomColor
    });
  }
}

function update() {
  if (!gameStarted || gameOver) return;

  const currentSettings = DIFFICULTY_SETTINGS[currentDiffKey];
  if (Math.random() < currentSettings.spawnRate) spawnObstacle();

  for (let i = 0; i < obstacles.length; i++) {
    obstacles[i].y += speed;

    let obs = obstacles[i];
    if (Math.abs(LANES[player.lane] - obs.x) < 22 && Math.abs(player.y - obs.y) < 42) {
      gameOver = true;
      playSound(120, 'sawtooth', 0.5);
    }
  }

  if (obstacles.length > 0 && obstacles[0].y > canvas.height + 50) {
    obstacles.shift();
    score += 10;
    playSound(587, 'sine', 0.08);
    if (score % 100 === 0) {
      level++;
      speed += currentSettings.speedInc;
    }
  }
}

function draw() {
  drawEnvironment();

  if (!gameStarted) {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = '#FFD700';
    ctx.font = 'bold 26px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('RACING ATTACK', canvas.width / 2, 180);
    
    ctx.fillStyle = '#4CAF50';
    ctx.font = 'bold 16px Arial';
    ctx.fillText(`Mức độ: ${DIFFICULTY_SETTINGS[currentDiffKey].name.toUpperCase()}`, canvas.width / 2, 220);

    ctx.fillStyle = '#FFF';
    ctx.font = '15px Arial';
    ctx.fillText('Nhấn Space để bắt đầu', canvas.width / 2, 260);
    return;
  }

  obstacles.forEach(obs => {
    drawCar(obs.x, obs.y, obs.color, false);
  });

  drawCar(LANES[player.lane], player.y, '#00E5FF', true);

  ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
  ctx.fillRect(0, 0, canvas.width, 40);

  ctx.fillStyle = '#FFD700';
  ctx.font = 'bold 15px Arial';
  ctx.textAlign = 'left';
  ctx.fillText(`Score: ${score}`, 12, 25);
  
  ctx.fillStyle = '#00E5FF';
  ctx.textAlign = 'center';
  ctx.fillText(`[${DIFFICULTY_SETTINGS[currentDiffKey].name}]`, canvas.width / 2, 25);

  ctx.fillStyle = '#FFD700';
  ctx.textAlign = 'right';
  ctx.fillText(`Lvl: ${level}`, canvas.width - 12, 25);

  if (gameOver) {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
    ctx.fillRect(30, 160, 300, 140);

    ctx.fillStyle = '#FF3333';
    ctx.font = 'bold 28px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('GAME OVER', canvas.width / 2, 210);

    ctx.fillStyle = '#FFF';
    ctx.font = '15px Arial';
    ctx.fillText(`Điểm của bạn: ${score}`, canvas.width / 2, 245);
    ctx.fillText('Bấm Space để chơi lại', canvas.width / 2, 275);
  }
}

function gameLoop() {
  update();
  draw();
  requestAnimationFrame(gameLoop);
}

function moveLeft() {
  if (player.lane > 0) {
    player.lane--;
    playSound(400, 'square', 0.04);
  }
}

function moveRight() {
  if (player.lane < LANES.length - 1) {
    player.lane++;
    playSound(400, 'square', 0.04);
  }
}

function startGame() {
  if (!gameStarted || gameOver) {
    const currentSettings = DIFFICULTY_SETTINGS[currentDiffKey];
    gameStarted = true;
    gameOver = false;
    score = 0;
    level = 1;
    speed = currentSettings.initialSpeed;
    player.lane = 1;
    obstacles = [];
    playSound(880, 'sine', 0.15);
  }
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') {
    moveLeft();
  } else if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') {
    moveRight();
  } else if (e.key === 'Enter' || e.key === ' ' || e.code === 'Space') {
    e.preventDefault();
    startGame();
  }
});

gameLoop();
</script>
</body>
</html>
"""

components.html(game_code, height=640)
