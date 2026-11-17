const creationWindow = document.getElementById('creation-window');
const gameWindow = document.getElementById('game-window');
const deathWindow = document.getElementById('death-window');

const petNameInput = document.getElementById('pet-name');
const petHpInput = document.getElementById('pet-hp');
const btnCreate = document.getElementById('btn-create');
const btnRestart = document.getElementById('btn-restart');

const displayName = document.getElementById('display-name');
const statHp = document.getElementById('stat-hp');
const statHappiness = document.getElementById('stat-happiness');
const statHunger = document.getElementById('stat-hunger');
const gameMessage = document.getElementById('game-message');
const deathReason = document.getElementById('death-reason');
const petImg = document.getElementById('pet-img');
const actionButtons = document.querySelectorAll('.action-btn');

// Предзагрузка GIF-анимаций
const animations = ['idle', 'happy', 'sleep', 'break'];
animations.forEach(state => {
    const img = new Image();
    img.src = `character/${state}.gif`;
});

let animTimeout = null;
let currentPetState = null;

function playPetAnimation(state, isTemporary = true) {
    if (!petImg) return;

    petImg.src = `character/${state}.gif`;
    clearTimeout(animTimeout);

    if (isTemporary && state !== 'idle') {
        animTimeout = setTimeout(() => {
            // Если заряд или сытость на исходе (<= 2), робот выглядит сломанным
            if (currentPetState && (currentPetState.hp <= 2 || currentPetState.hunger <= 2)) {
                petImg.src = 'character/break.gif';
            } else {
                petImg.src = 'character/idle.gif';
            }
        }, 2500);
    }
}

function updateUI(pet, message = '') {
    currentPetState = pet;

    // Если закончился заряд (HP) или сытость упала до 0 — робот отключается
    if (pet.hp <= 0 || pet.hunger <= 0 || pet.is_dead) {
        gameWindow.classList.add('hidden');
        creationWindow.classList.add('hidden');
        deathWindow.classList.remove('hidden');
        deathReason.textContent = message || `${pet.name} полностью истощил ресурсы!`;
        return;
    }

    creationWindow.classList.add('hidden');
    deathWindow.classList.add('hidden');
    gameWindow.classList.remove('hidden');

    displayName.textContent = pet.name;
    statHp.textContent = pet.hp;
    statHappiness.textContent = pet.happiness;
    statHunger.textContent = `${pet.hunger} / 10`;

    if (message) {
        gameMessage.textContent = message;
    }
}

const API_URL = 'http://localhost:8000';

async function sendRequest(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' }
        };
        if (body) options.body = JSON.stringify(body);

        const response = await fetch(`${API_URL}${endpoint}`, options);
        if (!response.ok) throw new Error('Ошибка сервера');
        return await response.json();
    } catch (error) {
        return simulateBackend(endpoint, body);
    }
}

// Локальная симуляция с уменьшающейся сытостью (максимум 10)
let mockPet = { name: 'Swiko', hp: 10, happiness: 10, hunger: 10, is_dead: false };

function simulateBackend(endpoint, body) {
    if (endpoint === '/create') {
        mockPet = {
            name: body.name || 'Swiko',
            hp: Number(body.hp) || 10,
            happiness: 10,
            hunger: 10,
            is_dead: false
        };
        return { pet: mockPet, message: 'Система запущена!' };
    }

    if (endpoint === '/action') {
        const act = body.action;
        let msg = '';

        if (act === 'feed') {
            mockPet.hunger = Math.min(10, mockPet.hunger + 3);
            mockPet.hp = Math.min(100, mockPet.hp + 1);
            msg = 'Энергия пополнена! 🔋';
        } else if (act === 'pat') {
            mockPet.happiness = Math.min(10, mockPet.happiness + 2);
            mockPet.hunger = Math.max(0, mockPet.hunger - 1);
            msg = 'Сенсоры довольны! ✨';
        } else if (act === 'treat') {
            mockPet.happiness = Math.min(10, mockPet.happiness + 3);
            mockPet.hunger = Math.min(10, mockPet.hunger + 2);
            msg = 'Установлен новый модуль! ⚡';
        } else if (act === 'walk') {
            mockPet.happiness = Math.min(10, mockPet.happiness + 2);
            mockPet.hunger = Math.max(0, mockPet.hunger - 2);
            msg = 'Отличная прогулка! Заряд немного снизился. 🛰️';
        } else if (act === 'ignore') {
            mockPet.hp = Math.max(0, mockPet.hp - 2);
            mockPet.happiness = Math.max(0, mockPet.happiness - 2);
            mockPet.hunger = Math.max(0, mockPet.hunger - 2);
            msg = 'Режим ожидания: ресурсы тают... 💤';
        }

        if (mockPet.hp <= 0 || mockPet.hunger <= 0) {
            mockPet.is_dead = true;
            msg = mockPet.hunger <= 0
                ? 'Критическое истощение энергии!'
                : 'Критическая потеря прочности!';
        }

        return { pet: mockPet, message: msg };
    }
}

btnCreate.addEventListener('click', async () => {
    const name = petNameInput.value.trim() || 'Swiko';
    const hp = parseInt(petHpInput.value, 10) || 10;

    const data = await sendRequest('/create', 'POST', { name, hp });
    if (data && data.pet) {
        updateUI(data.pet, data.message);
        playPetAnimation('happy', true);
    }
});

actionButtons.forEach(button => {
    button.addEventListener('click', async () => {
        if (gameWindow.classList.contains('hidden')) return;

        const action = button.getAttribute('data-action');
        const data = await sendRequest('/action', 'POST', { action });

        if (data && data.pet) {
            updateUI(data.pet, data.message);

            if (action === 'ignore') {
                playPetAnimation('sleep', true);
            } else {
                playPetAnimation('happy', true);
            }
        }
    });
});

btnRestart.addEventListener('click', () => {
    deathWindow.classList.add('hidden');
    gameWindow.classList.add('hidden');
    creationWindow.classList.remove('hidden');
    petNameInput.value = '';
    playPetAnimation('idle', false);
});
