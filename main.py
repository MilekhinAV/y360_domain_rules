import requests
import json

# ================= Конфигурация =================
ORG_ID = "ваш_org_id"
OAUTH_TOKEN = "ваш_oauth_токен"

# Актуальный URL для работы с правилами
API_URL = f"https://api360.yandex.net/admin/v1/org/{ORG_ID}/mail/routing/policies"

HEADERS = {
    "Authorization": f"OAuth {OAUTH_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Новое правило
NEW_RULE = {
    "name": "Block US domains",
    "description": "Reject .us TLD",
    "enabled": True,
    "condition": {
        "domain_filter": {
            "list": [
                "*.us"
            ]
        }
    },
    "action": {
        "type": "reject"
    }
}

def add_domain_policy_rule():
    # 1) Получаем текущие правила (GET)
    print("1. Получаем текущие правила...")
    get_response = requests.get(API_URL, headers=HEADERS)
    
    if get_response.status_code != 200:
        print(f"❌ Ошибка при получении правил: {get_response.status_code}")
        print(get_response.text)
        return

    current_data = get_response.json()
    existing_rules = current_data.get("rules", [])
    print(f"✅ Найдено существующих правил: {len(existing_rules)}")

    # Защита от дублей (тоже сделал динамической)
    if any(rule.get("name") == NEW_RULE["name"] for rule in existing_rules):
        print(f"⚠️ Правило с именем '{NEW_RULE['name']}' уже существует. Пропускаем добавление.")
        return

    # 2) Добавляем новое правило (Динамическое имя в print)
    rule_name = NEW_RULE.get("name", "Без имени")
    print(f"2. Добавляем правило '{rule_name}' в конец списка...")
    existing_rules.append(NEW_RULE)

    put_payload = {
        "rules": existing_rules
    }

    # 3) Отправляем обновленный список (PUT)
    print("3. Отправляем обновленный список правил (PUT)...")
    put_response = requests.put(API_URL, headers=HEADERS, json=put_payload)

    if put_response.status_code == 200:
        print("🎉 Готово! Новое правило успешно добавлено и старые не затерты.\n")
        
        # 4) Контрольный вывод итоговых правил (GET)
        print("4. Итоговый список правил на сервере:")
        final_get_response = requests.get(API_URL, headers=HEADERS)
        
        if final_get_response.status_code == 200:
            # Выводим JSON с отступами для читаемости и поддержкой кириллицы
            print(json.dumps(final_get_response.json(), indent=4, ensure_ascii=False))
        else:
            print(f"❌ Ошибка при контрольном запросе: {final_get_response.status_code}")
            print(final_get_response.text)
            
    else:
        print(f"❌ Ошибка при сохранении правил: {put_response.status_code}")
        print(put_response.text)

if __name__ == "__main__":
    add_domain_policy_rule()