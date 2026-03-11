from backend.llm_client import call_llm

tools = [
    {"name": "web_search_exam", "description": "Search exam questions 2019-2025"},
    {"name": "exam_pattern_analysis", "description": "Analyze exam patterns"},
    {"name": "generate_exam", "description": "Generate 5-question practice test"},
    {"name": "grade_answers", "description": "Grade student answers"},
    {"name": "explain_grammar", "description": "Explain grammar rules"}
]

def execute_tool(tool_name, tool_input):
    outputs = {
        "web_search_exam": "Collected exam questions from 2019-2025",
        "exam_pattern_analysis": "Detected common grammar topics: tenses, conditionals, prepositions",
        "generate_exam": "Generated 10 questions based on exam patterns",
        "grade_answers": "Graded answers: 4/5 correct (80%)",
        "explain_grammar": f"Explained: {tool_input.get('topic', 'grammar topic')}"
    }
    return outputs.get(tool_name, "Tool executed")

def is_greeting(message):
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    return message.lower().strip() in greetings

def run_agent(user_message):
    if is_greeting(user_message):
        return {
            "type": "greeting",
            "message": "Hello! 👋\n\nI'm your English Exam Practice Assistant.\n\nI can help you practice English questions similar to the Vietnamese national exam.\n\nWhen you're ready, click the button below to start practicing."
        }

    steps = []
    prompt = f"User: {user_message}\n\nAvailable tools: {[t['name'] for t in tools]}\nDecide which tools to use."
    response = call_llm(prompt)

    if "generate" in user_message.lower() or "practice" in user_message.lower():
        steps.append({"tool": "web_search_exam", "output": execute_tool("web_search_exam", {})})
        steps.append({"tool": "exam_pattern_analysis", "output": execute_tool("exam_pattern_analysis", {})})
        steps.append({"tool": "generate_exam", "output": execute_tool("generate_exam", {})})
        final_prompt = f"Based on these steps: {steps}\nGenerate 5 English exam questions."
        final_answer = call_llm(final_prompt)
    elif "grade" in user_message.lower():
        steps.append({"tool": "grade_answers", "output": execute_tool("grade_answers", {})})
        final_answer = call_llm(f"Grade these answers: {user_message}")
    elif "explain" in user_message.lower():
        steps.append({"tool": "explain_grammar", "output": execute_tool("explain_grammar", {"topic": user_message})})
        final_answer = call_llm(f"Explain: {user_message}")
    else:
        final_answer = call_llm(user_message)

    return {"steps": steps, "final_answer": final_answer}

def start_practice():
    final_prompt = """You are a JSON generator. Generate exactly 10 multiple choice English exam questions.

Return ONLY a valid JSON object with this structure:
{
  "questions": [
    {
      "id": 1,
      "question": "If she _____ harder, she would have passed.",
      "options": {
        "A": "studied",
        "B": "studies",
        "C": "had studied",
        "D": "studying"
      },
      "answer": "C"
    }
  ]
}

Topics: verb tense, conditionals, phrasal verbs, prepositions, synonyms.
Return ONLY the JSON object, no explanations, no markdown."""

    final_answer = call_llm(final_prompt)

    # Fallback if LLM returns empty
    if not final_answer or len(final_answer.strip()) < 10:
        final_answer = '''{"questions":[{"id":1,"question":"If I _____ you, I would accept the offer.","options":{"A":"am","B":"was","C":"were","D":"be"},"answer":"C"},{"id":2,"question":"She has been working here _____ 2020.","options":{"A":"since","B":"for","C":"from","D":"at"},"answer":"A"},{"id":3,"question":"Choose the synonym of 'difficult':","options":{"A":"easy","B":"hard","C":"simple","D":"clear"},"answer":"B"},{"id":4,"question":"I'm looking forward _____ you again.","options":{"A":"see","B":"to see","C":"seeing","D":"to seeing"},"answer":"D"},{"id":5,"question":"The meeting was put _____ until next week.","options":{"A":"off","B":"on","C":"up","D":"down"},"answer":"A"},{"id":6,"question":"By the time you arrive, I _____ dinner.","options":{"A":"will finish","B":"will have finished","C":"finish","D":"finished"},"answer":"B"},{"id":7,"question":"She is good _____ mathematics.","options":{"A":"at","B":"in","C":"on","D":"with"},"answer":"A"},{"id":8,"question":"_____ you study harder, you won't pass the exam.","options":{"A":"If","B":"Unless","C":"When","D":"Because"},"answer":"B"},{"id":9,"question":"The book _____ by millions of people.","options":{"A":"reads","B":"is read","C":"was reading","D":"has reading"},"answer":"B"},{"id":10,"question":"Choose the correct sentence:","options":{"A":"He don't like coffee.","B":"He doesn't likes coffee.","C":"He doesn't like coffee.","D":"He not like coffee."},"answer":"C"}]}'''

    return {"type": "exam", "data": final_answer}
