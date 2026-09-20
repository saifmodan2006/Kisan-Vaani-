# Kisan Vaani

> Multimodal Voice and Text Agricultural Intelligence Platform for Indian Farmers  
> Built for the WeMakeDevs First Commit Hackathon (Build It Track)

---

## 1. Problem Statement

Indian farmers frequently encounter significant information barriers when marketing their produce and navigating government welfare initiatives:

1. **Market Price Asymmetry:** Local middlemen and aggregators often quote non-transparent crop rates. Farmers lack immediate, comparative visibility into daily prices across neighboring Agricultural Produce Market Committees (APMC mandis) to negotiate fair compensation.
2. **Complex Welfare Schemes:** Core central and state agricultural welfare programs (such as PM-KISAN, PMFBY, and SMAM) operate under strict landholding and category-specific eligibility conditions. Agricultural documentation is frequently bureaucratic and inaccessible to rural producers.
3. **Literacy and Accessibility:** Many farmers in rural regions face literacy challenges and require direct, spoken voice interaction in regional Indian languages rather than text-based web forms.

Kisan Vaani addresses these challenges by providing an intelligent, bilingual voice and text conversational assistant that delivers actionable market prices and eligibility assessments in plain Hindi and English.

---

## 2. Key Features

### Feature A: Multimodal Voice Interaction (Speech-to-Text and Text-to-Speech)
- **Voice Query Processing:** Users can speak directly into their microphone in Hindi or Indian English. Audio is converted into text and processed by the intelligence engine.
- **Natural Audio Playback:** Kisan Vaani synthesizes natural spoken responses in Hindi or Indian English using text-to-speech, allowing farmers to listen to guidance without reading screens.
- **Continuous Multi-Turn Dialogue:** The voice interface automatically resets after each turn, enabling natural, uninterrupted back-to-back voice questions while preserving conversation memory.

### Feature B: Mandi Price Navigator
- **Commodity Price Discovery:** Provides verified price information per quintal for five staple crops: Onion, Wheat, Rice, Cotton, and Tomato.
- **District Coverage:** Tracks APMC market data across Nashik, Pune, Indore, and Karnal.
- **Automated Clarification:** When a query lacks either the crop name or the target district, the system politely prompts for the missing parameter before executing the market lookup.

### Feature C: Government Scheme Eligibility Advisor
- **Deterministic Rule Evaluation:** Assesses applicant qualifications based on farm acreage and classification (land-owning farmer vs. tenant farmer).
- **Supported Schemes:**
  - **PM-KISAN (Pradhan Mantri Kisan Samman Nidhi):** Direct income support of Rs. 6,000 per year in three equal installments for eligible farmers holding up to 5 acres.
  - **PMFBY (Pradhan Mantri Fasal Bima Yojana):** Comprehensive crop loss insurance against natural risks with nominal premium caps (1.5% to 2%), applicable to both owners and tenant farmers.
  - **SMAM (Sub-Mission on Agricultural Mechanization):** 40% to 50% capital subsidies for purchasing tractors, power tillers, and agricultural machinery for landholdings up to 10 acres.
- **Transparent Justification:** Outputs plain-language reasoning for why an applicant qualifies or does not qualify for each scheme.

---

## 3. Architecture Note

> Agent tool-calling architecture built in plain Python using Gemini API function calling (same function-calling pattern used by AWS Strands Agents SDK) due to time constraints — see Future Work for a Strands migration path. Built for WeMakeDevs First Commit hackathon (Build It track).

---

## 4. Technical Stack

- **Application Logic:** Python 3.10+
- **Agent Intelligence & Function Calling:** Google Gemini API (gemini-3.6-flash / gemini-3.5-flash with native tool execution and model failover)
- **Voice Recognition (Speech-to-Text):** SpeechRecognition engine with Gemini multimodal audio fallback
- **Voice Synthesis (Text-to-Speech):** gTTS (Google Text-to-Speech) for Hindi and Indian English
- **User Interface:** Streamlit interactive web and voice application
- **Data Persistence:** Local structured JSON records (`data/mandi_prices.json`, `data/schemes.json`)

---

## 5. Repository Structure

```
aws_first_commit_hackathon/
|-- data/
|   |-- mandi_prices.json       # APMC commodity pricing records
|   |-- schemes.json            # Welfare scheme rules and benefit descriptions
|-- agent.py                    # LLM configuration, function calling, system instructions
|-- app.py                      # Streamlit voice and text chat interface
|-- tools.py                    # Core deterministic tools for prices and eligibility
|-- voice.py                    # Audio transcription and speech synthesis utilities
|-- requirements.txt            # Project dependencies
|-- .env.example                # Environment variable configuration template
|-- .gitignore                  # Exclusion file for secrets and temporary artifacts
`-- README.md                   # Project documentation
```

---

## 6. Installation and Execution

### Prerequisites
- Python 3.10 or higher
- Git
- Google Gemini API Key

### Step 1: Clone the Repository
```bash
git clone https://github.com/saifmodan2006/Kisan-Vaani-.git
cd Kisan-Vaani-
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment
Copy the example environment configuration:
```bash
cp .env.example .env
```
Open `.env` in a text editor and provide your Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key
```

### Step 4: Launch the Application
Run the Streamlit server:
```bash
streamlit run app.py
```
If `streamlit` is not recognized directly on your system PATH:
```bash
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 7. Sample Queries

Users can interact through either voice or text input:

- **Price Inquiry (English):** "What is the onion price in Nashik?"
- **Price Inquiry (Hindi):** "नाशिक में प्याज का भाव क्या है?"
- **Eligibility Assessment:** "I have 3 acres of land, am I eligible for PM-KISAN? I am a farmer."
- **Tenant Machinery Inquiry:** "I am a tenant farmer with 4 acres. Can I get a subsidy on machinery?"
- **Missing Information Query:** "What is the price of tomato?" *(The assistant asks which district to check before executing).*

---

## 8. Future Work and Cloud Migration Path

1. **AWS Voice Integration:**
   - Integrate **Amazon Transcribe** for high-accuracy regional Indian dialect transcription and streaming speech-to-text.
   - Integrate **Amazon Polly** for neural natural voice output tailored for rural communities.
2. **Live Government Data Integration:**
   - Replace static JSON data layers with real-time feeds from the Open Government Data (OGD) Platform India / Agmarknet API.
3. **AWS Strands Agents SDK Migration:**
   - Refactor Python function-calling tools into the AWS Strands Agents SDK tool format to operate natively across AWS Bedrock foundation models.
4. **Cloud Deployment (Ship It Track):**
   - Package application backend into containerized AWS Lambda functions fronted by Amazon API Gateway and Amazon Bedrock, or deploy via AWS App Runner for scalable hosting.
