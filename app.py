import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Racing Attack Game",
    page_icon="🏎",
    layout="centered"
)

st.title("🏎️ Racing Attack")
st.caption("Game đua xe Racing Attack phong cách Retro - Hỗ trợ cả Bàn phím và Cảm ứng Điện thoại!")

game_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; -webkit-user-select: none; }
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
  /* Nút bấm cảm ứng dành riêng cho điện thoại */
  .touch-controls {
    display: flex;
    justify-content: space-between;
    width: 360px;
    margin-top: 10px;
    gap: 10px;
  }
  .control-btn {
    flex: 1;
    background: #222;
    color: #fff;
    border: 2px solid #555;
    padding: 14px 0;
    font-size: 16px;
    font-weight: bold;
    border-radius: 8px;
    cursor: pointer;
    text-align: center;
    box-shadow: 0 4px 0 #000;
    -webkit-tap-highlight-color: transparent;
  }
  .control-btn:active {
    transform: translateY(2px);
    box-shadow: 0 2px 0 #000;
    background: #444;
  }
  .instruction {
    margin-top: 10px;
    font-size: 12px;
    color: #aaa;
    text-align: center;
    background: #1a1a1a;
    padding: 8px 12px;
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

<!-- Nút điều khiển cảm ứng cho điện thoại -->
<div class="touch-controls">
  <div class="control-btn" id="btnLeft">◄ Trái (A)</div>
  <div class="control-btn" id="btnStart" style="background: #1b5e20;">Bắt đầu / OK</div>
  <div class="control-btn" id="btnRight">Phải (D) ►</div>
</div>

<div class="instruction">
  🎮 PC: Phím <b>◄ / ►</b> hoặc <b>A / D</b> | <b>Space</b> Bắt đầu<br>
  📱 Điện thoại: Chạm trực tiếp vào các nút phía trên
</div>

<script>
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const ROAD_LEFT = 60;
const ROAD_RIGHT = 300;
const ROAD_WIDTH = 240;
const LANES = [90, 150, 210, 270];

const DIFFICULTY_SETTINGS = {
  easy: { name: 'Dễ', initialSpeed: 4, speedInc: 0.5, spawnRate: 0.045 },
  medium: { name: 'Vừa', initialSpeed: 6, speedInc: 1.0, spawnRate: 0.065 },
  hard: { name: 'Khó', initialSpeed: 8, speedInc: 1.5, spawnRate: 0.090 }
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
let speed = 6;
let gameOver = false;
let gameStarted = false;

// Khởi tạo AudioContext
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
let bgmInterval = null;

function playSound(freq, type, duration) {
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
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

// Nhạc nền game đua xe cực kỳ sôi động, dồn dập (Fast Arcade Chiptune)
const upbeatMelody = [
  330, 392, 440, 523, 587, 523, 440, 392,
  349, 440, 494, 587, 659, 587, 494, 440,
  293, 370, 440, 494, 587, 494, 440, 370,
  330, 392, 440, 494, 523, 494, 440, 392
];
let noteIndex = 0;

function startBGM() {
  stopBGM(); 
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }

  bgmInterval = setInterval(() => {
    if (!gameStarted || gameOver) return;
    try {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      
      osc.type = 'square'; 
      osc.frequency.value = upbeatMelody[noteIndex];
      
      gain.gain.setValueAtTime(0.025, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.12);
      
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.12);

      noteIndex = (noteIndex + 1) % upbeatMelody.length;
    } catch(e){}
  }, 140);
}

function stopBGM() {
  if (bgmInterval) {
    clearInterval(bgmInterval);
    bgmInterval = null;
  }
}

function drawCar(x, y, bodyColor, isPlayer=false) {
  const rx = Math.round(x);
  const ry = Math.round(y);

  ctx.fillStyle = '#111';
  ctx.fillRect(rx - 17, ry + 6, 4, 12);
  ctx.fillRect(rx + 13, ry + 6, 4, 12);
  ctx.fillRect(rx - 17, ry + 32, 4, 12);
  ctx.fillRect(rx + 13, ry + 32, 4, 12);

  ctx.fillStyle = bodyColor;
  ctx.fillRect(rx - 13, ry, 26, 48);

  if (isPlayer) {
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(rx - 2, ry, 4, 48);
  }

  ctx.fillStyle = '#111';
  ctx.fillRect(rx - 10, ry + 10, 20, 10);
  ctx.fillRect(rx - 9, ry + 32, 18, 6);

  if (isPlayer) {
    ctx.fillStyle = '#ffea00';
    ctx.fillRect(rx - 11, ry + 1, 5, 3);
    ctx.fillRect(rx + 6, ry + 1, 5, 3);
  } else {
    ctx.fillStyle = '#ff2222';
    ctx.fillRect(rx - 11, ry + 44, 5, 3);
    ctx.fillRect(rx + 6, ry + 44, 5, 3);
  }
}

let roadOffset = 0;
function drawEnvironment() {
  ctx.fillStyle = '#4CAF50';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  roadOffset = (roadOffset + speed) % 120;
  let treeOffset = Math.round(roadOffset);

  // Giảm bớt số cây 2 bên đường (khoảng cách 120px) cho đỡ rối mắt
  ctx.fillStyle = '#2E7D32';
  for (let y = -80 + treeOffset; y < canvas.height; y += 120) {
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

  let lineOffset = Math.round(roadOffset % 30);
  ctx.fillStyle = '#FFFFFF';
  for (let y = -30 + lineOffset; y < canvas.height; y += 30) {
    ctx.fillRect(LANES[0] + 30 - 2, y, 4, 15);
    ctx.fillRect(LANES[1] + 30 - 2, y, 4, 15);
    ctx.fillRect(LANES[2] + 30 - 2, y, 4, 15);
  }
}

const CAR_COLORS = ['#E53935', '#1E88E5', '#FB8C00', '#8E24AA', '#43A047'];

function spawnObstacle() {
  const laneIndex = Math.floor(Math.random() * LANES.length);
  const lastObs = obstacles[obstacles.length - 1];
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
      stopBGM();
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
    ctx.fillText('Bấm Space hoặc nút Bắt đầu', canvas.width / 2, 260);
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
    ctx.fillText('Bấm Space / Nút OK để chơi lại', canvas.width / 2, 275);
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
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }

  const currentSettings = DIFFICULTY_SETTINGS[currentDiffKey];
  gameStarted = true;
  gameOver = false;
  score = 0;
  level = 1;
  speed = currentSettings.initialSpeed;
  player.lane = 1;
  obstacles = [];
  
  playSound(880, 'sine', 0.15);
  startBGM();
}

// Bắt sự kiện bàn phím PC
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

// Bắt sự kiện bấm nút cảm ứng trên điện thoại
document.getElementById('btnLeft').addEventListener('click', moveLeft);
document.getElementById('btnRight').addEventListener('click', moveRight);
document.getElementById('btnStart').addEventListener('click', startGame);

// Hỗ trợ cảm ứng nhạy hơn trên màn hình di động (tránh độ trễ click)
document.getElementById('btnLeft').addEventListener('touchstart', (e) => { e.preventDefault(); moveLeft(); });
document.getElementById('btnRight').addEventListener('touchstart', (e) => { e.preventDefault(); moveRight(); });
document.getElementById('btnStart').addEventListener('touchstart', (e) => { e.preventDefault(); startGame(); });

gameLoop();
</script>
</body>
</html>
"""

components.html(game_code, height=720)
