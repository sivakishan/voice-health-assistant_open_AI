import streamlit as st
import time
import os
import requests
from PIL import Image
import openai
import base64
from speech_utils import listen_to_voice, speak
from gpt_engine import ask_gpt
from excel_lookup import get_medicine_for_symptom
from elks_handler import make_reservation_call
from map_finder import get_pharmacy_link
from dotenv import load_dotenv

st.set_page_config(layout="centered", page_title="Health Assistant", page_icon="💊")

st.markdown("<h1 style='text-align: center;'>🦳 Voice Health Assistant</h1>", unsafe_allow_html=True)

conversation_active = True
last_speech_time = time.time()
TIMEOUT = 180  # 3 minutes

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_nearby_medical_stores(api_key, location="pharmacy", latitude="17.385044", longitude="78.486671"):
    url = (
        f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
        f"location={latitude},{longitude}&radius=2000&type=pharmacy&keyword={location}&key={api_key}"
    )
    response = requests.get(url)
    stores = []
    if response.status_code == 200:
        data = response.json()
        for result in data.get("results", [])[:3]:
            name = result.get("name")
            address = result.get("vicinity", "No address")
            phone = result.get("formatted_phone_number", "+46123456789")  # fallback for now
            if phone.startswith("0"):
                phone = "+46" + phone[1:]
            stores.append({"name": name, "address": address, "number": phone})
    return stores

def describe_medicine_image(image_file):
    image = Image.open(image_file)
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {"role": "system", "content": "You are a helpful medical assistant. Describe what the medicine is and what it is used for."},
            {"role": "user", "content": [
                {"type": "text", "text": "What is this medicine used for?"},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(image_file.getvalue()).decode('utf-8')}}
            ]}
        ],
        max_tokens=300
    )
    return response.choices[0].message['content']

uploaded_file = st.file_uploader("Upload a photo of a medicine to identify it", type=["jpg", "png", "jpeg"])
if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Medicine Image", use_column_width=True)
    with st.spinner("Analyzing the medicine..."):
        result = describe_medicine_image(uploaded_file)
        st.success(result)
        speak(result)

if st.button("🎹 Start Talking"):
    st.write("Speak now. Say 'stop' to end the session.")
    speak("Hi! I'm listening. You can ask me anything health-related.")

    while conversation_active:
        if time.time() - last_speech_time > TIMEOUT:
            st.warning("Session timed out after 3 minutes of silence.")
            speak("Ending session due to inactivity.")
            break

        query = listen_to_voice()
        if not query or query.lower() == "sorry, i didn't catch that.":
            continue

        last_speech_time = time.time()
        st.write(f"🔤 You said: {query}")

        if "stop" in query.lower():
            st.success("Session ended.")
            speak("Goodbye! Stay healthy.")
            break

        response = ask_gpt(query)
        st.success(response)
        speak(response)

        st.subheader("🔎 Suggestions from database:")
        data = get_medicine_for_symptom(query)
        if data:
            for item in data:
                st.info(f"💊 {item['Medicine']} — {item['Dosage']}\n📄 {item['Instructions']}")
        else:
            st.warning("No medicine found for this symptom.")

        if "medical store" in query.lower() or "pharmacy" in query.lower():
            api_key = os.getenv("GOOGLE_MAPS_API_KEY")
            stores = get_nearby_medical_stores(api_key)
            if stores:
                speak(f"I found {len(stores)} pharmacies nearby.")
                for store in stores:
                    speak(f"{store['name']} located at {store['address']}.")
            else:
                speak("Sorry, I could not find any nearby pharmacies.")
            store_url = "https://www.google.com/maps/search/pharmacy+near+me/"
            st.markdown(f"[📍 Nearby Pharmacies]({store_url})")
            speak("I found nearby pharmacies. Do you want me to call one?")

            permission = listen_to_voice()
            if "yes" in permission.lower():
                medicine_name = data[0]['Medicine'] if data else "a medicine"
                store = stores[0] if stores else {"name": "a pharmacy", "address": "unknown", "number": "+911234567890"}
                speak(f"Calling {store['name']} for {medicine_name}.")
                sid = make_reservation_call(store['number'], medicine_name)
                st.info(f"📞 Call placed. Call ID: {sid}")
            else:
                st.info("Okay, not making the call.")
