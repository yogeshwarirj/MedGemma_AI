# MedPanel - Multi-Agent AI Clinical Decision Support

AI system using adversarial agents to catch missed diagnoses.

## Features
- 🩻 Radiologist Agent - Image analysis
- 🩺 Internist Agent - Symptom analysis
- 📚 Evidence Reviewer - PubMed RAG
- 😈 Devil's Advocate - Challenges diagnoses
- 🎯 Orchestrator - Final synthesis

## Setup

### Local Development
```bash
# Clone repo
git clone https://github.com/yourusername/medpanel-backend.git
cd medpanel-backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env and add your HF_TOKEN

# Run locally
python app.py
```

### Deploy to Render
1. Push to GitHub
2. Connect to Render
3. Add HF_TOKEN environment variable
4. Deploy

### API Usage

**POST /analyze**
```json
{
  "image": "base64_encoded_image_data",
  "notes": "Patient symptoms and clinical notes"
}
```

**Response:**
```json
{
  "success": true,
  "report": {
    "primary_diagnosis": "...",
    "panel_agreement_score": 95,
    "escalate_to_human": true,
    ...
  }
}
```

## Built For
Google MedGemma Impact Challenge 2025

## License
MIT
