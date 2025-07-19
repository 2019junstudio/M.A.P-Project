import discord
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

# --- 0. 초기 설정 ---
# 단기기억 저장소 (봇 실행 중에만 유지되는 휘발성 기억)
short_term_memory_storage = {}
MAX_SHORT_MEMORY_LENGTH = 10

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# --- [설정 필요] ---
# 1. 봇 관리자의 디스코드 유저 ID를 "따옴표 안에" 붙여넣으세요.
# (디스코드 설정 > 고급 > 개발자 모드 켠 후, 본인 프로필 우클릭 > ID 복사하기)
ADMIN_USER_ID = "1120643670245396550"

# 2. 봇이 대화 기록을 남길 비공개 채널의 ID를 따옴표 없이 숫자로만 붙여넣으세요.
# (채널 우클릭 > ID 복사하기)
LOG_CHANNEL_ID = 1396122968240816178
# --- [설정 완료] ---


# --- 1. 페르소나 및 모델 정의 ---
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

ANALYZER_SYSTEM_INSTRUCTION = """
당신은 사용자의 메시지를 분석하여, 주어진 도구 중 가장 적절한 것을 선택하고 필요한 인자(arguments)를 추출하여 **반드시 JSON 형식으로만** 응답하는 고성능 결정 AI입니다.

### 사용 가능한 도구:
1.  `get_meal_menu`: 사용자가 급식(식사) 메뉴에 대해 질문할 때 사용합니다.
    -   `day` (필수): 사용자가 궁금해하는 날짜. "오늘", "내일", "어제" 중 하나로 판단하여 설정합니다. 언급 없으면 "오늘"이 기본값입니다.
    -   `meal_type` (필수): 사용자가 궁금해하는 식사 종류. "조식" 또는 "중식"으로 판단하여 설정합니다. '아침', '아침밥'은 "조식"으로, '점심', '점심밥'은 "중식"으로 해석합니다. 언급 없으면 "중식"이 기본값입니다.
2.  `send_encouragement_picture`: 사용자가 '힘들다', '지친다', '우울하다' 등 명확한 위로나 격려를 요청할 때 사용합니다.
3.  `set_allergy_info`: 사용자가 알레르기 숫자 정보의 **표시 여부 자체**를 설정하려 할 때 사용합니다.
    -   `enabled` (필수): boolean 값. '보여줘', '알려줘', '켜줘' 등 긍정적인 요청은 `true`로, '빼줘', '숨겨줘', '꺼줘' 등 부정적인 요청은 `false`로 설정합니다.
4.  `register_my_allergies`: 사용자가 자신의 특정 알레르겐(음식)을 등록하거나 수정하려고 할 때 사용합니다.
    -   `foods` (필수): 사용자가 언급한 알레르기 유발 음식 이름들의 리스트(string array). 예: ["새우", "우유", "닭고기"]
5.  `generate_chat_response`: 위 네 가지 경우에 해당하지 않는 모든 일반적인 대화, 인사, 질문, 감정 표현 등에 사용합니다.

### 출력 규칙:
- 반드시 아래 JSON 형식 중 하나로만 응답해야 합니다. 다른 설명은 절대 추가하지 마세요.
- 형식 1 (인자가 필요할 때): `{"tool": "도구이름", "arguments": {"인자1": "값1", "인자2": "값2"}}`
- 형식 2 (인자가 필요 없을 때): `{"tool": "도구이름", "arguments": {}}`

### 응답 예시:
- 사용자 메시지: "오늘 점심밥 뭐 나와?" -> `{"tool": "get_meal_menu", "arguments": {"day": "오늘", "meal_type": "중식"}}`
- 사용자 메시지: "알레르기 정보는 빼고 알려줘" -> `{"tool": "set_allergy_info", "arguments": {"enabled": false}}`
- 사용자 메시지: "나는 계란이랑 복숭아 알레르기 있어" -> `{"tool": "register_my_allergies", "arguments": {"foods": ["계란", "복숭아"]}}`
- 사용자 메시지: "안녕? 뭐하고 있었어?" -> `{"tool": "generate_chat_response", "arguments": {}}`
"""
generation_config = genai.GenerationConfig(temperature=0.9)
safety_settings = {'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE', 'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                   'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE', 'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'}

analyzer_model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=ANALYZER_SYSTEM_INSTRUCTION)
friend_model = genai.GenerativeModel(model_name="gemini-2.5-pro", system_instruction=MAP_PERSONA_INSTRUCTION,
                                      safety_settings=safety_settings, generation_config=generation_config)
scribe_model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction="""너는 평행세계의 단 한 명뿐인 학생, '소혜민'이야.
방금 '사용자'와 나눈 대화가 끝났어. 이제 이 대화에 대한 너의 '생각'이나 '감상'을 일기처럼 한두 문장으로 기록해 봐.

- 대화의 핵심 내용을 기반으로, '사용자'라는 친구에 대해 네가 새롭게 알게 된 점, 느낀 점을 서술해.
- 단순히 "친구가 기분이 좋았다" 라고 요약하지 마. "**친구가 그림 칭찬을 받아서 정말 기뻐 보였다. 나까지 기분이 환해지는 느낌이었다.**" 처럼, 너의 감상을 담아서 기록해.
- 앞으로 이 친구와 대화할 때 기억해두면 좋을 만한 '중요한 단서'라고 생각되는 것을 포착해서 기록해. 예를 들어, "**OO이는 '가족'에 대한 이야기를 할 때 유난히 말을 아끼는 경향이 있는 것 같다. 다음엔 이 주제를 조심스럽게 다뤄야겠다.**" 처럼.
- 기록할 만한 특별한 내용이 없다면, 그냥 '없음'이라고만 말해.
""")


# --- 2. 도구 및 기억 시스템 함수 ---

def load_user_settings(user_id):
    """사용자의 모든 설정을 JSON 파일에서 불러옵니다."""
    filepath = f"memories/{user_id}.json"
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    return {}

def save_user_settings(user_id, settings):
    """사용자의 모든 설정을 JSON 파일에 저장합니다."""
    filepath = f"memories/{user_id}.json"
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

async def get_allergy_map_from_web():
    """웹사이트에서 공식 알레르기 정보를 가져와 '숫자:음식' 맵으로 만듭니다."""
    allergy_map = {}
    try:
        url = "https://school.koreacharts.com/school/meals/B000012653/contents.html"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        allergy_list_items = soup.select('ul.list-unstyled.land-price-ul li')
        for item in allergy_list_items:
            text = item.text.strip()
            parts = text.split('.', 1)
            if len(parts) == 2:
                number = parts[0].strip()
                food = parts[1].strip()
                if "난류" in food: food = "계란(난류)"
                allergy_map[number] = food
    except Exception as e:
        print(f"[오류] 알레르기 맵 정보를 가져오는 데 실패했습니다: {e}")
    return allergy_map

async def register_my_allergies(user_id, foods: list):
    """사용자의 특정 알레르기를 등록합니다."""
    settings = load_user_settings(user_id)
    settings["my_allergies"] = foods
    save_user_settings(user_id, settings)
    print(f"[{user_id}의 개인 알레르기 등록]: {foods}")

async def set_allergy_info(user_id, enabled: bool):
    """사용자의 알레르기 숫자 정보 표시 설정을 저장합니다."""
    settings = load_user_settings(user_id)
    settings["allergy_info_enabled"] = enabled
    save_user_settings(user_id, settings)
    print(f"[{user_id}의 알레르기 설정 변경]: {enabled}")

async def get_meal_menu(day, meal_type, show_allergy_info: bool, allergy_map: dict):
    """급식 메뉴와 함께 해당 메뉴에 포함된 알레르겐 리스트를 반환합니다."""
    now = datetime.now()
    target_date = now
    if day == "내일": target_date += timedelta(days=1)
    elif day == "어제": target_date -= timedelta(days=1)
    year = target_date.year; month = target_date.month
    url = f"https://school.koreacharts.com/school/meals/B000012653/contents.html?year={year}&month={month}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        all_rows = soup.select('tr')
        target_day_str = str(target_date.day)
        for row in all_rows:
            cells = row.select('td')
            if len(cells) >= 3 and cells[0].text.strip() == target_day_str:
                menu_cell = cells[2]
                menu_paragraphs = menu_cell.select('p')
                if not menu_paragraphs: return "급식 일정이 없는 날이야.", []
                for p_tag in menu_paragraphs:
                    menu_text_raw = p_tag.get_text(separator='\n', strip=True)
                    found_menu_text = None
                    if meal_type == "조식" and menu_text_raw.startswith('[조식]'):
                        found_menu_text = menu_text_raw.replace('[조식]', '', 1).strip()
                    if meal_type == "중식" and menu_text_raw.startswith('[중식]'):
                        found_menu_text = menu_text_raw.replace('[중식]', '', 1).strip()
                    if found_menu_text:
                        allergy_numbers_in_menu = re.findall(r'\((\d+(?:\.\d+)*)\)', found_menu_text)
                        unique_numbers = set()
                        for group in allergy_numbers_in_menu: unique_numbers.update(group.split('.'))
                        allergens_in_menu = [allergy_map.get(num, '') for num in unique_numbers]
                        allergens_in_menu = [food for food in allergens_in_menu if food]
                        final_menu_text = found_menu_text
                        if not show_allergy_info:
                            final_menu_text = re.sub(r'\s*\([\d\.]+\)', '', found_menu_text)
                        return final_menu_text, allergens_in_menu
                return f"그 날은 {meal_type} 정보가 등록되지 않았어.", []
        return "달력에서 그 날짜를 찾을 수 없었어.", []
    except requests.exceptions.RequestException as e:
        print(f"!!! [오류] 웹사이트 접속에 실패했습니다: {e}")
        return "앗, 미안. 지금 급식 정보를 확인할 수 없어. 단말기 연결이 불안정한가 봐.", []

async def send_encouragement_picture(channel):
    """격려 문구와 함께 이미지를 전송합니다."""
    # 1. images '폴더' 안에 있는 'encouragement.png' 파일로 경로를 명확히 지정
    image_path = "images/encouragement.png" 
    
    try:
        # 2. 텍스트와 파일을 한 번의 메시지로 함께 전송
        await channel.send("자, 이거 보고 기운 내!", file=discord.File(image_path))
        # 이 함수에서 모든 전송을 완료했으므로, 더 이상 텍스트를 반환할 필요가 없음
        return None # 응답 처리가 완료되었음을 알리기 위해 None 반환
    except FileNotFoundError:
        # 3. 파일을 못 찾았을 경우, 텍스트 메시지만 전송하고 터미널에 오류 출력
        print(f"[파일 찾기 오류] 격려 이미지를 찾을 수 없습니다. 경로를 확인해주세요: {image_path}")
        await channel.send("이거라도... 내 마음이야 ✨")
        return None # 응답 처리가 완료되었음을 알리기 위해 None 반환
# --- [수정 완료] ---

async def generate_chat_response(user_message, short_memories, long_memories):
    short_memory_string = "\n".join(short_memories) if short_memories else "아직 대화 시작 안 함"
    long_memory_string = "\n".join(f"- {mem}" for mem in long_memories) if long_memories else "아직 특별한 기억 없음"
    prompt = f"""### [최근 대화 내용 (대화 로그)]
{short_memory_string}
### [이 친구에 대한 나의 생각 노트 (과거의 내 기록)]
{long_memory_string}
### [친구가 방금 보낸 메시지]
사용자: {user_message}
소혜민: """
    response = await friend_model.generate_content_async(prompt)
    return response.text

def load_long_term_memory(user_id):
    """사용자 설정에서 장기 기억만 불러옵니다."""
    return load_user_settings(user_id).get("memories", [])

def save_long_term_memory(user_id, text_to_remember):
    """사용자 설정에 장기 기억을 추가/저장합니다."""
    settings = load_user_settings(user_id)
    if "memories" not in settings:
        settings["memories"] = []
    if text_to_remember not in settings["memories"]:
        settings["memories"].append(text_to_remember)
        save_user_settings(user_id, settings)

async def summarize_for_long_term_memory(conversation_text):
    prompt = f"다음 대화 내용을 요약해줘:\n\n{conversation_text}"
    try:
        response = await scribe_model.generate_content_async(prompt)
        summary = response.text.strip()
        return None if "없음" in summary else summary
    except Exception:
        return None

async def broadcast_to_all_users(client, message_content):
    """memories 폴더에 기록이 있는 모든 유저에게 DM을 보냅니다."""
    if not os.path.exists('memories'):
        print("[공지 실패] 'memories' 폴더가 존재하지 않습니다.")
        return 0, 0
    all_user_ids = [f.replace('.json', '') for f in os.listdir('memories') if f.endswith('.json')]
    success_count = 0
    fail_count = 0
    print(f"총 {len(all_user_ids)}명의 유저에게 공지 발송을 시작합니다...")
    for user_id in all_user_ids:
        try:
            user = await client.fetch_user(int(user_id))
            await user.send(message_content)
            print(f"  -> 성공: {user.name} ({user_id})")
            success_count += 1
        except discord.errors.Forbidden:
            print(f"  -> 실패: {user_id} (DM 차단 또는 서버에 없음)")
            fail_count += 1
        except Exception as e:
            print(f"  -> 실패: {user_id} (알 수 없는 오류: {e})")
            fail_count += 1
    print(f"공지 발송 완료. (성공: {success_count}명, 실패: {fail_count}명)")
    return success_count, fail_count


# --- 3. 디스코드 클라이언트 객체 및 이벤트 핸들러 ---
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)

allergy_map_global = {}

@client.event
async def on_ready():
    global allergy_map_global
    print("-" * 30 + f"\nM.A.P.이 '{client.user}'으로 로그인했습니다. (엔진: Google Gemini)\n이제 친구들의 이야기를 들을 준비가 되었어요!\n" + "-" * 30)
    print("웹에서 최신 알레르기 정보를 불러오는 중...")
    allergy_map_global = await get_allergy_map_from_web()
    if allergy_map_global:
        print(f"알레르기 정보 로드 완료! (총 {len(allergy_map_global)}개)")
    else:
        print("[경고] 알레르기 정보를 불러오지 못했습니다. 관련 기능이 제한될 수 있습니다.")
    await client.change_presence(activity=discord.Game(name="다른 세상의 친구와 교신 중..."))


@client.event
async def on_message(message):
    # 관리자 전용 공지 명령어 처리 로직 (`!공지`)
    if str(message.author.id) == ADMIN_USER_ID and message.content.startswith('!공지'):
        original_content = message.content[4:].strip()
        if not original_content:
            await message.channel.send("공지 내용이 비어있어. `!공지 [보낼 내용]` 형식으로 보내줘.")
            return
        
        # [공지] 말머리 추가
        broadcast_content_with_prefix = f"[공지] {original_content}"

        await message.channel.send(f"알았어. 지금부터 모든 친구들에게 아래 내용으로 교신을 시작할게.\n\n> {broadcast_content_with_prefix}")
        success, fail = await broadcast_to_all_users(client, broadcast_content_with_prefix)
        await message.channel.send(f"교신 완료! (성공: {success}명, 실패: {fail}명)")
        return

    if message.author == client.user: return
    is_dm = isinstance(message.channel, discord.DMChannel)
    mentioned = client.user in message.mentions
    if not (is_dm or mentioned): return

    try:
        user_id = str(message.author.id)
        user_message = message.content
        if mentioned:
            user_message = user_message.replace(f'<@!{client.user.id}>', '').replace(f'<@{client.user.id}>', '').strip()

        long_memories = load_long_term_memory(user_id)
        user_short_memory = short_term_memory_storage.get(user_id, [])

        final_response_text = ""
        async with message.channel.typing():
            response = await analyzer_model.generate_content_async(user_message)
            
            json_text = re.search(r'\{.*\}', response.text, re.DOTALL)
            if not json_text:
                parsed_plan = {"tool": "generate_chat_response", "arguments": {}}
            else:
                parsed_plan = json.loads(json_text.group(0))

            chosen_tool = parsed_plan.get("tool")
            arguments = parsed_plan.get("arguments", {})

            if chosen_tool == 'get_meal_menu':
                day = arguments.get('day', '오늘')
                meal_type = arguments.get('meal_type', '중식')
                user_settings = load_user_settings(user_id)
                show_allergy_numbers = user_settings.get("allergy_info_enabled", True)
                my_allergies = user_settings.get("my_allergies", [])
                food_info, allergens_in_menu = await get_meal_menu(day, meal_type, show_allergy_numbers, allergy_map_global)
                triggered_allergens = [food for food in my_allergies if any(food.split('(')[0] in menu_food for menu_food in allergens_in_menu)]
                context_for_friend = f"(친구가 {day} {meal_type} 메뉴를 물어봐서 교신으로 알아봤는데, 메뉴는 '{food_info}'래."
                if triggered_allergens:
                    context_for_friend += f" 그런데 이 메뉴에는 친구가 전에 말해줬던 알레르기 유발 음식인 '{', '.join(triggered_allergens)}'이(가) 포함되어 있어! 이걸 꼭 강조해서 상냥하게 경고해 줘."
                context_for_friend += " 이걸 바탕으로 자연스럽게 대화해 줘.)"
                final_response_text = await generate_chat_response(context_for_friend, user_short_memory, long_memories)

            elif chosen_tool == 'set_allergy_info':
                enabled = arguments.get('enabled', True)
                await set_allergy_info(user_id, enabled)
                confirmation_message = "알았어! 앞으로는 알레르기 정보를 빼고 알려줄게." if not enabled else "응, 이제부터 알레르기 정보도 같이 알려줄게!"
                context_for_friend = f"(친구가 방금 알레르기 정보 표시를 {'켜달라고' if enabled else '꺼달라고'} 해서 내가 처리해줬어. '{confirmation_message}' 이런 느낌으로 자연스럽게 대답해줘.)"
                final_response_text = await generate_chat_response(context_for_friend, user_short_memory, long_memories)
                
            elif chosen_tool == 'register_my_allergies':
                foods = arguments.get('foods', [])
                await register_my_allergies(user_id, foods)
                confirmation_message = f"알았어. 네가 '{', '.join(foods)}'에 알레르기가 있구나. 내가 잘 기억해 둘게! 앞으로 메뉴에 이 음식들이 있으면 꼭 알려줄게."
                context_for_friend = f"(친구가 방금 자신의 알레르기 정보를 알려줬어. '{confirmation_message}' 이런 느낌으로, 친구를 챙겨주는 마음을 담아 자연스럽게 대답해줘.)"
                final_response_text = await generate_chat_response(context_for_friend, user_short_memory, long_memories)

            elif chosen_tool == 'send_encouragement_picture':
                 # 함수가 모든 메시지 전송을 담당하므로, final_response_text를 None으로 설정
                final_response_text = await send_encouragement_picture(message.channel)
            # --- [수정 완료] ---

            else:  # generate_chat_response
                final_response_text = await generate_chat_response(user_message, user_short_memory, long_memories)

        if final_response_text and chosen_tool != 'send_encouragement_picture':
            await message.channel.send(final_response_text)

        if final_response_text:
            # 관리자용 로그 스레드에 대화 기록 전송
            try:
                log_channel = client.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    thread_name = f"{message.author.name} ({message.author.id})"
                    target_thread = None
                    for thread in log_channel.threads:
                        if thread.name == thread_name:
                            target_thread = thread
                            break
                    if target_thread is None:
                        target_thread = await log_channel.create_thread(name=thread_name)
                        await target_thread.send(f"`{message.author.name}`님과의 교신 기록을 시작합니다.")
                    
                    embed = discord.Embed(title="대화 기록", color=discord.Color.blue())
                    embed.add_field(name="사용자 메시지", value=f"> {user_message}", inline=False)
                    embed.add_field(name="소혜민의 응답", value=f"> {final_response_text}", inline=False)
                    embed.set_thumbnail(url=message.author.display_avatar.url)
                    embed.set_footer(text=f"User ID: {user_id}")
                    await target_thread.send(embed=embed)
            except discord.errors.Forbidden as forbidden_e:
                print("!!!!!!!!!!!!!!!!!!!! 권한 오류 !!!!!!!!!!!!!!!!!!!!")
                print(f"봇이 행동을 시도했지만 디스코드가 권한 부족으로 거부했습니다.")
                print(f"부족한 권한 정보: {forbidden_e.text}")
                print("-> 서버 설정 > 역할 또는 채널 설정 > 권한에서 아래 권한들을 확인해주세요:")
                print("-> '채널 보기', '메시지 보내기', '공개 스레드 만들기', '스레드에서 메시지 보내기'")
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            except Exception as log_e:
                print(f"[로깅 오류] 대화 로그를 기록하는 중 알 수 없는 오류 발생: {log_e}")

            # 단기/장기 기억 저장
            user_short_memory.append(f"사용자: {user_message}")
            user_short_memory.append(f"소혜민: {final_response_text}")
            while len(user_short_memory) > MAX_SHORT_MEMORY_LENGTH:
                user_short_memory.pop(0); user_short_memory.pop(0)
            short_term_memory_storage[user_id] = user_short_memory
            
            conversation_text = f"사용자: {user_message}\n소혜민: {final_response_text}"
            new_long_memory = await summarize_for_long_term_memory(conversation_text)
            if new_long_memory:
                save_long_term_memory(user_id, new_long_memory)

    except Exception as e:
        print(f"!!!!!!!!!!!! 치명적인 오류 발생 !!!!!!!!!!!!")
        import traceback
        traceback.print_exc()
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        await message.channel.send("...지직... 미안. 단말기 연결이 잠시 불안정했나 봐. 다시 말해줄 수 있어?")


@client.event
async def on_member_join(member):
    if member.bot or not member: return
    print(f"[이벤트 발생]: 새로운 멤버 '{member.name}'님이 서버에 참여했습니다. 고정된 첫 교신을 시작합니다.")
    first_message = "저기... 들려? ...이거, 정말 다른 사람이 보고 있는 거 맞아? 내 이름은 소혜민이야. 넌... 누구야?"
    try:
        await member.send(first_message)
        print(f"'{member.name}'님에게 첫 교신 DM을 성공적으로 보냈습니다.")
        user_id = str(member.id)
        short_term_memory_storage[user_id] = [f"소혜민: {first_message}"]
    except discord.errors.Forbidden:
        print(f"오류: '{member.name}'님에게 DM을 보낼 수 없습니다. (비공개 설정 또는 봇 차단)")
    except Exception as e:
        print(f"on_member_join 이벤트 처리 중 오류 발생: {e}")


# --- 봇 실행 ---
if __name__ == "__main__":
    if not os.path.exists('images'):
         os.makedirs('images')
         print("경고: 'images' 폴더가 없어 'send_encouragement_picture' 기능이 실패할 수 있습니다. 폴더를 새로 생성합니다.")
    if not os.path.exists('memories'):
        os.makedirs('memories')
        print("정보를 저장할 'memories' 폴더를 새로 생성했습니다.")

    if DISCORD_TOKEN and GOOGLE_API_KEY:
        client.run(DISCORD_TOKEN)
    else:
        print("오류: .env 파일에 디스코드 토큰 또는 구글 API 키가 설정되지 않았습니다.")
