"""
MedPanel Flask API - Optimized for Lovable Frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import base64
from io import BytesIO
import os
import json
import traceback

from medpanel import initialize_models, run_medpanel

app = Flask(__name__)

# Configure CORS to accept requests from Lovable
CORS(app, resources={
    r"/*": {
        "origins": ["*"],  # Allows all origins - you can restrict to Lovable domain
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize models on startup
print("🚀 Starting MedPanel API...")
HF_TOKEN = os.environ.get('HF_TOKEN')
if not HF_TOKEN:
    print("⚠️ Warning: HF_TOKEN not found. Set it as environment variable.")
else:
    initialize_models(HF_TOKEN)
    print("✅ Models loaded and ready!")


@app.route('/', methods=['GET'])
def home():
    """Root endpoint - API info"""
    return jsonify({
        "service": "MedPanel API",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze (POST)",
            "test": "/test (GET)"
        },
        "documentation": "https://github.com/yourusername/medpanel-backend"
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "MedPanel API",
        "models_loaded": True
    })


@app.route('/test', methods=['GET'])
def test():
    """Test endpoint with mock response"""
    return jsonify({
        "success": True,
        "message": "API is working!",
        "sample_response": {
            "primary_diagnosis": "Test Mode",
            "panel_agreement_score": 100,
            "escalate_to_human": False
        }
    })


@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    """
    Main analysis endpoint - accepts image and clinical notes from Lovable
    
    Request format:
    {
        "image": "data:image/png;base64,iVBORw0KG..." (optional),
        "notes": "Patient clinical notes",
        "mode": "full" or "text-only" (optional)
    }
    """
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Parse request data
        if request.is_json:
            data = request.json
        else:
            return jsonify({
                "success": False,
                "error": "Content-Type must be application/json"
            }), 400
        
        # Extract clinical notes
        notes = data.get('notes', '').strip()
        if not notes:
            return jsonify({
                "success": False,
                "error": "Clinical notes are required",
                "message": "Please provide patient symptoms and clinical information"
            }), 400
        
        # Extract and decode image (if provided)
        image = None
        image_provided = False
        
        if data.get('image'):
            try:
                image_data = data['image']
                
                # Handle data URL format (data:image/png;base64,...)
                if 'base64,' in image_data:
                    image_data = image_data.split('base64,')[1]
                
                # Decode base64
                image_bytes = base64.b64decode(image_data)
                image = Image.open(BytesIO(image_bytes)).convert('RGB')
                image_provided = True
                
                print(f"📷 Image received: {image.size}")
                
            except Exception as img_error:
                print(f"⚠️ Image decode error: {img_error}")
                return jsonify({
                    "success": False,
                    "error": "Invalid image format",
                    "message": "Please provide a valid base64-encoded image"
                }), 400
        
        # Determine mode
        mode = data.get('mode', 'full' if image_provided else 'text-only')
        
        print(f"\n🏥 MedPanel Request:")
        print(f"   Mode: {mode}")
        print(f"   Image: {'Yes' if image else 'No'}")
        print(f"   Notes length: {len(notes)} chars")
        
        # Run MedPanel analysis
        result = run_medpanel(image, notes)
        
        # Parse and clean the report
        report = result["final_report"]
        
        # Handle raw_response format
        if isinstance(report, dict) and "raw_response" in report:
            try:
                raw = report["raw_response"]
                
                # Clean up truncated JSON
                if not raw.strip().endswith('}'):
                    # Find last complete field
                    last_complete = raw.rfind('",')
                    if last_complete > 0:
                        raw = raw[:last_complete+2] + '\n}'
                
                # Parse JSON
                report = json.loads(raw)
                print("✅ Report parsed successfully")
                
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parse error: {e}")
                # Keep raw_response if parsing fails
                pass
        
        # Add metadata
        response_data = {
            "success": True,
            "mode": mode,
            "image_analyzed": image_provided,
            "report": report,
            "trace": result["panel_trace"],
            "summary": {
                "diagnosis": report.get('primary_diagnosis', 'N/A'),
                "confidence": report.get('panel_agreement_score', 'N/A'),
                "escalate": report.get('escalate_to_human', False),
                "reason": report.get('escalation_reason', '')
            }
        }
        
        print("✅ Analysis complete\n")
        return jsonify(response_data)
        
    except Exception as e:
        # Log full error
        error_trace = traceback.format_exc()
        print(f"❌ Error occurred:")
        print(error_trace)
        
        return jsonify({
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "message": "An error occurred during analysis. Please try again."
        }), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "message": "Please check the API documentation"
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": "Something went wrong. Please try again later."
    }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"\n{'='*60}")
    print(f"🏥 MedPanel API Server")
    print(f"{'='*60}")
    print(f"🌐 Running on: http://0.0.0.0:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"{'='*60}\n")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
