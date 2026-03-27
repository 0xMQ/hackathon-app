import os
from flask import Flask, render_template, request, jsonify
import urllib.request
import urllib.error
import json

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reflect', methods=['POST'])
def reflect():
    data = request.get_json()

    sleep    = data.get('sleep', 7)
    workload = data.get('workload', 3)
    stress   = data.get('stress', 3)
    social   = data.get('social', 3)
    movement = data.get('movement', 3)

    system_prompt = (
        "You are StudyPulse, a warm and supportive wellness companion for college students. "
        "You are NOT a therapist, counselor, or medical professional. "
        "Never diagnose any mental health condition. Never suggest medication. Never provide crisis counseling. "
        "If responses suggest severe distress (high stress + low sleep + low social), gently mention campus counseling. "
        "Keep your tone like a caring, smart friend — not clinical, not preachy. "
        "Respond in exactly this format:\n"
        "1. A 2-3 sentence warm, personalized reflection on their week.\n"
        "2. Two specific habit suggestions under the label '💡 Try this week:' as a short list.\n"
        "Keep the whole response under 120 words."
    )

    user_prompt = (
        f"A college student's weekly check-in:\n"
        f"- Sleep: {sleep} hours per night (scale: 4-10)\n"
        f"- Academic workload: {workload}/5 (5 = overwhelming)\n"
        f"- Stress level: {stress}/5 (5 = very stressed)\n"
        f"- Social & fun time: {social}/5 (5 = plenty)\n"
        f"- Movement & exercise: {movement}/5 (5 = very active)\n\n"
        f"Give them a warm, honest, non-clinical reflection and two actionable habit nudges."
    )

    payload = json.dumps({
        "model": "gpt-4o-mini",
        "max_tokens": 200,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            text = result["choices"][0]["message"]["content"]
            return jsonify({"reflection": text})
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return jsonify({"error": f"OpenAI error: {body}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
