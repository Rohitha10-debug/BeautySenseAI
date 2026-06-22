from flask import Flask, render_template, request, jsonify
import random
import re
import sys
import json

app = Flask(__name__, static_url_path='', static_folder='.', template_folder='.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze_product', methods=['POST'])
def analyze_product():
    data = request.get_json()
    product_name = data.get('product_name')

    if not product_name:
        return jsonify({'error': 'Product name is required'}), 400

    # Simulate Generative AI Analysis
    analysis_result = run_genai_analysis(product_name)
    
    # Simulate Recommendations
    recommendations = get_recommendations(product_name)
    
    response = {
        **analysis_result,
        "recommendations": recommendations
    }
    
    try:
        json_response = json.dumps(response, indent=2)
        # with open('debug_output.json', 'w') as f:
        #     f.write(json_response)
        
        return app.response_class(response=json_response, status=200, mimetype='application/json')
    except Exception as e:
        print(f"DEBUG: JSON dump failed: {e}", file=sys.stderr)
        return jsonify({'error': 'JSON serialization failed'}), 500

@app.route('/api/analyze_single_review', methods=['POST'])
def analyze_single_review():
    data = request.get_json()
    review_text = data.get('review_text')

    if not review_text:
        return jsonify({'error': 'Review text is required'}), 400

    # Input Validation: Allow only alphanumeric and basic punctuation
    # Allowed: Letters, Numbers, Spaces, ., !, ?, ', ", -
    if not re.match(r'^[a-zA-Z0-9\s.,!?"\'-]+$', review_text):
        return jsonify({'error': 'Invalid character used'}), 400

    sentiment = run_single_sentiment_check(review_text)
    return jsonify({'sentiment': sentiment})

@app.route('/api/book_appointment', methods=['POST'])
def book_appointment():
    data = request.get_json()
    # In a real app, this would save to a database
    # Mock success response
    return jsonify({'success': True, 'message': 'Appointment booked successfully!'})

@app.route('/api/generate_diary', methods=['POST'])
def generate_diary():
    data = request.get_json()
    skin_type = data.get('skin_type')
    concerns = data.get('concerns')
    
    # Mock AI Logic for Skincare Diary
    # Simple rule-based generation for demo
    routine = {
        "Morning": ["Gentle Cleanser", "Vitamin C Serum", "Moisturizer", "Sunscreen"],
        "Evening": ["Oil Cleanser", "Water-based Cleanser", "Retinol (if applicable)", "Heavy Moisturizer"]
    }
    
    if skin_type and "dry" in skin_type.lower():
        routine["Morning"] = ["Hydrating Cleanser", "Hyaluronic Acid", "Rich Moisturizer", "Sunscreen"]
        routine["Evening"] = ["Cleansing Balm", "Hydrating Cleanser", "Peptide Serum", "Sleeping Mask"]
    elif skin_type and "oily" in skin_type.lower():
        routine["Morning"] = ["Foaming Cleanser", "Niacinamide", "Gel Moisturizer", "Matte Sunscreen"]
        routine["Evening"] = ["Micellar Water", "Salicylic Acid Cleanser", "Lightweight Moisturizer"]
        
    return jsonify({'routine': routine})

def run_genai_analysis(product_name):
    """
    Simulates the core Generative AI logic.
    Returns a JSON object with sentiment data.
    """
    # Mock data generation based on product name length to give slight variety
    # In a real app, this would call an LLM API
    
    base_sentiment = {
        "Positive": 65,
        "Negative": 20,
        "Neutral": 10,
        "Mixed": 5
    }
    
    # Slight randomization for demo purposes
    pos = random.randint(55, 75)
    neg = random.randint(10, 25)
    neu = random.randint(5, 15)
    mixed = 100 - (pos + neg + neu)
    
    if mixed < 0:
        mixed = 0
        neu = 100 - (pos + neg)

    overall_sentiment = {
        "Positive": pos,
        "Negative": neg,
        "Neutral": neu,
        "Mixed": mixed
    }

    key_aspects_sentiment = [
        {"aspect": "Effectiveness", "sentiment": f"Positive ({random.randint(80, 95)}%)"},
        {"aspect": "Texture", "sentiment": f"Positive ({random.randint(70, 90)}%)"},
        {"aspect": "Scent", "sentiment": f"Neutral ({random.randint(40, 60)}%)"},
        {"aspect": "Price", "sentiment": f"Negative ({random.randint(50, 70)}%)"},
        {"aspect": "Packaging", "sentiment": f"Positive ({random.randint(85, 99)}%)"}
    ]

    ai_summary = (
        f"Based on recent customer feedback, {product_name} is highly regarded for its effectiveness and luxurious texture. "
        "Users consistently praise the packaging, though some find the price point to be on the higher side. "
        "The scent receives mixed reviews, with some finding it pleasant and others finding it too strong. "
        "Overall, it is considered a premium choice in its category."
    )

    sample_reviews = [
        {"text": f"I absolutely love {product_name}! It changed my skin texture overnight.", "sentiment": "Positive"},
        {"text": "Too expensive for the amount you get. I didn't see a huge difference.", "sentiment": "Negative"},
        {"text": "It's okay. Smells nice but I'm not sure if it's worth the hype.", "sentiment": "Neutral"}
    ]

    return {
        "overall_sentiment": overall_sentiment,
        "key_aspects_sentiment": key_aspects_sentiment,
        "ai_summary": ai_summary,
        "sample_reviews": sample_reviews
    }

def run_single_sentiment_check(review_text):
    """
    Simulates sentiment analysis for a single review.
    Returns: "Positive", "Negative", or "Neutral"
    """
    # Enhanced rule-based sentiment analysis
    text_lower = review_text.lower()
    
    # Gibberish Detection:
    # 1. Check for long continuous strings without spaces (likely random keys)
    if len(review_text) > 15 and ' ' not in review_text:
        return "Invalid Input"
    
    # Normalize repeated characters (e.g., "goood" -> "good", "baaad" -> "bad")
    # This reduces 3 or more identical characters to 1, and 2 identical characters to 1 if not in dictionary? 
    # Simpler approach: Check original, then check with 3+ reduced to 1, then 2+ reduced to 1.
    
    words = text_lower.split()
    
    positive_words = {'love', 'great', 'amazing', 'good', 'best', 'excellent', 'happy', 'nice', 'wonderful', 'recommend', 'perfect', 'smooth', 'effective', 'glowing', 'awesome', 'fantastic', 'fabulous'}
    negative_words = {'hate', 'bad', 'worst', 'terrible', 'awful', 'waste', 'disappointing', 'poor', 'dry', 'irritating', 'breakout', 'useless', 'weak', 'horrible', 'gross'}
    negation_words = {'not', 'no', 'never', "don't", "didn't", "wouldn't", "isn't", "wasn't", "cant", "can't"}
    contrast_words = {'but', 'however', 'although', 'though', 'yet'}
    
    score = 0
    has_contrast = False
    
    for i, word in enumerate(words):
        # Clean punctuation from word for matching
        clean_word = re.sub(r'[^\w\s]', '', word)
        
        # Handle repeated characters: "gooddd" -> "good"
        # 1. Try exact match
        match_word = clean_word
        
        # 2. If not found, try reducing 3+ repeats to 1 (e.g. "goood" -> "god" - wait, "good" needs 2. 
        # Let's try reducing any sequence of 3+ chars to 2 chars first: "gooddd" -> "goodd"
        # Then try reducing 2+ chars to 1 char: "goodd" -> "god"
        
        # Helper to check sentiment
        def get_sentiment_val(w):
            if w in positive_words: return 1
            if w in negative_words: return -1
            return 0
            
        val = get_sentiment_val(match_word)
        
        if val == 0:
            # Try reducing 3+ repeats to 2: "sooo" -> "soo"
            reduced_3to2 = re.sub(r'(.)\1{2,}', r'\1\1', match_word)
            val = get_sentiment_val(reduced_3to2)
            
        if val == 0:
            # Try reducing 2+ repeats to 1: "good" -> "god" (might fail for good), "baaad" -> "bad"
            reduced_2to1 = re.sub(r'(.)\1+', r'\1', match_word)
            val = get_sentiment_val(reduced_2to1)
            
        # Special case: "good" -> "god" is not in list. "good" is.
        # If we have "gooddd", 3to2 gives "goodd". 2to1 gives "god". Neither matches "good".
        # We need a smarter check.
        # Try reducing 3+ to 2, AND check if removing one of double chars helps?
        # Let's just add common variations or use a library? No library allowed.
        # Let's try to match against the dictionary keys using regex? Too slow.
        
        # Simple heuristic: If word starts with a known word? No.
        # Let's try: "gooddd" -> remove trailing repeats?
        if val == 0:
             # "gooddd" -> "good"
             # Regex: Replace any char repeated 3+ times with 2 chars, then check.
             # If that fails, replace with 1 char, then check.
             # Also handle "good" specifically if needed.
             pass

        # Let's just add a manual fix for "good" variations if the above failed
        # Actually, let's look at the specific user case: "goodddddddddddd"
        # re.sub(r'(.)\1{2,}', r'\1\1', "gooddddd") -> "goodd".
        # re.sub(r'(.)\1{2,}', r'\1', "gooddddd") -> "good".  <-- This works for "gooddd"!
        # "good" has 2 'o's. They are not 3+. So "good" stays "good".
        # "goood" (3 'o's) -> "god".
        
        # So: 
        # 1. Check exact.
        # 2. Check with 3+ chars reduced to 1. (Handles "gooddd" -> "good")
        # 3. Check with 2+ chars reduced to 1. (Handles "baaad" -> "bad")
        
        if val == 0:
             reduced_3plus_to_1 = re.sub(r'(.)\1{2,}', r'\1', match_word)
             val = get_sentiment_val(reduced_3plus_to_1)
             
        if val == 0:
             reduced_2plus_to_1 = re.sub(r'(.)\1+', r'\1', match_word)
             val = get_sentiment_val(reduced_2plus_to_1)

        if word in contrast_words:
            has_contrast = True
            
        # Check for negation in the previous 2 words
        is_negated = False
        if i > 0 and words[i-1] in negation_words:
            is_negated = True
        elif i > 1 and words[i-2] in negation_words:
            is_negated = True
            
        if val == 1:
            score += -1 if is_negated else 1
        elif val == -1:
            score += 1 if is_negated else -1
            
    # Logic to handle mixed/neutral sentiments stronger
    # If there is a contrast word and the score is not strongly polarized, lean towards Neutral
    if has_contrast and -2 < score < 2:
        return "Neutral"
        
    if score > 0:
        return "Positive"
    elif score < 0:
        return "Negative"
    else:
        return "Neutral"

# Product Database with real images and purchase links
PRODUCT_DATABASE = {
    "moisturizer": [
        {
            "name": "Glow Recipe Watermelon Glow AHA Night Treatment",
            "reason": "Exfoliates and hydrates for glowing skin",
            "image_url": "https://placehold.co/600x400/FFB6C1/ffffff?text=Glow+Recipe+Watermelon",
            "product_url": "https://www.glowrecipe.com/products/watermelon-glow-aha-night-treatment"
        },
        {
            "name": "Laneige Water Sleeping Mask",
            "reason": "Intensive overnight hydration",
            "image_url": "https://placehold.co/600x400/A2D2FF/ffffff?text=Laneige+Water+Mask",
            "product_url": "https://us.laneige.com/products/water-sleeping-mask"
        },
        {
            "name": "Drunk Elephant Protini Polypeptide Cream",
            "reason": "Strengthens and firms skin",
            "image_url": "https://placehold.co/600x400/20B2AA/ffffff?text=Drunk+Elephant+Protini",
            "product_url": "https://www.drunkelephant.com/collections/moisturizers/products/protini-polypeptide-cream"
        },
        {
            "name": "Tatcha The Dewy Skin Cream",
            "reason": "Rich, moisturizing cream for dry skin",
            "image_url": "https://placehold.co/600x400/E6E6FA/000000?text=Tatcha+Dewy+Skin",
            "product_url": "https://www.tatcha.com/product/the-dewy-skin-cream/CL30510.html"
        },
        {
            "name": "Kiehl's Ultra Facial Cream",
            "reason": "24-hour hydration for all skin types",
            "image_url": "https://placehold.co/600x400/ffffff/000000?text=Kiehls+Ultra+Facial",
            "product_url": "https://www.kiehls.com/skincare/face-moisturizers/ultra-facial-cream-with-squalane/622.html"
        },
        {
            "name": "Neutrogena Hydro Boost Water Gel",
            "reason": "Lightweight, oil-free hydration",
            "image_url": "https://placehold.co/600x400/87CEEB/ffffff?text=Neutrogena+Hydro+Boost",
            "product_url": "https://www.neutrogena.com/products/skincare/neutrogena-hydro-boost-water-gel-with-hyaluronic-acid/6811047.html"
        }
    ],
    "serum": [
        {
            "name": "The Ordinary Niacinamide 10% + Zinc 1%",
            "reason": "Reduces blemishes and balances oil",
            "image_url": "https://placehold.co/600x400/D3D3D3/000000?text=The+Ordinary+Niacinamide",
            "product_url": "https://theordinary.com/en-us/niacinamide-10-zinc-1-serum-100436.html"
        },
        {
            "name": "Estée Lauder Advanced Night Repair",
            "reason": "Comprehensive anti-aging serum",
            "image_url": "https://placehold.co/600x400/8B4513/ffffff?text=Estee+Lauder+ANR",
            "product_url": "https://www.esteelauder.com/product/689/7749/product-catalog/skincare/repair-serum/advanced-night-repair-serum-synchronized-multi-recovery-complex"
        },
        {
            "name": "SkinCeuticals C E Ferulic",
            "reason": "Advanced antioxidant protection",
            "image_url": "https://placehold.co/600x400/FFFFE0/000000?text=SkinCeuticals+CE+Ferulic",
            "product_url": "https://www.skinceuticals.com/skincare/vitamin-c-serums/c-e-ferulic-with-15-l-ascorbic-acid/S17.html"
        },
        {
            "name": "La Roche-Posay Hyalu B5 Serum",
            "reason": "Plumps and repairs skin barrier",
            "image_url": "https://placehold.co/600x400/00008B/ffffff?text=LRP+Hyalu+B5",
            "product_url": "https://www.laroche-posay.us/our-products/face/face-serum/hyalu-b5-pure-hyaluronic-acid-serum-hyalub5serum.html"
        },
        {
            "name": "Sunday Riley Good Genes",
            "reason": "Lactic acid treatment for radiance",
            "image_url": "https://placehold.co/600x400/FFD700/000000?text=Sunday+Riley+Good+Genes",
            "product_url": "https://sundayriley.com/products/good-genes-lactic-acid-treatment"
        },
        {
            "name": "COSRX Advanced Snail 96 Mucin Power Essence",
            "reason": "Soothes and hydrates damaged skin",
            "image_url": "https://placehold.co/600x400/F0E68C/000000?text=COSRX+Snail+Mucin",
            "product_url": "https://www.cosrx.com/products/advanced-snail-96-mucin-power-essence"
        }
    ],
    "cleanser": [
        {
            "name": "CeraVe Hydrating Facial Cleanser",
            "reason": "Restores protective skin barrier",
            "image_url": "https://placehold.co/600x400/ffffff/228B22?text=CeraVe+Hydrating",
            "product_url": "https://www.cerave.com/skincare/cleansers/hydrating-facial-cleanser"
        },
        {
            "name": "Youth to the People Superfood Cleanser",
            "reason": "Deep cleans pores with antioxidants",
            "image_url": "https://placehold.co/600x400/228B22/ffffff?text=YTTP+Superfood",
            "product_url": "https://www.youthtothepeople.com/products/superfood-cleanser"
        },
        {
            "name": "Fresh Soy Face Cleanser",
            "reason": "pH-balanced and gentle",
            "image_url": "https://placehold.co/600x400/F5F5DC/000000?text=Fresh+Soy+Cleanser",
            "product_url": "https://www.fresh.com/us/skincare/cleansers/face-cleansers/soy-ph-balanced-hydrating-facial-cleanser-fresh/02001557.html"
        },
        {
            "name": "Cetaphil Gentle Skin Cleanser",
            "reason": "Clinically proven to hydrate",
            "image_url": "https://placehold.co/600x400/ffffff/0000FF?text=Cetaphil+Gentle",
            "product_url": "https://www.cetaphil.com/us/gentle-skin-cleanser/302993921045.html"
        },
        {
            "name": "La Roche-Posay Toleriane Hydrating Gentle Cleanser",
            "reason": "Formulated for sensitive skin",
            "image_url": "https://placehold.co/600x400/ffffff/00008B?text=LRP+Toleriane",
            "product_url": "https://www.laroche-posay.us/our-products/face/face-wash/toleriane-hydrating-gentle-facial-cleanser-tolerianehydratinggentlefacialcleanser.html"
        },
        {
            "name": "Farmacy Green Clean Makeup Meltaway Cleansing Balm",
            "reason": "Melts away makeup and pollution",
            "image_url": "https://placehold.co/600x400/98FB98/000000?text=Farmacy+Green+Clean",
            "product_url": "https://www.farmacybeauty.com/products/green-clean-makeup-meltaway-cleansing-balm"
        }
    ],
    "sunscreen": [
        {
            "name": "Supergoop! Unseen Sunscreen SPF 40",
            "reason": "Totally invisible, weightless formula",
            "image_url": "https://placehold.co/600x400/FFFF00/000000?text=Supergoop+Unseen",
            "product_url": "https://supergoop.com/products/unseen-sunscreen"
        },
        {
            "name": "La Roche-Posay Anthelios Melt-in Milk SPF 60",
            "reason": "Broad spectrum protection for face and body",
            "image_url": "https://placehold.co/600x400/FFA500/ffffff?text=LRP+Anthelios",
            "product_url": "https://www.laroche-posay.us/our-products/sun/body-sunscreen/anthelios-melt-in-milk-sunscreen-spf-60-antheliosmeltinmilkbodyfacesunscreenspf60.html"
        },
        {
            "name": "EltaMD UV Clear Broad-Spectrum SPF 46",
            "reason": "Calms and protects acne-prone skin",
            "image_url": "https://placehold.co/600x400/ffffff/000000?text=EltaMD+UV+Clear",
            "product_url": "https://eltamd.com/products/uv-clear-broad-spectrum-spf-46"
        },
        {
            "name": "Neutrogena Ultra Sheer Dry-Touch SPF 70",
            "reason": "Fast-absorbing and water-resistant",
            "image_url": "https://placehold.co/600x400/87CEEB/ffffff?text=Neutrogena+Ultra+Sheer",
            "product_url": "https://www.neutrogena.com/products/sun/ultra-sheer-dry-touch-sunscreen-broad-spectrum-spf-70/6868790.html"
        },
        {
            "name": "Black Girl Sunscreen SPF 30",
            "reason": "No white cast, infused with jojoba and cacao",
            "image_url": "https://placehold.co/600x400/000000/FFD700?text=Black+Girl+Sunscreen",
            "product_url": "https://www.blackgirlsunscreen.com/product/black-girl-sunscreen-spf-30/"
        }
    ]
}

def get_recommendations(product_name):
    """
    Returns recommendations based on the product category inferred from the name.
    """
    product_lower = product_name.lower()
    
    if "serum" in product_lower or "treatment" in product_lower or "oil" in product_lower:
        category = "serum"
    elif "cleanser" in product_lower or "wash" in product_lower or "scrub" in product_lower:
        category = "cleanser"
    elif "sunscreen" in product_lower or "spf" in product_lower or "block" in product_lower:
        category = "sunscreen"
    else:
        # Default to moisturizer if no other category matches
        category = "moisturizer"
        
    # Get all products for the category
    all_recs = PRODUCT_DATABASE.get(category, PRODUCT_DATABASE["moisturizer"])
    
    # Randomly select 3 unique products
    # Ensure we don't try to sample more than available
    num_to_select = min(3, len(all_recs))
    selected_recs = random.sample(all_recs, num_to_select)
    
    return selected_recs



if __name__ == '__main__':
    app.run(port=5001)
