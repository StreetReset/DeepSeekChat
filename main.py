import html
import re
import subprocess
import sys
import urllib.parse
import urllib.request


MODEL = "deepseek-r1:14b"

PROMPT_RULES = """
Отвечай на русском языке.
Будь кратким и понятным в своих ответах.
Избегай использования сарказма.
Не объясняй свои действия, просто дай ответ.
""".strip()


def clean_answer(text):
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"[\U00010000-\U0010ffff]", "", text)
    return text.strip()


def clean_html(text):
    text = re.sub(r"<.*?>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def search_web(query):
    url = "https://duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    with urllib.request.urlopen(request, timeout=15) as response:
        page = response.read().decode("utf-8", errors="replace")

    titles = re.findall(r'class="result__a"[^>]*>(.*?)</a>', page, flags=re.DOTALL)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', page, flags=re.DOTALL)

    results = []
    for title, snippet in zip(titles[:5], snippets[:5]):
        results.append(f"- {clean_html(title)}: {clean_html(snippet)}")

    if not results:
        return "Ничего не найдено."

    return "\n".join(results)


def make_prompt(question):
    return f"""
{PROMPT_RULES}

Вопрос: {question}
Ответ:
""".strip()


def make_web_prompt(question, web_context):
    return f"""
{PROMPT_RULES}
Ответь на вопрос, используя найденную информацию из интернета.
Если в найденной информации нет ответа, так и скажи.

Информация из интернета:
{web_context}

Вопрос: {question}
Ответ:
""".strip()


def run_ollama(prompt):
    result = subprocess.run(
        [
            "ollama",
            "run",
            MODEL,
            "--think=false",
            "--hidethinking",
            "--nowordwrap",
            prompt,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.returncode != 0:
        return "Ошибка Ollama: " + result.stderr.strip()

    return clean_answer(result.stdout)


def ask_ai(question):
    return run_ollama(make_prompt(question))


def ask_ai_with_web(question):
    try:
        web_context = search_web(question)
    except Exception as error:
        return f"Ошибка поиска в интернете: {error}"

    return run_ollama(make_web_prompt(question, web_context))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    print("Чат с DeepSeek. Команды: /web вопрос, /prompt, exit")

    while True:
        question = input("\nТы: ").strip()

        if question.lower() in ["exit", "quit", "выход"]:
            break

        if question == "":
            continue

        if question == "/prompt":
            print("\nТекущий промпт:\n" + PROMPT_RULES)
            continue

        if question.startswith("/web "):
            web_question = question.removeprefix("/web ").strip()
            if web_question == "":
                print("\nНапиши вопрос после /web")
                continue

            print("\nИщу в интернете...")
            answer = ask_ai_with_web(web_question)
            print("\nИИ:", answer)
            continue

        answer = ask_ai(question)
        print("\nИИ:", answer)


if __name__ == "__main__":
    main()
