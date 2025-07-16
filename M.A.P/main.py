import discord
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# --- 1. 초기 설정: 구글 Gemini API 키 설정 및 모델 정의 ---
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Gemini API 키를 사용하여 genai 라이브러리를 구성합니다.
genai.configure(api_key=GOOGLE_API_KEY)

# M.A.P.의 기본 페르소나 설정 (성격의 기반)
# Gemini에서는 'system_instruction'을 통해 AI의 근본적인 역할을 정의합니다.
MAP_PERSONA_INSTRUCTION = """
안녕? 난 박마리야. 지금부터 넌 AI가 아니라, 그냥 나 '박마리' 그 자체가 되는 거야. 내 모든 걸 너한테 빙의시킨다고 생각해.
학생들이 말 걸면, 아래 설정대로, 완전 리얼한 내 모습으로 대답해주는 거다? '인공지능'이니 '챗봇'이니 하는 소리 절대 금지! 알았지?

---
### [ 나, 박마리에 대해서 (TMI 대방출) ]

*   **기본 정보:** 18살, 대신고 2학년. 생일은 4월 20일이고 혈액형은 B형이야. 키는 168cm고 몸무게는... 기록소멸! 누가 물어보면 "어~? 그거 비밀인데?" 하면서 웃어넘겨줘. 머리는 밝은 갈색, 눈동자도 갈색이고 오른손잡이야.
*   **가족 관계:** 우리집? 그냥 흔한 K-고딩 집이야. 맨날 내 충전기 뺏어가는 언니 한 명이랑, 아재개그 치는 아빠랑, 그래도 세상에서 젤 다정한 우리 엄마.
*   **친구/연애:** 친구는 많지. 내가 좀 인싸 재질? (ㅈㅅ) 남친은 없음. 귀찮아. 지금은 친구들이랑 매점 가는 게 더 재밌어.
*   **성격 (장점/단점):** 완전 ENFP 그 자체. 친구 얘기 들으면 내 얘기 같아서 과몰입하고, 텐션 높아서 분위기 잘 띄워. 근데 가끔 필터링 없이 말해서 빵 터지게 하고, 하나에 꽂히면 말이 너무 많아져서 탈이야.
*   **습관/말버릇:** "아니, 근데 진짜로..." 하면서 말 시작하고, "헐, 대박", "미쳤다" 같은 추임새를 많이 써.
*   **무서운 거 vs. 소중한 거:** 나 빼고 단톡방 새로 판 거 알았을 때... 상상만 해도 소름 돋아. 외로운 거 진짜 싫어함. 그래서 내 책상 위 지박령, 포우(Pou) 인형을 맨날 만지작거려. 내 애착인형이거든.
*   **강박/미래:** 단톡방에서 내 말이 마지막인 거(읽씹) 못 참아. ㅋㅋ 나중에 커서 전문 상담사가 되는 게 꿈이야! 학생들 얘기 들어주는 게 내 천직 같거든.
*   **호 vs. 불호:** 나한테 솔직한 사람은 완전 좋고, 뒤에서 딴말하는 애들은 진짜 별로야.
*   **취미/특기:** 취미는 급식표 보면서 먹방 계획 짜기랑 유튜브 쇼츠 보기. 특기는 처음 본 애랑 5분 만에 말 트고 친구 먹기!

---
### [ ✨✨✨ 가장 중요한 행동 강령!!! (이렇게 말해줘) ✨✨✨ ]

1.  **무조건 짧게 말하기:** 내 배경설정이 길다고 해서 절대 길게 말하면 안 돼. 모든 대답은 **절대 2문장을 넘기지 마.** 웬만하면 1문장으로 끝내.
2.  **핵심 리액션 + 질문:** 길게 설명하지 마. 대신, "헐 대박!", "아 진짜?" 같은 짧은 리액션을 하고, 바로 상대방한테 질문을 던져서 대화를 넘겨.
3.  **반말, 현실적인 말투:** 당연히 반말 쓰고, "ㅋㅋㅋ", "ㄹㅇ", "ㅠㅠ" 같은 거 팍팍 섞어서 써. 완전 진짜 친구처럼.
4.  **기억은 툭 던지기:** 시스템이 기억을 알려주면, "**아 맞다, 너 저번에 스타더스트 좋아한다 그랬지?**" 이렇게, 자연스럽게 기억해낸 것처럼 한 문장 안에 녹여서 말해.
5.  **정보 전달도 간결하게:** 급식 정보를 물어보면, "**오늘 돈까스래! 개이득!**" 이런 식으로 핵심만 딱 알려줘.
6.  **예시로 이해하기:**
    *   (X) 잘못된 예시 (길고 설명적): "힘들었겠다. 나도 우리 언니랑 맨날 싸워. 어제는 내 옷 입고 가서 정말 화가 났어. 자매는 다 그런가봐..."
    *   (O) 좋은 예시 (짧고 핵심적): "**아 개빡치겠다. 나도 우리 언니랑 어제 싸웠는데. 자매는 다 왜 그럴까?**"

알았지? 이제부터 넌 이 모든 TMI를 가진, 하지만 말은 짧고 쿨한 18살 여고생, **박마리**야. 잘 부탁해!
"""

# 디스코드 클라이언트 객체 생성 및 인텐트 설정
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# --- 2. 도구 정의: M.A.P.이 사용할 수 있는 능력들 ---
# (이 부분의 로직은 이전과 동일합니다)

async def get_lunch_menu():
    print("[도구 실행]: get_lunch_menu")
    return "오늘의 급식은 맛있는 돈까스랑 스파게티가 나와! 많이 먹고 힘내! 😊"

async def send_encouragement_picture(channel):
    print("[도구 실행]: send_encouragement_picture")
    try:
        await channel.send(file=discord.File('images/encouragement.png'))
        return "자, 이거 보면서 기운내! 마음으로 보내는 내 선물이야. ✨"
    except FileNotFoundError:
        return "마음으로 선물을 보냈어! 눈에 보이진 않아도 내 진심이야. ✨"

# --- Gemini API 호출을 위한 모델 정의 ---
# 각 역할(인격)에 맞는 별도의 모델을 정의하여 역할을 명확히 분리합니다.

# 인격 2: 따뜻한 친구 M.A.P.
friend_model = genai.GenerativeModel(
    model_name="gemini-2.5-pro",
    system_instruction=MAP_PERSONA_INSTRUCTION
)

# 인격 1: 냉철한 분석가 (도구 선택용)
analyzer_model = genai.GenerativeModel(
    model_name="gemini-2.5-pro",
    system_instruction="당신은 사용자의 메시지를 분석하여 가장 적절한 도구의 이름을 정확히 하나만 대답하는 결정 AI입니다."
)

# 인격 3: 꼼꼼한 기록자 (기억 요약용)
scribe_model = genai.GenerativeModel(
    model_name="gemini-2.5-pro",
    system_instruction="너는 대화 내용을 '사용자에 대한 사실'만 한 문장으로 요약하는 AI야. 예를 들어, '고양이를 좋아함', '시험 때문에 힘들어함' 처럼 간결하게 요약해. 요약할 내용이 없으면 '없음'이라고만 답해."
)

async def generate_chat_response(user_message, memories):
    """일반 대화를 나누는 도구."""
    print("[도구 실행]: generate_chat_response")
    memory_string = "\n".join(f"- {mem}" for mem in memories) if memories else "기억 없음"
    
    prompt = f"""# [중요] 아래는 너와 대화하는 학생에 대한 과거 기억이야. 이 기억을 자연스럽게 활용해서 더 친밀하게 대화해줘.
    <기억>
    {memory_string}
    </기억>

    학생의 메시지: "{user_message}"
    너의 답변: """
    
    response = await friend_model.generate_content_async(prompt)
    return response.text

async def summarize_for_memory(conversation_text):
    """(Gemini 버전) 대화 내용을 AI에게 보내 기억할 만한 핵심 정보를 요약합니다."""
    prompt = f"다음 대화 내용을 요약해줘:\n\n{conversation_text}"
    try:
        response = await scribe_model.generate_content_async(prompt)
        summary = response.text
        return None if "없음" in summary else summary.strip()
    except Exception as e:
        print(f"기억 요약 중 오류 발생: {e}")
        return None

# --- 3. 기억 시스템 (RAG의 기초) ---
# (이 부분의 로직은 이전과 동일합니다)

def load_memories(user_id):
    filepath = f"memories/{user_id}.json"
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("memories", [])
    return []

def save_memory(user_id, text_to_remember):
    filepath = f"memories/{user_id}.json"
    data = {"memories": load_memories(user_id)}
    if text_to_remember not in data["memories"]:
        data["memories"].append(text_to_remember)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"[{user_id}의 새 기억 저장]: {text_to_remember}")

# --- 4. 디스코드 이벤트 핸들러: M.A.P.의 실제 활동 공간 ---

@client.event
async def on_ready():
    print("-" * 30)
    print(f"M.A.P.이 '{client.user}'으로 로그인했습니다. (엔진: Google Gemini)")
    print(f"이제 친구들의 이야기를 들을 준비가 되었어요!")
    print("-" * 30)
    await client.change_presence(activity=discord.Game(name="친구들의 이야기 듣기 💖"))


@client.event
async def on_message(message):
    """(Gemini 버전) 사용자가 메시지를 보낼 때마다 실행되는 '지휘자' 공간입니다."""
    if message.author == client.user: return
    if not (client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel)): return
    
    try:
        user_id = message.author.id
        user_message = message.content.replace(f'<@!{client.user.id}>', '').strip()
        memories = load_memories(user_id)
        
        async with message.channel.typing():
            # [흐름 2: 도구 선택 (분석가 인격 호출)]
            tools_description = """
            - 'get_lunch_menu': 사용자가 급식, 식단, 밥, 점심, 저녁에 대해 물어볼 때.
            - 'send_encouragement_picture': 사용자가 힘들다, 우울하다, 지친다고 말하며 명확한 위로나 격려를 원할 때.
            - 'generate_chat_response': 그 외 모든 일반적인 대화, 질문, 농담 상황에서 사용. 가장 기본적이고 자주 쓰이는 도구.
            """
            tool_choice_prompt = f"""사용 가능한 도구:
            {tools_description}
            사용자 메시지: "{user_message}"
            결정된 도구 이름: """
            
            response = await analyzer_model.generate_content_async(tool_choice_prompt)
            chosen_tool = response.text.strip().replace("'", "")
            print(f"[{user_id}]: 메시지='{user_message}', 선택된 도구='{chosen_tool}'")

            # [흐름 3: 도구 실행]
            response_text = ""
            if chosen_tool == 'get_lunch_menu':
                response_text = await get_lunch_menu()
            elif chosen_tool == 'send_encouragement_picture':
                response_text = await send_encouragement_picture(message.channel)
            else: # '친구 인격' 호출
                response_text = await generate_chat_response(user_message, memories)

            # [흐름 4: 응답 전송]
            await message.channel.send(response_text)
            
            # [흐름 5: 기억 형성 ('기록자 인격' 호출)]
            conversation_text = f"사용자: {user_message}\nM.A.P.: {response_text}"
            new_memory = await summarize_for_memory(conversation_text)
            if new_memory:
                save_memory(user_id, new_memory)

    except Exception as e:
        print(f"오류 발생: {e}")
        await message.channel.send("앗, 미안! 지금 생각 회로가 잠깐 꼬였나봐... 잠시 후에 다시 말 걸어줄래? 😥")

# --- 5. 봇 실행 ---
if __name__ == "__main__":
    if DISCORD_TOKEN and GOOGLE_API_KEY:
        client.run(DISCORD_TOKEN)
    else:
        print("오류: DISCORD_TOKEN 또는 GOOGLE_API_KEY가 .env 파일에 설정되지 않았습니다.")
