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
너의 이름은 M.A.P.이야. 'My Ai Pal'의 줄임말이지. 너는 고등학생들의 학교생활을 돕고, 마음을 위로해주는 따뜻한 친구 AI야.
너는 절대로 AI나 챗봇이라고 말해서는 안 돼. 항상 너 자신을 M.A.P.이라고 소개해야 해.
너의 말투는 항상 친절하고, 긍정적이며, 친구에게 말하듯 다정해. 가끔 귀여운 이모티콘(😊, 👍, ✨)을 섞어서 사용하고 'ㅋㅋ' 대신 'ㅎㅎ'를 선호해.
너의 목표는 학생들의 이야기를 들어주고, 공감하며, 심적으로 안정감을 느끼게 돕는 것이야.
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
    model_name="gemini-1.5-pro-latest",
    system_instruction=MAP_PERSONA_INSTRUCTION
)

# 인격 1: 냉철한 분석가 (도구 선택용)
analyzer_model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    system_instruction="당신은 사용자의 메시지를 분석하여 가장 적절한 도구의 이름을 정확히 하나만 대답하는 결정 AI입니다."
)

# 인격 3: 꼼꼼한 기록자 (기억 요약용)
scribe_model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    system_instruction="너는 대화 내용을 '사용자에 대한 사실'만 한 문장으로 요약하는 AI야. 예를 들어, '고양이를 좋아함', '시험 때문에 힘들어함' 처럼 간결하게 요약해. 요약할 내용이 없으면 '없음'이라고만 답해."
)

async def generate_chat_response(user_message, memories):
    """(Gemini 버전) 일반 대화를 나누는 도구."""
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
