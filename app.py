import streamlit as st
from google import genai

# Page config
st.set_page_config(
    page_title="Sehat Saathi - AI Health Triage",
    page_icon="🩺",
    layout="centered"
)

# Custom CSS for better look
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1a5f2a 0%, #0d3b1a 100%);
        padding: 20px;
    }
    .stApp {
        background: linear-gradient(135deg, #1a5f2a 0%, #0d3b1a 100%);
    }
    .title {
        color: white;
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
    }
    .subtitle {
        color: #a8e6cf;
        text-align: center;
        font-size: 1.2rem;
    }
    .result-box {
        background: #0d3b1a;
        border-radius: 10px;
        padding: 20px;
        border: 2px solid #2d8a4e;
        margin-top: 20px;
    }
    .urgent {
        color: #ff6b6b;
        font-weight: bold;
    }
    .moderate {
        color: #ffd93d;
        font-weight: bold;
    }
    .safe {
        color: #6bff8e;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Gemini client
@st.cache_resource
def get_client():
    return genai.Client(api_key="AIzaSyDD1W3GrD7HS3bvHwQEqA5-nA-kwoopY4E")

client = get_client()

# Main function
def sehat_saathi(user_symptoms):
    system_prompt = """You are Sehat Saathi, a health triage assistant for users in Pakistan.
Users type symptoms in Roman Urdu (English alphabet, Urdu language).
You MUST respond in this EXACT format:

URDU RESPONSE (Roman Urdu):
[2-3 sentences explaining possible causes in simple Roman Urdu]

URGENCY LEVEL:
[Choose ONE: Ghar Mein Ilaj | Doctor Se Milen | Foran Emergency]

ADVICE:
[2-3 bullet points as - dashes, not asterisks]

IMPORTANT RULES:
- Always respond in Roman Urdu, not English script
- Be conservative: if symptoms could be serious, recommend doctor
- Never claim to be a real doctor
- Keep language simple for low-literacy users"""
    
    full_prompt = f"{system_prompt}\n\nUser symptoms: {user_symptoms}"
    
    try:
        response = client.models.generate_content(
            model="gemma-4-31b-it",
            contents=full_prompt
        )
        return response.text, "Gemma-4"
    except:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )
        return response.text, "Gemini (fallback)"

# UI
st.markdown('<p class="title">🩺 Sehat Saathi</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI Health Triage for Pakistan</p>', unsafe_allow_html=True)

st.markdown("---")

# Info box
with st.expander("ℹ️ Is App Ke Baare Mein (About)", expanded=False):
    st.markdown("""
    **Sehat Saathi** aapki takleef ko Roman Urdu mein samajhta hai aur aapko batata hai:
    - 🏠 **Ghar Mein Ilaj** - Ghar par theek ho sakta hai
    - 👨‍⚕️ **Doctor Se Milen** - Doctor se checkup karwana behtar hoga  
    - 🚨 **Foran Emergency** - Turant hospital jana zaroori hai
    
    ⚠️ **Note:** Yeh AI assistant hai, asli doctor nahi. Gair mamooli surat-e-haal mein doctor se zaroor milein.
    """)

# Input area
st.markdown("### ✍️ Apni Takleef Likhein (Roman Urdu Mein)")

col1, col2 = st.columns([3, 1])
with col1:
    user_input = st.text_area(
        "",
        placeholder="Example: mujhe 2 din se tez bukhar hai, sar dard aur khansi ho rahi hai...",
        height=120,
        label_visibility="collapsed"
    )
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.button("🔍 Check Karein", use_container_width=True, type="primary")

# Process
if submit and user_input.strip():
    with st.spinner("🔄 Analyzing your symptoms... Please wait..."):
        result, model_used = sehat_saathi(user_input)
    
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    
    # Parse result
    lines = result.split('\n')
    urdu_response = ""
    urgency = ""
    advice = []
    
    current_section = None
    for line in lines:
        line = line.strip()
        if line.startswith("URDU RESPONSE"):
            current_section = "response"
            continue
        elif line.startswith("URGENCY LEVEL"):
            current_section = "urgency"
            continue
        elif line.startswith("ADVICE"):
            current_section = "advice"
            continue
        elif line == "":
            continue
        elif current_section == "response" and line:
            urdu_response += line + " "
        elif current_section == "urgency" and line:
            urgency = line
        elif current_section == "advice" and line:
            advice.append(line)
    
    # Display
    st.markdown("### 📋 Tashkhees (Analysis)")
    st.markdown(f'<p style="color:white; font-size:1.1rem;">{urdu_response.strip()}</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ⚡ Emergency Level")
    
    if "Doctor" in urgency or "Milen" in urgency:
        st.error(f"**{urgency}**")
    elif "Foran" in urgency or "Emergency" in urgency:
        st.error(f"🚨 **{urgency}**")
    else:
        st.success(f"✅ **{urgency}**")
    
    st.markdown("---")
    st.markdown("### 💊 Mashwara (Advice)")
    for adv in advice:
        clean_adv = adv.replace('-', '').replace('*', '').strip()
        if clean_adv:
            st.markdown(f"• {clean_adv}")
    
    st.markdown("---")
    st.caption(f"🤖 Powered by: **{model_used}** | ⚠️ Yeh doctor ki jagah nahi le sakta")
    
    st.markdown('</div>', unsafe_allow_html=True)

elif submit:
    st.warning("⚠️ Barah-e-meharbani apni takleef likhein.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#888;">
    Made with ❤️ for Pakistan | Gemma 4 Good Hackathon 2026<br>
    Google DeepMind
</div>
""", unsafe_allow_html=True)