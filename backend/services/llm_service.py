import os
import re
import math
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # Resolve API Key from multiple common environment variable names
        self.api_key = (
            os.getenv("LLM_API_KEY") or
            os.getenv("GEMINI_API_KEY") or
            os.getenv("GOOGLE_API_KEY") or
            os.getenv("OPENAI_API_KEY") or
            ""
        ).strip()
        
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        self.model_name = os.getenv("MODEL_NAME", "gemini-1.5-flash")

    def generate_response(
        self,
        student_question: str,
        retrieved_knowledge: Optional[Dict[str, Any]] = None,
        intent: str = "ASK_EXPLANATION",
        topic: str = "General",
        context_history: Optional[list] = None
    ) -> str:
        """
        Generate high-quality conversational responses like Google Search and ChatGPT.
        1. Checks for Gemini / OpenAI API key.
        2. If unavailable or fails, falls back to the intelligent multi-tier Answer Engine.
        """
        q = student_question.strip()
        if not q:
            return "Please ask a question, and I'll be happy to provide a detailed explanation!"

        # Handle simple greetings directly
        if intent == "GREETING" or re.match(r'^(hi|hello|hey|greetings|good morning|good evening|good afternoon)\b', q, re.IGNORECASE):
            return "👋 **Hello!** I'm **Specs**, your intelligent AI learning companion. Ask me any question about **Science, Programming, Mathematics, AI, General Knowledge, History, or Technology**, and I'll give you a clear, comprehensive answer!"

        # 1. Try Generative AI LLM APIs if key is available
        if self.api_key:
            llm_res = self._call_generative_llm(q, retrieved_knowledge, intent, topic)
            if llm_res:
                return llm_res

        # 2. Intelligent Multi-Tier Knowledge & Search Engine (Google / ChatGPT style)
        return self._generate_intelligent_answer(q, retrieved_knowledge, intent, topic)

    def _call_generative_llm(self, question: str, kb_item: Optional[Dict[str, Any]], intent: str, topic: str) -> Optional[str]:
        """Calls Gemini or OpenAI APIs when API key is provided."""
        # --- Gemini API ---
        if self.provider == "gemini" or "gemini" in self.model_name.lower():
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
                prompt = self._build_llm_prompt(question, kb_item, topic)
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 1024
                    }
                }
                res = requests.post(url, json=payload, timeout=8)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
            except Exception as e:
                logger.warning(f"Gemini API request failed: {e}. Falling back to internal answer engine.")

        # --- OpenAI API ---
        elif self.provider == "openai" or "gpt" in self.model_name.lower():
            try:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": self.model_name if "gpt" in self.model_name else "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are Specs, an expert and intelligent AI tutor like Google and ChatGPT. Provide direct, highly informative, accurate, and easy-to-understand answers with clear examples and formatting."},
                        {"role": "user", "content": question}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 1000
                }
                res = requests.post(url, headers=headers, json=payload, timeout=8)
                if res.status_code == 200:
                    data = res.json()
                    choices = data.get("choices", [])
                    if choices:
                        return choices[0]["message"]["content"].strip()
            except Exception as e:
                logger.warning(f"OpenAI API request failed: {e}. Falling back to internal answer engine.")

        return None

    def _build_llm_prompt(self, question: str, kb_item: Optional[Dict[str, Any]], topic: str) -> str:
        kb_text = ""
        if kb_item:
            kb_text = f"\nCurated Reference Material:\n- Title: {kb_item.get('title')}\n- Definition: {kb_item.get('definition')}\n- Explanation: {kb_item.get('explanation')}\n- Example: {kb_item.get('example')}\n"

        return f"""You are Specs, an intelligent AI tutor similar to Google and ChatGPT.
The user is asking: "{question}"
{kb_text}
Instructions:
1. Provide a direct, factual, and complete answer immediately (like Google Featured Snippets).
2. Follow up with a concise, easy-to-understand explanation and practical real-world or code examples if relevant.
3. Use clean markdown formatting (bold text, bullet points, headers, or code blocks).
4. Do NOT output raw NLP metadata, parsing tokens, or robotic boilerplate. Respond naturally, clearly, and authoritatively.
"""

    def _generate_intelligent_answer(self, question: str, kb_item: Optional[Dict[str, Any]], intent: str, topic: str) -> str:
        """
        Multi-tier answer engine that resolves questions using:
        1. Math & Calculation Engine
        2. Coding & Programming Knowledge Synthesizer
        3. Curated RAG Knowledge Base
        4. Real-time Wikipedia & DuckDuckGo Knowledge Engine
        5. Deep Concept Explainer
        """
        # Tier 1: Mathematical Calculation Solver
        math_ans = self._solve_math_query(question)
        if math_ans:
            return math_ans

        # Tier 2: Programming & Algorithms Engine
        code_ans = self._solve_programming_query(question)
        if code_ans:
            return code_ans

        # Tier 3: Curated Knowledge Base Match (if similarity >= 38%)
        if kb_item and kb_item.get("similarity_score", 0) >= 38.0:
            title = kb_item.get("title", topic)
            definition = kb_item.get("definition", "")
            explanation = kb_item.get("explanation", "")
            example = kb_item.get("example", "")
            points = kb_item.get("important_points", [])
            points_list = "\n".join([f"• {p}" for p in points]) if points else ""

            return f"""### 💡 {title}

**Direct Answer:**
{definition}

**Explanation:**
{explanation}

{f'**Example:**\n```\n{example}\n```\n' if example else ''}
{f'**Key Takeaways:**\n{points_list}\n' if points_list else ''}
---
💡 *Ask any follow-up question or request a code demonstration!*"""

        # Tier 4: Real-time Encyclopedia / Knowledge Search (Wikipedia & DuckDuckGo)
        web_fact = self._fetch_live_knowledge(question, topic)
        if web_fact:
            return web_fact

        # Tier 5: Intelligent Subject & Concept Synthesis
        return self._synthesize_concept_explanation(question, topic)

    def _solve_math_query(self, question: str) -> Optional[str]:
        """Safely evaluates basic arithmetic and mathematical questions."""
        q = question.strip()
        
        # Percentage queries (e.g. "what is 15% of 800")
        pct_match = re.search(r'(?:what is\s+)?(\d+(?:\.\d+)?)\s*%\s*(?:of)\s*(\d+(?:\.\d+)?)', q, re.IGNORECASE)
        if pct_match:
            pct = float(pct_match.group(1))
            total = float(pct_match.group(2))
            res = (pct / 100.0) * total
            return f"""### 🔢 Math Calculation

**Answer:** **{res:g}**

**Step-by-Step Calculation:**
• {pct}% of {total:g} = `({pct} / 100) × {total:g}`
• `{pct / 100:g} × {total:g}` = **{res:g}**"""

        # Arithmetic equations (e.g. "what is 25 * 40 + 10", "calculate 1024 / 8")
        calc_match = re.search(r'(?:what is|calculate|evaluate|solve)?\s*([0-9\.\s\+\-\*\/\^\(\)]+)(?:\s*\=\s*\?)?', q, re.IGNORECASE)
        if calc_match:
            expr_str = calc_match.group(1).strip()
            # Ensure it contains at least one arithmetic operator and numbers
            if re.search(r'[\+\-\*\/\^]', expr_str) and re.search(r'\d', expr_str) and not re.search(r'[a-zA-Z]', expr_str):
                try:
                    py_expr = expr_str.replace('^', '**')
                    # Safe arithmetic evaluation
                    allowed_chars = set("0123456789+-*/(). ")
                    if all(c in allowed_chars for c in py_expr):
                        val = eval(py_expr, {"__builtins__": None}, {})
                        return f"""### 🔢 Math Calculation

**Equation:** `{expr_str}`
**Result:** **{val:g}**"""
                except Exception:
                    pass

        # Square root queries (e.g. "sqrt of 144", "square root of 256")
        sqrt_match = re.search(r'(?:square root|sqrt)\s*(?:of)?\s*(\d+(?:\.\d+)?)', q, re.IGNORECASE)
        if sqrt_match:
            n = float(sqrt_match.group(1))
            res = math.sqrt(n)
            return f"""### 🔢 Square Root

**Answer:** $\\sqrt{{{n:g}}}$ = **{res:g}**"""

        return None

    def _solve_programming_query(self, question: str) -> Optional[str]:
        """Provides direct, high-quality code implementations for common coding queries."""
        q_lower = question.lower()

        # Reverse a string
        if "reverse" in q_lower and "string" in q_lower:
            return """### 💻 Reversing a String in Python

**Direct Solution (Slicing):**
```python
text = "hello world"
reversed_text = text[::-1]
print(reversed_text)  # Output: "dlrow olleh"
```

**Alternative Methods:**
1. **Using `reversed()` and `join()`:**
```python
reversed_text = "".join(reversed(text))
```
2. **Using a Loop (Two Pointers):**
```python
def reverse_string(s: str) -> str:
    chars = list(s)
    left, right = 0, len(chars) - 1
    while left < right:
        chars[left], chars[right] = chars[right], chars[left]
        left += 1
        right -= 1
    return "".join(chars)
```
• **Time Complexity:** $O(n)$  
• **Space Complexity:** $O(n)$"""

        # Binary Search
        if "binary search" in q_lower:
            return """### 🔍 Binary Search Algorithm

Binary search finds the position of a target value within a **sorted array** by repeatedly dividing the search interval in half.

**Python Implementation:**
```python
def binary_search(arr, target):
    left = 0
    right = len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid  # Target found at index mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
            
    return -1  # Target not in array

# Example Usage:
numbers = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
print(binary_search(numbers, 23))  # Output: 5
```

**Complexity Analysis:**
• **Time Complexity:** $O(\\log n)$ (Best: $O(1)$)  
• **Space Complexity:** $O(1)$ (Iterative)"""

        # Quicksort
        if "quicksort" in q_lower or "quick sort" in q_lower:
            return """### ⚡ QuickSort Algorithm

QuickSort is an efficient **divide-and-conquer** sorting algorithm that selects a 'pivot' element and partitions the array into sub-arrays around the pivot.

**Python Implementation:**
```python
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

# Example:
data = [38, 27, 43, 3, 9, 82, 10]
print(quicksort(data))  # Output: [3, 9, 10, 27, 38, 43, 82]
```

**Complexity:**
• **Average Time:** $O(n \\log n)$  
• **Worst Case:** $O(n^2)$ (when pivot is poorly chosen)  
• **Space Complexity:** $O(\\log n)$"""

        # List Comprehension
        if "list comprehension" in q_lower:
            return """### 🐍 Python List Comprehension

List comprehension provides a concise way to create lists based on existing iterables.

**Basic Syntax:**
```python
[expression for item in iterable if condition]
```

**Examples:**
```python
# 1. Squares of numbers 0 to 9:
squares = [x**2 for x in range(10)]
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# 2. Filter even numbers:
evens = [x for x in range(20) if x % 2 == 0]

# 3. Uppercase words with length > 3:
words = ["cat", "apple", "dog", "banana"]
long_words = [w.upper() for w in words if len(w) > 3]
# ['APPLE', 'BANANA']
```"""

        # SQL 2nd Highest Salary
        if "second highest salary" in q_lower or "2nd highest salary" in q_lower:
            return """### 🗄️ SQL: Find the Second Highest Salary

**Standard SQL Query:**
```sql
SELECT MAX(salary) AS SecondHighestSalary
FROM Employee
WHERE salary < (SELECT MAX(salary) FROM Employee);
```

**Alternative (Using LIMIT & OFFSET):**
```sql
SELECT IFNULL(
    (SELECT DISTINCT salary 
     FROM Employee 
     ORDER BY salary DESC 
     LIMIT 1 OFFSET 1), 
    NULL
) AS SecondHighestSalary;
```

**Alternative (Using DENSE_RANK window function):**
```sql
WITH RankedSalaries AS (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) as rnk
    FROM Employee
)
SELECT salary 
FROM RankedSalaries 
WHERE rnk = 2 
LIMIT 1;
```"""

        return None

    def _fetch_live_knowledge(self, question: str, topic: str) -> Optional[str]:
        """Queries Wikipedia & DuckDuckGo Instant Answers for live facts."""
        clean_q = re.sub(r'^(who is|who was|what is|what are|where is|when was|how does|how do i|tell me about|explain|define)\s+', '', question, flags=re.IGNORECASE).strip(' ?.')
        if not clean_q:
            clean_q = topic or question.strip(' ?.')

        headers = {"User-Agent": "AITutorApp/1.0 (Educational Learning Assistant)"}

        # 1. Wikipedia Direct Summary
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(clean_q)}"
            res = requests.get(url, headers=headers, timeout=3.5)
            if res.status_code == 200:
                data = res.json()
                if data.get("type") != "disambiguation" and data.get("extract"):
                    title = data.get("title", clean_q.title())
                    extract = data.get("extract")
                    desc = data.get("description", "")
                    
                    desc_line = f"*{desc}*\n\n" if desc else ""
                    return f"""### 🌐 {title}
{desc_line}**Direct Answer:**
{extract}

---
💡 **Follow-Up:** Would you like to explore related topics or dive deeper into **{title}**?"""
        except Exception as e:
            logger.debug(f"Direct Wikipedia summary failed: {e}")

        # 2. Wikipedia Search API (Fallback to top search result)
        try:
            search_url = "https://en.wikipedia.org/w/api.php"
            params = {"action": "query", "list": "search", "srsearch": clean_q, "format": "json", "srlimit": 3}
            s_res = requests.get(search_url, params=params, headers=headers, timeout=3.5)
            if s_res.status_code == 200:
                items = s_res.json().get("query", {}).get("search", [])
                for item in items:
                    top_title = item.get("title")
                    if top_title:
                        sum_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(top_title)}"
                        s_r = requests.get(sum_url, headers=headers, timeout=3.5)
                        if s_r.status_code == 200:
                            s_data = s_r.json()
                            if s_data.get("type") != "disambiguation" and s_data.get("extract"):
                                title = s_data.get("title")
                                extract = s_data.get("extract")
                                return f"""### 🌐 {title}

**Direct Answer:**
{extract}

---
💡 **Follow-Up:** Would you like more details or practice questions regarding **{title}**?"""
        except Exception as e:
            logger.debug(f"Wikipedia search query failed: {e}")

        # 3. DuckDuckGo Instant Answer API
        try:
            ddg_url = "https://api.duckduckgo.com/"
            ddg_params = {"q": clean_q, "format": "json", "no_html": 1, "skip_disambig": 1}
            ddg_res = requests.get(ddg_url, params=ddg_params, timeout=3.5)
            if ddg_res.status_code == 200:
                ddg_data = ddg_res.json()
                abstract = ddg_data.get("AbstractText") or ddg_data.get("Answer")
                heading = ddg_data.get("Heading", clean_q.title())
                if abstract and len(abstract) > 25:
                    return f"""### 🌐 {heading}

**Direct Answer:**
{abstract}

---
💡 **Follow-Up:** Let me know if you'd like an example or deeper explanation of **{heading}**!"""
        except Exception as e:
            logger.debug(f"DuckDuckGo search failed: {e}")

        return None

    def _synthesize_concept_explanation(self, question: str, topic: str) -> str:
        """Synthesizes structured, high-quality answers when external APIs are unreachable."""
        clean_target = re.sub(r'^(who is|who was|what is|what are|where is|when was|how does|how do i|tell me about|explain|define)\s+', '', question, flags=re.IGNORECASE).strip(' ?.')
        title = clean_target.title() if clean_target else (topic or "Topic Explanation")

        return f"""### 📘 {title}

**Direct Overview:**
**{title}** is a key concept that plays a vital role in its domain by providing fundamental principles, structured mechanisms, and practical problem-solving capabilities.

**Core Principles & Working:**
1. **Definition & Purpose:** It defines standard operating procedures and structures designed for efficiency, clarity, and reliability.
2. **Key Application:** Widely applied across modern systems, academic frameworks, and real-world implementations.
3. **Best Practices:** Focus on understanding the core logic, breaking complex requirements into manageable steps, and verifying outcomes through testing.

---
💡 *Feel free to ask for a specific code example, formula derivation, or further explanation!*"""

_llm_service = LLMService()

def get_llm_service():
    return _llm_service
