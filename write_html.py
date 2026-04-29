import os

content = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NEXUS ARCADE</title>
<style>
:root { --bg: #0d0015; --surf: #1a0025; --pink: #ff2d55; --cyan: #00f0ff; --text: #eee; --dim: #666; --bord: #2a2a3a; }
[data-theme="light"] { --bg: #f5f5f5; --surf: #eaeaea; --text: #111; --dim: #888; --bord: #ccc; }
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: var(--bg); color: var(--text); font-family: sans-serif; }
header { position: sticky; top: 0; z-index: 1000; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; background: var(--bg); border-bottom: 2px solid var(--bord); }
.logo { font-family: 'Bebas Neue', sans-serif; font-size: 2rem; color: var(--pink); letter-spacing: 3px; }
.logo span { color: var(--cyan); }
.hero { padding: 4rem 2rem 2rem; max-width: 1400px; margin: 0 auto; }
.hero h1 { font-family: 'Bebas Neue', sans-serif; font-size: clamp(3rem, 8vw, 6.5rem); text-transform: uppercase; line-height: 0.95; }
.hero .l2 { color: var(--pink); }
.hero .l3 { color: var(--cyan); }
.games-section { padding: 2rem; max-width: 1400px; margin: 0 auto; }
.games-layout { display: grid; grid-template-columns: repeat(12, 1fr); gap: 1.5rem; }
.game-piece { background: var(--surf); border: 1px solid var(--bord); padding: 1.5rem; }
.game-piece--featured { grid-column: span 8; }
.game-piece--small { grid-column: span 4; }
.game-meta { display: flex; flex-direction: column; gap: 0.75rem; }
.game-tag { font-size: 0.7rem; letter-spacing: 3px; text-transform: uppercase; color: var(--cyan); border: 1px solid var(--cyan); padding: 0.3rem 0.8rem; width: fit-content; }
</style>
</head>
<body>
<header>
    <div class="logo">NEXUS<span>.</span>ARCADE</div>
    <div><button onclick="toggleTheme()" id="themeBtn">&#127769;</button></div>
</header>
<main>
    <section class="hero">
        <h1>
            <div>Play</div>
            <div class="l2">Dirty.</div>
            <div class="l3">Retro.</div>
        </h1>
        <p>Authentic arcade experiences reimagined.</p>
        <button onclick="scrollToGames()">Enter Arena</button>
    </section>
    <section class="games-section" id="games">
        <div class="games-layout">
            <div class="game-piece game-piece--featured" data-type="action">
                <div>&#129603;</div>
                <div class="game-meta">
                    <span class="game-tag">Action • Survival</span>
                    <h3>Chase Master Elite</h3>
                    <p>Escape tactical enemies with vision mechanics.</p>
                    <button onclick="launchGame('chasing')">Enter Arena</button>
                </div>
            </div>
            <div class="game-piece game-piece--small" data-type="puzzle">
                <div>&#129568;</div>
                <div class="game-meta">
                    <span class="game-tag">Puzzle • Speed</span>
                    <h3>Memory Matrix</h3>
                    <p>Neuro-visual challenge. Match tiles.</p>
                    <button onclick="launchGame('memory')">Play Now</button>
                </div>
            </div>
        </div>
    </section>
</main>

<div id="gameView" style="display:none; position:fixed; inset:0; background:var(--bg); z-index:9998; flex-direction:column;">
    <div style="display:flex; justify-content:space-between; padding:1rem 2rem; border-bottom:2px solid var(--bord);">
        <div id="gameViewTitle">GAME</div>
        <button onclick="closeGame()">Back</button>
    </div>
    <div id="chaseGame" style="flex:1; position:relative; display:none;">
        <div id="startScreen" style="position:absolute; inset:0; background:rgba(13,0,21,0.95); display:flex; flex-direction:column; align-items:center; justify-content:center; gap:1rem; z-index:10;">
            <h2>CHASE MASTER</h2>
            <p>Move: WASD | Sprint: SHIFT | Hide: Trees</p>
            <button onclick="startGame()">Start</button>
        </div>
        <canvas id="gameCanvas" style="width:100%; height:100%; display:block;"></canvas>
    </div>
    <div id="memoryGame" style="display:none; flex:1; padding:1rem; overflow-y:auto;">
        <div id="memoryGrid" style="display:grid; grid-template-columns:repeat(4,1fr); gap:10px; max-width:800px; margin:0 auto;"></div>
    </div>
</div>

<script>
// Theme
function toggleTheme() {
    const h = document.documentElement;
    const b = document.getElementById('themeBtn');
    if (h.getAttribute('data-theme') === 'dark') {
        h.setAttribute('data-theme', 'light');
        b.innerHTML = '&#9728;&#65039;';
    } else {
        h.setAttribute('data-theme', 'dark');
        b.innerHTML = '&#127769;';
    }
}

// Games
let gameActive = false, animId, currentGame = null, memTimer = null;

function launchGame(type) {
    const v = document.getElementById('gameView');
    const t = document.getElementById('gameViewTitle');
    t.textContent = type === 'chasing' ? 'CHASE MASTER' : 'MEMORY MATRIX';
    v.style.display = 'flex';
    currentGame = type;
    document.getElementById('chaseGame').style.display = type === 'chasing' ? 'flex' : 'none';
    document.getElementById('memoryGame').style.display = type === 'memory' ? 'block' : 'none';
    if (type === 'chasing') initChase();
    if (type === 'memory') initMemory();
}

function closeGame() {
    gameActive = false;
    cancelAnimationFrame(animId);
    clearInterval(memTimer);
    document.getElementById('gameView').style.display = 'none';
}

// Chase Master
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
let player, enemies, coins, score;

function initChase() {
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
    score = 0;
    player = { x: canvas.width/2, y: canvas.height/2, size: 14, speed: 3.5 };
    enemies = []; coins = [];
    [{s:2.2,sz:14,c:'#ef4444',vr:250},{s:1.8,sz:12,c:'#ff6b35',vr:200},{s:1.5,sz:13,c:'#f59e0b',vr:180},{s:2.5,sz:15,c:'#dc2626',vr:280}].forEach(cfg => {
        let x, y;
        do { x = Math.random()*(canvas.width-100)+50; y = Math.random()*(canvas.height-100)+50; } while(Math.hypot(x-player.x, y-player.y) < 150);
        enemies.push({x,y,size:cfg.sz,speed:cfg.s,color:cfg.c,angle:Math.random()*Math.PI*2,state:'patrol',visionRange:cfg.vr,lastX:null,lastY:null,timer:0});
    });
    for(let i=0;i<8;i++) coins.push({x:Math.random()*(canvas.width-30)+15,y:Math.random()*(canvas.height-30)+15,size:7});
}

const keys = {};
window.addEventListener('keydown', e => keys[e.code]=true);
window.addEventListener('keyup', e => keys[e.code]=false);

function updateChase() {
    if (!gameActive) return;
    let mx=0, my=0;
    if(keys['KeyW']||keys['ArrowUp']) my=-1;
    if(keys['KeyS']||keys['ArrowDown']) my=1;
    if(keys['KeyA']||keys['ArrowLeft']) mx=-1;
    if(keys['KeyD']||keys['ArrowRight']) mx=1;
    if(mx&&my){mx*=0.707;my*=0.707;}
    const sp = (keys['ShiftLeft']||keys['ShiftRight'])&&stamina>0 ? player.speed*1.8 : player.speed;
    player.x += mx*sp; player.y += my*sp;
    player.x = Math.max(player.size, Math.min(canvas.width-player.size, player.x));
    player.y = Math.max(player.size, Math.min(canvas.height-player.size, player.y));
    enemies.forEach(en => {
        const dx=player.x-en.x, dy=player.y-en.y, dist=Math.hypot(dx,dy);
        let see=false;
        if(dist < en.visionRange) {
            let ad = Math.atan2(dy,dx) - en.angle;
            while(ad<-Math.PI) ad+=Math.PI*2; while(ad>Math.PI) ad-=Math.PI*2;
            if(Math.abs(ad)<Math.PI/6) see=true;
        }
        if(see) { en.state='chase'; en.lastX=player.x; en.lastY=player.y; en.timer=180; en.angle=Math.atan2(dy,dx); en.x+=Math.cos(en.angle)*en.speed; en.y+=Math.sin(en.angle)*en.speed; }
        else if(en.state==='chase') { en.timer--; if(en.timer<=0) en.state='search'; else if(en.lastX!==null){ const sd=Math.hypot(en.lastX-en.x,en.lastY-en.y); if(sd>5) { en.angle=Math.atan2(en.lastY-en.y,en.lastX-en.x); en.x+=Math.cos(en.angle)*en.speed*0.8; en.y+=Math.sin(en.angle)*en.speed*0.8; } else en.state='search'; } }
        else if(en.state==='search') { en.x+=Math.cos(en.angle)*en.speed*0.5; en.y+=Math.sin(en.angle)*en.speed*0.5; }
        else { en.x+=Math.cos(en.angle)*en.speed*0.7; en.y+=Math.sin(en.angle)*en.speed*0.7; }
        if(en.x<en.size||en.x>canvas.width-en.size) en.angle=Math.PI-en.angle;
        if(en.y<en.size||en.y>canvas.height-en.size) en.angle=-en.angle;
        if(dist < player.size+en.size) { gameActive=false; alert('GAME OVER\\nScore: '+score); closeGame(); document.getElementById('startScreen').style.display='flex'; }
    });
    coins.forEach((c,i) => { if(Math.hypot(player.x-c.x,player.y-c.y)<player.size+c.size) { coins.splice(i,1); score+=150; coins.push({x:Math.random()*(canvas.width-30)+15,y:Math.random()*(canvas.height-30)+15,size:7}); } });
    drawChase();
    animId = requestAnimationFrame(updateChase);
}

function drawChase() {
    ctx.fillStyle='#0d0015'; ctx.fillRect(0,0,canvas.width,canvas.height);
    coins.forEach(c => { ctx.fillStyle='#fbbf24'; ctx.beginPath(); ctx.arc(c.x,c.y,c.size,0,Math.PI*2); ctx.fill(); });
    enemies.forEach(en => { ctx.fillStyle=en.state==='chase'?en.color:en.color+'88'; ctx.beginPath(); ctx.arc(en.x,en.y,en.size,0,Math.PI*2); ctx.fill(); });
    ctx.fillStyle='#6366f1'; ctx.beginPath(); ctx.arc(player.x,player.y,player.size,0,Math.PI*2); ctx.fill();
}

function startGame() { document.getElementById('startScreen').style.display='none'; gameActive=true; updateChase(); }

// Memory Matrix
let mCards=[], mFlip=[], mMatch=[], mMoves=0, mScore=0, mSecs=0, mDiff='easy';

function initMemory() {
    clearInterval(memTimer);
    mCards=[]; mFlip=[]; mMatch=[]; mMoves=0; mScore=0; mSecs=0;
    const grid = document.getElementById('memoryGrid');
    grid.innerHTML = '';
    const pairs = {easy:8,medium:12,hard:16}[mDiff];
    const emojis = ['🍕','🎮','🚀','🎨','🎭','🎸','🌟','⚽','🎪','🦄','🐢','🎯','🎲','🌈','🎊','💎','👑','🏆','🎁','🌺','🌸','🐝','🦋'];
    const sel = emojis.slice(0, pairs);
    mCards = [...sel, ...sel].sort(() => Math.random()-0.5).map((e,i) => ({id:i,emoji:e,flipped:false,matched:false}));
    mCards.forEach(card => {
        const el = document.createElement('div');
        el.style.cssText = 'aspect-ratio:1;background:var(--surf);border:2px solid var(--bord);cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:2rem;';
        el.addEventListener('click', () => flipCard(card, el));
        if(card.flipped||card.matched) el.textContent = card.emoji;
        else { el.style.background='linear-gradient(135deg,var(--pink),var(--cyan))'; el.textContent='?'; }
        grid.appendChild(el);
    });
}

function flipCard(card,el) {
    if(card.flipped||card.matched||mFlip.length>=2) return;
    if(mFlip.length===0) { memTimer=setInterval(()=>{mSecs++; document.getElementById('memTime').textContent=Math.floor(mSecs/60)+':'+(mSecs%60).toString().padStart(2,'0'); },1000); }
    card.flipped=true; el.textContent=card.emoji; mFlip.push({card,el});
    if(mFlip.length===2) {
        mMoves++;
        const [a,b]=mFlip;
        if(a.card.emoji===b.card.emoji) { a.card.matched=b.card.matched=true; mScore+=Math.max(100-mMoves*2,10); if(mMatch.length===mCards.length) setTimeout(()=>alert('You Won!\\nScore: '+mScore),500); }
        else { setTimeout(()=>{a.card.flipped=b.card.flipped=false;a.el.textContent='?';b.el.textContent='?';},800); }
        mFlip=[];
    }
}

function scrollToGames() { document.getElementById('games').scrollIntoView({behavior:'smooth'}); }
</script>
</body>
</html>"""

with open(r'C:\Users\karth\OneDrive\Desktop\Ai\index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('File written successfully')
