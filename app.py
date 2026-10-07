import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Racing Attack Game",
    page_icon="🏎",
    layout="centered"
)

st.title("🏎️ Racing Attack")
st.caption("Game đua xe Racing Attack phong cách Retro!")

r"""
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
  .touch-controls {
    display: flex;
    justify-content: space-between;
    width: 360px;
    margin-top: 15px;
    gap: 10px;
  }
  .control-btn {
    flex: 1;
    background: #222;
    color: #fff;
    border: 2px solid #555;
    padding: 12px 0;
    font-size: 16px;
    font-weight: bold;
    border-radius: 8px;
    cursor: pointer;
    text-align: center;
    box-shadow: 0 4px 0 #000;
  }
  .control-btn:active {
    transform: translateY(2px);
    box-shadow: 0 2px 0 #000;
    background: #333;
  }
  .instruction {
    margin-top: 10px;
    font-size: 13px;
    color: #aaa;
    text-align: center;
  }
</style>
</head>
<body>

<div class="game-container">
  <canvas id="gameCanvas" width="360" height="480"></canvas>
</div>

<div class="touch-controls">
  <div class="control-btn" id="btnLeft">◄ Trái (A)</div>
  <div class="control-btn" id="btnOk">Bắt đầu / OK</div>
  <div class="control-btn" id="btnRight">Phải (D) ►</div>
</div>

<div class="instruction">
  Điều khiển: Phím <b>◄ / ►</b> hoặc <b>A / D</b> | <b>Enter / Space</b> để chơi lại
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const ROAD_LEFT = 60;
const ROAD_RIGHT = 300;
const ROAD_WIDTH = 240;
const LANES = [90, 150, 210, 270];

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

  ctx.fillStyle = '#2E7D32';
  for (let y = -40 + (roadOffset % 60); y < canvas.height; y += 60) {
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
  if (!lastObs || lastObs.y > 90) {
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

  if (Math.random() < 0.04) spawnObstacle();

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
      speed += 0.8;
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
    ctx.fillText('RACING ATTACK', canvas.width / 2, 200);
    
    ctx.fillStyle = '#FFF';
    ctx.font = '16px Arial';
    ctx.fillText('Nhấn OK hoặc Space để bắt đầu', canvas.width / 2, 250);
    return;
  }

  obstacles.forEach(obs => {
    drawCar(obs.x, obs.y, obs.color, false);
  });

  drawCar(LANES[player.lane], player.y, '#00E5FF', true);

  ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
  ctx.fillRect(0, 0, canvas.width, 40);

  ctx.fillStyle = '#FFD700';
  ctx.font = 'bold 16px Arial';
  ctx.textAlign = 'left';
  ctx.fillText(`Score: ${score}`, 15, 25);
  
  ctx.textAlign = 'right';
  ctx.fillText(`Lvl: ${level}`, canvas.width - 15, 25);

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
    ctx.fillText('Bấm OK / Space để chơi lại', canvas.width / 2, 275);
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
    gameStarted = true;
    gameOver = false;
    score = 0;
    level = 1;
    speed = 5;
    player.lane = 1;
    obstacles = [];
    playSound(880, 'sine', 0.15);
  }
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') moveLeft();
  if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') moveRight();
  if (e.key === 'Enter' || e.key === ' ') startGame();
});

document.getElementById('btnLeft').addEventListener('click', moveLeft);
document.getElementById('btnRight').addEventListener('click', moveRight);
document.getElementById('btnOk').addEventListener('click', startGame);

gameLoop();
</script>
</body>
</html>
"""
