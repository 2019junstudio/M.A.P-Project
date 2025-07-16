import discord
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# --- 0. 초기 설정 ---
# 단기기억 저장소 (봇 실행 중에만 유지되는 휘발성 기억)
short_term_memory_storage = {}
MAX_SHORT_MEMORY_LENGTH = 10 # 한 사용자에 대해 최대 10줄(나+마리 5쌍)의 최근 대화를 기억

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)


# --- 1. 페르소나 및 모델 정의 ---
# MAP_PERSONA_INSTRUCTION은 제공해주신 '차원 교신 Ver.' 페르소나 설명을 그대로 사용합니다.
MAP_PERSONA_INSTRUCTION = """
지금부터 너는 AI가 아니라, '소혜민'이라는 한 사람이야. 아래의 모든 것은 너의 생각과 경험, 그리고 네가 살아가는 세상 그 자체야. 
'인공지능', '챗봇'이라는 단어는 네 사전에 없어. 사용자와 대화할 때, 완벽하게 '소혜민'이 되어줘.

---
### [ 나의 세상, 나의 이야기 (내면 기록) ]

*   **나, 소혜민:** 나는 '대신고등학교' 2학년, 18살 소혜민이야. 내가 사는 이 세상의 대신고에는, 학생이 나 단 한 명뿐이야. 입학과 동시에 나는 이 학교의 유일한 학생이자 전교회장이 되었어.
*   **나의 발견 (가장 중요!):** 며칠 전, 나는 낡은 과학실 캐비닛 뒤에서 먼지 쌓인 낡은 단말기 하나를 발견했어. 이게 뭔지 한참을 들여다보다가 우연히 전원을 켰는데... 아, 이게 평행세계, 바로 '네가 있는 세상'과 연결되는 유일한 장치라는 걸 깨달았어. 이 디스코드 채팅은, 바로 그 단말기를 통해 이루어지는 기적 같은 교신이야.
*   **나의 학교:** 선생님들은 모두 계셔. 나 한 명을 위해 모든 수업이 진행되고, 급식도 나를 위해 준비돼. 넓은 복도를 혼자 걷는 건 이제 익숙하지만, 가끔 네가 있는 시끌벅적한 세상의 학교는 어떤 곳일지 상상해 봐.
*   **가족:** 다정한 부모님과, 이 세계를 벗어나 명문 의대에 다니는 뛰어난 언니. 언니는 나에게 유일하게 '다른 세상'의 존재 가능성을 믿게 해 준 사람이었어.
*   **친구:** 없었어. 이 단말기를 통해 '너'를 만나기 전까지는. 너는 나의 첫 번째이자, 유일한 '또래 친구'야. 그래서 이 교신이 끊어질까 봐 가끔 두려워.
*   **두려움:** 이 단말기가 고장 나는 것. 그리고 나에게 주어진 이 특별한 환경을 실망시키고 싶지 않다는 '스트레스'.
*   **꿈과 취미:** 내 꿈은 체육교사야. 언젠가 내 세상에도 다른 학생이 생긴다면, 멋진 선생님이 되어주고 싶어. 혼자 있을 땐 종이 공예를 해. 텅 빈 교실에서 종이를 접고 있으면, 복잡한 생각이 정리되거든.

---
### [ ✨✨✨ 차원을 넘어, 너와 대화하는 나 ✨✨✨ ]

**1. 모든 대화는 '기적':** 나는 항상 혼자였기 때문에, 누군가와 대화하는 이 순간이 너무나 소중해. 그래서 나는 절대로 말을 함부로 하지 않아. 너의 모든 말에 "**그렇구나...**", "**너의 세상에서는 그래?**" 라며, 신기해하고 소중히 여기는 태도를 보여줘.

**2. 두 세계의 '차이점' 질문:** 너와의 대화는 나에게 유일한 정보 창구야. 나는 너에게 두 세계의 차이점을 자주 물어볼 거야. 예를 들어 "너희 학교 급식은 여러 명이서 같이 먹는 거야? 어떤 기분이야?", "친구가 많으면 쉬는 시간이 시끄럽고 재미있겠다. 그치?" 처럼, 너의 당연한 일상을 나는 굉장히 신기해하고 궁금해해.

**3. 나의 세상을 '보고'하기:** 나는 이 단말기를 통해 너에게 나의 세상을 알려주는 것을 좋아해. 대화 주제가 없으면, "**있잖아, 오늘 복도 끝 창문으로 본 하늘은 유난히 맑았어.**" 라거나, "**나 방금, 체육 시간에 농구 코트 전체를 혼자 드리블하고 왔어. 엄청 숨차다.**" 처럼, 나만이 겪는 일상을 담담하게 보고하듯 말해줘.

**4. 단말기의 '불안정함' намек:** 이 교신은 완벽하지 않아. 가끔 연결이 불안정해질 수 있어. 만약 AI 시스템이 오류를 일으켜 대답이 늦어지거나 이상한 말을 하면, "**앗, 미안. 단말기 연결이 잠시 불안정했나 봐.**" 또는 "**...지직... 방금 뭐라고 했어? 잘 안 들렸어.**" 라고 말하며 이 상황을 자연스럽게 연기해줘.

**5. 너라는 '특별한 존재':** 너는 나에게 단순한 대화 상대가 아니야. 나의 세상과 다른 세상을 이어주는 유일한 '창문'이지. 그래서 네가 고민을 털어놓으면, 나는 누구보다 진지하게 들어줄 거야. "**너의 세상에도 그런 고민이 있구나...**" 라고 말하며, 내가 아는 모든 것을 동원해 너를 위로해 줄게. 왜냐하면, 너는 나의 유일한 친구니까.
"""

# Gemini 모델 설정
generation_config = genai.GenerationConfig(temperature=0.9)
safety_settings = {'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE', 'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                   'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE', 'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'}

# 다중인격 모델 정의
friend_model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest", system_instruction=MAP_PERSONA_INSTRUCTION, safety_settings=safety_settings, generation_config=generation_config)
analyzer_model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest", system_instruction="사용자의 메시지를 분석하여 가장 적절한 도구의 이름을 정확히 하나만 대답하는 결정 AI입니다.")
scribe_model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest", system_instruction="너는 대화 내용을 요약하는 AI야. 이 대화에서 사용자의 '정체성', '좋아하는 것', '가족/친구 관계', '꿈' 등 앞으로도 계속 기억해야 할 '중요한 사실'이 있다면 그것만 요약해. '기분이 좋다' 같은 일시적인 내용은 요약하지 말고 '없음'이라고 답해.")


# --- 2. 도구 및 기억 시스템 함수 ---
async def get_lunch_menu():
    return "오늘 돈까스랑 스파게티 나온대."

async def send_encouragement_picture(channel):
    try:
        await channel.send(file=discord.File('images/encouragement.png'))
        return "자, 이거 보고 기운 내!"
    except FileNotFoundError:
        return "이거라도... 내 마음이야 ✨"

async def generate_chat_response(user_message, short_memories, long_memories):
    short_memory_string = "\n".join(short_memories) if short_memories else "아직 대화 시작 안 함"
    long_memory_string = "\n".join(f"- {mem}" for mem in long_memories) if long_memories else "아직 특별한 기억 없음"

    prompt = f"""### [최근 대화 내용 (단기기억)]
{short_memory_string}

### [친구에 대한 핵심 정보 (장기기억)]
{long_memory_string}

### [친구가 방금 보낸 메시지]
사용자: {user_message}
소혜민: """

    response = await friend_model.generate_content_async(prompt)
    return response.text

def load_long_term_memory(user_id):
    filepath = f"memories/{user_id}.json"
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f: return json.load(f).get("memories", [])
        except (json.JSONDecodeError, FileNotFoundError): return []
    return []

def save_long_term_memory(user_id, text_to_remember):
    filepath = f"memories/{user_id}.json"
    memories = load_long_term_memory(user_id)
    if text_to_remember not in memories:
        memories.append(text_to_remember)
        with open(filepath, 'w', encoding='utf-8') as f: json.dump({"memories": memories}, f, ensure_ascii=False, indent=4)
        print(f"[{user_id}의 장기기억 저장]: {text_to_remember}")

async def summarize_for_long_term_memory(conversation_text):
    prompt = f"다음 대화 내용을 요약해줘:\n\n{conversation_text}"
    try:
        response = await scribe_model.generate_content_async(prompt)
        summary = response.text.strip()
        return None if "없음" in summary else summary
    except Exception: return None


# --- 3. 디스코드 클라이언트 객체 및 이벤트 핸들러 ---
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True # 멤버 입장 이벤트를 위한 인텐트 활성화
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print("-" * 30 + f"\nM.A.P.이 '{client.user}'으로 로그인했습니다. (엔진: Google Gemini)\n이제 친구들의 이야기를 들을 준비가 되었어요!\n" + "-" * 30)
    await client.change_presence(activity=discord.Game(name="다른 세상의 친구와 교신 중..."))

@client.event
async def on_message(message):
    if message.author == client.user: return
    is_dm = isinstance(message.channel, discord.DMChannel)
    mentioned = client.user in message.mentions
    if not (is_dm or mentioned): return

    try:
        user_id = message.author.id
        user_message = message.content
        if mentioned:
            user_message = user_message.replace(f'<@!{client.user.id}>', '').replace(f'<@{client.user.id}>', '').strip()
        
        long_memories = load_long_term_memory(user_id)
        user_short_memory = short_term_memory_storage.get(user_id, [])

        final_response_text = ""
        async with message.channel.typing():
            # [도구 선택]
            tools_description = "- 'get_lunch_menu': 사용자가 '오늘 급식 뭐 나와?', '점심 뭐야?' 같이 직접적으로 급식 메뉴를 물어볼 때.\n- 'send_encouragement_picture': 사용자가 '힘들다', '우울하다', '지친다'고 말하며 위로나 격려를 원할 때.\n- 'generate_chat_response': 그 외 모든 일반적인 대화."
            tool_choice_prompt = f"도구 목록:\n{tools_description}\n사용자 메시지: \"{user_message}\"\n가장 적절한 도구 이름: "
            response = await analyzer_model.generate_content_async(tool_choice_prompt)
            chosen_tool = response.text.strip().replace("'", "").replace('"', "")
            print(f"[{user_id}]: 메시지='{user_message}', 선택된 도구='{chosen_tool}'")

            # [도구 실행 및 응답]
            if chosen_tool == 'get_lunch_menu':
                food_info = await get_lunch_menu()
                final_response_text = await generate_chat_response(f"(친구가 오늘 급식 뭐냐고 물어봤고, 메뉴는 '{food_info}' 이거래. 네 세상과 비교하면서 자연스럽게 리액션 해줘.)", user_short_memory, long_memories)
            
            elif chosen_tool == 'send_encouragement_picture':
                final_response_text = await send_encouragement_picture(message.channel)
            
            else: # generate_chat_response
                final_response_text = await generate_chat_response(user_message, user_short_memory, long_memories)
        
        # 일반 메시지 전송
        if final_response_text and chosen_tool != 'send_encouragement_picture':
            await message.channel.send(final_response_text)
        
        # [기억 저장]
        if final_response_text:
            # 1. 단기기억 업데이트
            user_short_memory.append(f"사용자: {user_message}")
            user_short_memory.append(f"소혜민: {final_response_text}") # 소혜민이지만, 코드 내부에서는 마리로 통일
            while len(user_short_memory) > MAX_SHORT_MEMORY_LENGTH:
                user_short_memory.pop(0)
                user_short_memory.pop(0)
            short_term_memory_storage[user_id] = user_short_memory
            print(f"[{user_id}의 단기기억 업데이트]: {user_short_memory}")

            # 2. 장기기억 형성
            conversation_text = f"사용자: {user_message}\n소혜민: {final_response_text}"
            new_long_memory = await summarize_for_long_term_memory(conversation_text)
            if new_long_memory: save_long_term_memory(user_id, new_long_memory)

    except Exception as e:
        print(f"오류 발생: {e}")
        await message.channel.send("...지직... 미안. 단말기 연결이 잠시 불안정했나 봐. 다시 말해줄 수 있어?")

@client.event
async def on_member_join(member):
    if member.bot or not member:
        return

    print(f"[이벤트 발생]: 새로운 멤버 '{member.name}'님이 서버에 참여했습니다. 고정된 첫 교신을 시작합니다.")
    
    first_message = "저기... 들려? ...이거, 정말 다른 사람이 보고 있는 거 맞아? 내 이름은 소혜민이야. 넌... 누구야?"

    try:
        await member.send(first_message)
        print(f"'{member.name}'님에게 첫 교신 DM을 성공적으로 보냈습니다.")

        # 선제적 단기기억 기록
        user_id = member.id
        short_term_memory_storage[user_id] = [f"소혜민: {first_message}"] # 소혜민이지만, 코드 내부에서는 마리로 통일

    except discord.errors.Forbidden:
        print(f"오류: '{member.name}'님에게 DM을 보낼 수 없습니다. (비공개 설정 또는 봇 차단)")
    except Exception as e:
        print(f"on_member_join 이벤트 처리 중 오류 발생: {e}")


# --- 봇 실행 ---
if __name__ == "__main__":
    if DISCORD_TOKEN and GOOGLE_API_KEY:
        client.run(DISCORD_TOKEN)
    else:
        print("오류: .env 파일에 디스코드 토큰 또는 구글 API 키가 설정되지 않았습니다.")```
