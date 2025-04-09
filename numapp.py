import os
import re
import streamlit as st
from datetime import datetime
from groq import Groq

# --- Helper Functions ---

def numerology_value(name: str, use_vowels=None):
    values = {
        'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
        'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
        'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
    }
    vowels = "AEIOU"
    name = re.sub(r'[^A-Z]', '', name.upper())

    if use_vowels is None:
        selected = [values[ch] for ch in name]
    else:
        selected = [values[ch] for ch in name if (ch in vowels) == use_vowels]

    total = sum(selected)
    while total > 9 and total not in {11, 22, 33}:
        total = sum(int(d) for d in str(total))
    return total

def calculate_life_path_number(birthdate_str):
    mm, dd, yyyy = map(int, birthdate_str.split('/'))
    total = 0
    for num in [mm, dd, yyyy]:
        while num > 0:
            total += num % 10
            num //= 10
    while total > 9 and total not in {11, 22, 33}:
        total = sum(int(d) for d in str(total))
    return total

# --- Groq API Call Using the SDK ---
def get_numerology_explanation(name, birthdate, life_path, expression, soul_urge, personality, birthday, groq_client):
    prompt = f"""
    <think>
    Analyze the numerology for the following:
    - Name: {name}
    - Birthdate: {birthdate}
    - Life Path: {life_path}
    - Expression: {expression}
    - Soul Urge: {soul_urge}
    - Personality: {personality}
    - Birthday: {birthday}

    Think step-by-step through the personality, contradictions, traits, and possible growth paths. Structure your thoughts clearly.
    </think>
    """
    try:
        response = groq_client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- Streamlit App ---

def main():
    st.title("🔢 Numerology Magic!")
    st.markdown("""

Unlock the secrets of your **name** and **birthdate** with *Numerology Magic*—your personal guide to the hidden numbers that shape your life!  
Whether you're a **master number 22** destined for greatness or a **soulful 9** on a mission of compassion, our app reveals your unique **cosmic blueprint**.

---

### ✨ Discover Your Core Numbers:

- **Life Path**: Your destiny’s roadmap  
- **Expression**: Your true potential  
- **Soul Urge**: Your deepest desires  
- **Personality**: How the world sees you  

---

Enter your **name** and **birthdate**, and let the numbers tell your story.  
Are you ready to **decode your destiny**? 🔮

#### 👉 Calculate Your Custom Analysis Now✨
---
""")
    # Securely load API key (use environment variables or Streamlit secrets)
    groq_api_key = ("GROQ_API_KEY")
    
    if not groq_api_key:
        st.error("GROQ_API_KEY not found in environment variables or secrets. Please set it and restart the app.")
        st.stop()
    
    # Initialize the Groq client using the SDK
    groq_client = Groq(api_key=groq_api_key)
    
    st.sidebar.image("1.png")
    st.info("build by dw")
    name = st.sidebar.text_input("📝 Full Name")
    birthdate = st.sidebar.date_input("📅 Birthdate", datetime.now())
    
    if st.sidebar.button("Calculate Numerology"):
        if not name:
            st.error("Please enter a name.")
            return
        
        birth_str = birthdate.strftime("%m/%d/%Y")
        life_path = calculate_life_path_number(birth_str)
        expression = numerology_value(name)
        soul_urge = numerology_value(name, use_vowels=True)
        personality = numerology_value(name, use_vowels=False)
        
        # Calculate Birthday Number with reduction as needed
        birthday_num = birthdate.day
        while birthday_num > 9 and birthday_num not in {11, 22, 33}:
            birthday_num = sum(int(d) for d in str(birthday_num))
        
        st.subheader("🔍 Your Core Numbers")
        cols = st.columns(2)
        cols[0].write(f"**Life Path Number:** {life_path}")
        cols[1].write(f"**Expression Number:** {expression}")
        cols[0].write(f"**Soul Urge Number:** {soul_urge}")
        cols[1].write(f"**Personality Number:** {personality}")
        cols[0].write(f"**Birthday Number:** {birthday_num}")
        
        with st.spinner("Generating reading..."):
            explanation = get_numerology_explanation(
                name, birth_str, life_path, expression, 
                soul_urge, personality, birthday_num, groq_client
            )
            st.markdown("---")
            st.subheader("📖 Numerology Reading")
            st.text(" * for entertainment use only")

            # Extract <think> section
            thinking = explanation
            if "<think>" in explanation:
                try:
                    thinking = explanation.split("<think>")[1].split("</think>")[0].strip()
                except:
                    thinking = explanation  # fallback

            # Display columns
            st.markdown("### ✨ Final Reading")
            st.write(thinking)


if __name__ == "__main__":
    main()
