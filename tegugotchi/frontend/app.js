const API_URL = ''; // Один домен, используем относительные пути
let currentPetId = null;
let lastHp = null;

// Элементы окон
const creationWindow = document.getElementById('creation-window');
const gameWindow = document.getElementById('game-window');
const deathWindow = document.getElementById('death-window');
const petAvatar = document.getElementById('pet-avatar');
const tamagotchiCase = document.getElementById('case');

// Функция плавного переключения окон
function switchWindow(targetWindow) {
    document.querySelectorAll('.window').forEach(win => win.classList.remove('active'));
    targetWindow.classList.add('active');
}

// Запуск временной анимации для питомца
function triggerAvatarState(className, emoji, duration = 800) {
    petAvatar.className = `pet-avatar ${className}`;
    if (emoji) petAvatar.innerText = emoji;

    setTimeout(() => {
        if (currentPetId) {
            petAvatar.className = 'pet-avatar state-idle';
            petAvatar.innerText = '🦖';
        }
    }, duration);
}

// Всплывающие пиксельные эффекты текста (-2 💀, +1 ❤️)
function showFloatingEffect(text, color) {
    const container = document.getElementById('floating-effects');
    const el = document.createElement('div');
    el.className = 'floating-text';
    el.innerText = text;
    el.style.color = color;
    el.style.left = `${Math.random() * 40 + 30}%`; // Случайное смещение по центру
    container.appendChild(el);
    setTimeout(() => el.remove(), 800);
}

// Обновление данных на экране
function updateScreen(data) {
    if (data.gone) {
        switchWindow(deathWindow);
        document.getElementById('death-reason').innerText = data.message || "Питомец исчез.";
        currentPetId = null;
        lastHp = null;
        return;
    }

    currentPetId = data.id;
    document.getElementById('display-name').innerText = data.name;
    document.getElementById('stat-happiness').innerText = data.happiness;
    document.getElementById('stat-hunger').innerText = data.hunger;
    document.getElementById('stat-hp').innerText = data.hp;

    // Проверка на получение урона (тряска корпуса)
    if (lastHp !== null && data.hp < lastHp) {
        tamagotchiCase.classList.add('shake-case');
        showFloatingEffect(`-${lastHp - data.hp} HP 💔`, '#c0392b');
        setTimeout(() => tamagotchiCase.classList.remove('shake-case'), 400);
    }
    lastHp = data.hp;

    switchWindow(gameWindow);
}

// Кнопка: Создать
document.getElementById('btn-create').addEventListener('click', async () => {
    const name = document.getElementById('pet-name').value;
    const hp = parseInt(document.getElementById('pet-hp').value, 10);

    if (!name.trim()) return alert('Укажите имя для питомца!');

    try {
        const response = await fetch(`${API_URL}/pets`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, hp })
        });

        const data = await response.json();
        if (response.ok) {
            updateScreen(data);
            triggerAvatarState('state-happy', '🐣', 1200);
            document.getElementById('game-message').innerText = "Я родился и готов к игре!";
        } else {
            alert(data.error || "Ошибка валидации бэкенда");
        }
    } catch (err) {
        alert("Ошибка: Проверьте работу Python-сервера.");
    }
});

// Кнопки действий
document.querySelectorAll('.action-btn').forEach(button => {
    button.addEventListener('click', async () => {
        if (!currentPetId) return;

        const action = button.getAttribute('data-action');

        // Визуальный отклик до ответа сервера (Кастомные анимации под действия)
        if (action === 'feed') { triggerAvatarState('state-eating', '🍖'); showFloatingEffect('-2 💀', '#27ae60'); }
        if (action === 'pat') { triggerAvatarState('state-happy', '🥰'); showFloatingEffect('+1 😊', '#27ae60'); }
        if (action === 'treat') { triggerAvatarState('state-eating', '🍬'); showFloatingEffect('+2 😊', '#27ae60'); }
        if (action === 'walk') { triggerAvatarState('state-walking', '🏃‍♂️'); showFloatingEffect('+3 💀', '#d35400'); }
        if (action === 'ignore') { triggerAvatarState('state-sleeping', '💤'); showFloatingEffect('-1 😊', '#c0392b'); }

        try {
            const response = await fetch(`${API_URL}/pets/${currentPetId}/${action}`, { method: 'POST' });
            const data = await response.json();

            if (response.ok) {
                updateScreen(data);
                if (!data.gone) {
                    const messages = {
                        feed: "М-м-м, вкусно!",
                        pat: "Ур-р-р, приятно!",
                        treat: "Обожаю сладкое!",
                        walk: "Отличная прогулка!",
                        ignore: "*Питомец грустит в углу*"
                    };
                    document.getElementById('game-message').innerText = messages[action];
                }
            }
        } catch (err) {
            console.error("Ошибка сети:", err);
        }
    });
});

// Кнопка: Начать заново
document.getElementById('btn-restart').addEventListener('click', () => {
    switchWindow(creationWindow);
    document.getElementById('pet-name').value = '';
    petAvatar.innerText = '🦖';
});
