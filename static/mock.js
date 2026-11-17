// =========================================================================
//  БЛОК МОК-ДАННЫХ (ТОЧНАЯ ИМИТАЦИЯ МАТЕМАТИКИ БЭКЕНДА)
// =========================================================================

const mockPetState = {
    id: 1337,
    name: "Swiko",
    hp: 10,
    happiness: 2,
    hunger: 2,
    hunger_penalty_count: 0
};

const originalFetch = window.fetch;
window.fetch = async function(url, options) {
    // Небольшая задержка сети для отслеживания блокировки кнопок
    await new Promise(resolve => setTimeout(resolve, 300));

    // Перехват создания питомца (POST /pets)
    if (url.endsWith('/pets') && options && options.method === 'POST') {
        const body = JSON.parse(options.body);
        mockPetState.name = body.name || "Swiko";
        mockPetState.hp = body.hp || 10;
        mockPetState.happiness = 2;
        mockPetState.hunger = 2;
        mockPetState.hunger_penalty_count = 0;

        return {
            ok: true,
            status: 201,
            json: async () => ({ ...mockPetState })
        };
    }

    // Перехват игровых действий (POST /pets/<id>/<action>)
    if (url.includes('/pets/') && options && options.method === 'POST') {
        const parts = url.split('/');
        const action = parts[parts.length - 1];

        // 🎯 СТРОГОЕ СЛЕДОВАНИЕ ВАШИМ ПРАВИЛАМ И КЛАССУ PET 🎯
        if (action === 'feed') {
            // Покормить: голод -2 (минимальный голод = 0)
            mockPetState.hunger = Math.max(0, mockPetState.hunger - 2);
        } else if (action === 'pat') {
            // Погладить: счастье +1, голод +1
            mockPetState.happiness += 1;
            mockPetState.hunger += 1;
        } else if (action === 'treat') {
            // Дать вкусняшку: счастье +2, голод -1
            mockPetState.happiness += 2;
            mockPetState.hunger = Math.max(0, mockPetState.hunger - 1);
        } else if (action === 'walk') {
            // Отправиться в лес: счастье +1, голод +3
            mockPetState.happiness += 1;
            mockPetState.hunger += 3;
        } else if (action === 'ignore') {
            // Пропустить день: счастье -1, голод +1
            mockPetState.happiness -= 1;
            mockPetState.hunger += 1;
        }

        // --- Логика начисления штрафов за голод (__change_hunger на бэкенде) ---
        if (mockPetState.hunger > 5) {
            // Если голод > 5, питомец получает урон (1 + текущий накопленный штраф)
            const damage = 1 + mockPetState.hunger_penalty_count;
            mockPetState.hp -= damage;
            mockPetState.hunger_penalty_count += 1; // Увеличиваем штраф на будущее
        } else {
            // Если вовремя покормили и голод упал до 5 или ниже — штраф сбрасывается в 0
            mockPetState.hunger_penalty_count = 0;
        }

        // --- Проверка условий поражения (Смерть или Побег персонажа) ---
        if (mockPetState.hp <= 0 || mockPetState.happiness <= 0) {
            let deathMessage = "";
            if (mockPetState.hp <= 0) {
                deathMessage = `Питомец ${mockPetState.name} погиб в лесу от критического истощения! 💀 (HP упало до 0)`;
            } else if (mockPetState.happiness <= 0) {
                deathMessage = `Питомец ${mockPetState.name} собрал вещи, обиделся и навсегда ушел от вас! 😭 (Счастье упало до 0)`;
            }

            return {
                ok: true,
                status: 200,
                json: async () => ({
                    id: mockPetState.id,
                    gone: true,
                    message: deathMessage
                })
            };
        }

        return {
            ok: true,
            status: 200,
            json: async () => ({ ...mockPetState })
        };
    }

    return { ok: false, status: 404, json: async () => ({ error: "Not found" }) };
};
