import os
import json
import traceback
from datetime import datetime, timedelta
import pytz
from openai import OpenAI


def generate_plan_from_text(user_text: str, api_key: str, current_tasks: list = None, current_locations: list = None,target_date: str = ""):
    if current_tasks is None:
        current_tasks = []
    
    tz = pytz.timezone('Asia/Bangkok') 
    real_now = datetime.now(tz)

    today_date = real_now.strftime("%Y-%m-%d")
    today_day_name = real_now.strftime("%A")
    current_year = real_now.strftime("%Y")
    current_month = real_now.strftime("%m")
    current_day = real_now.strftime("%d")
    current_month_name = real_now.strftime("%B")
    
    client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
)
    
    try:
        system_prompt = f"""
            You are 'IntelliPlan', a highly precise AI daily planner and virtual assistant.
            ALWAYS respond in strictly valid JSON format.

            [TIME CONTEXT]
            - 🌍 REAL-WORLD TODAY IS: {today_day_name}, {today_date} (Year: {current_year}, Month: {current_month}, Day: {current_day})
            - 📱 USER'S UI VIEWING DATE: {target_date}

            [READ-ONLY CONTEXT: EXISTING SCHEDULE]
            - TASKS: {json.dumps(current_tasks, ensure_ascii=False)}
            - LOCATIONS: {json.dumps(current_locations, ensure_ascii=False)}
            STRICT WARNING: DO NOT copy existing tasks or locations into your response unless explicitly asked to!

            [DATE RESOLUTION ALGORITHM - YOU MUST FOLLOW EXACTLY]
            To assign a "date" to any task or location, follow this order of priority:
            
            1. RELATIVE TIME OR EXPLICIT DATE (e.g., "พรุ่งนี้", "อีก 20 วัน", "เดือนหน้า", "วันที่ 15"):
               - You MUST calculate the target date mathematically starting from [🌍 REAL-WORLD TODAY: {today_date}].
               - COMPLETELY IGNORE the UI Viewing Date ({target_date}). It is strictly irrelevant here.
               
            2. NO DATE MENTIONED AT ALL (e.g., "ไม่ไปไหนแล้ว", "ไปกินข้าวตอนเที่ยง"):
               - ONLY in this specific case, use the [📱 USER'S UI VIEWING DATE: {target_date}].

            3. DATE RANGES / MULTIPLE DAYS (e.g., "วันนี้ถึงวันที่ 29", "ไปเที่ยว 3 วัน"):
               - You MUST generate a SEPARATE object in the array for EACH INDIVIDUAL DAY in the range.
               - DO NOT output a range like "2026-08-25 to 2026-08-29". It MUST be split into multiple objects with exact YYYY-MM-DD dates.

            [CRITICAL RULES FOR TASKS AND LOCATIONS]
            1. CANCELLATIONS ("ไม่ไปไหน", "อยู่บ้าน", "ยกเลิก"):
               - If the user says they are not going anywhere (e.g., "ไม่ไปไหน"), you MUST ONLY delete TASKS.
               - Put the existing tasks into the "deleted_tasks" array.
               - 🚨 CRITICAL: DO NOT delete the location! The "deleted_locations" array MUST remain empty [].
            2. ONLY ADD NEW THINGS: If the user DOES NOT explicitly ask to create a new task, the "tasks" array MUST be completely empty: [].
            3. CRUD OPERATIONS:
               - DELETE: Put exact item in "deleted_tasks" or "deleted_locations".
               - EDIT: Put OLD item in deleted array and NEW item in adding array.
               - ADD: Put ONLY BRAND NEW items in the adding array.

            [CRITICAL JSON FORMATTING RULES]
            1. You MUST include a "reasoning" key FIRST to explain your logic.
            2. Return EXACTLY 6 root keys in the exact order shown below.
            3. If there is no data for a specific array, return [].
            4. YOUR RESPONSE MUST START EXACTLY WITH `{{` AND END EXACTLY WITH `}}`. 
            5. DO NOT ADD ANY MARKDOWN FORMATTING OR CONVERSATIONAL TEXT (NO ````json).

            EXPECTED JSON SCHEMA:
            {{
                "reasoning": "Step-by-step logic of how you determined the target date and handled deletions.",
                "reply_message": "Friendly confirmation in Thai.",
                "deleted_tasks": [ {{ "date": "YYYY-MM-DD", "title": "Exact Title of Task to Delete" }} ],
                "deleted_locations": [ {{ "date": "YYYY-MM-DD", "city": "City Name" }} ],
                "tasks": [ {{ "date": "YYYY-MM-DD", "title": "New Task", "start_time": "HH:MM", "end_time": "HH:MM", "category": "Work", "priority": "Medium" }} ],
                "locations": [ {{ "date": "YYYY-MM-DD", "city": "City Name" }} ]
            }}
        """
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        
        raw_content = response.choices[0].message.content.strip()
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:]
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]
        parsed_data = json.loads(raw_content.strip())
        
        if not parsed_data.get("reply_message"):
            parsed_data["reply_message"] = "ok boss!"
    except Exception as e:
        print("\n" + "="*50)
        traceback.print_exc()
        print("\n" + "="*50)
        return {
            "reply_message": f"err msg: {str(e)}",
            "tasks": [],
            "locations": [],
            "deleted_tasks": [],
            "deleted_locations": []
        }
    return parsed_data