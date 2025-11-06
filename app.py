from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from sqlalchemy import or_ , case , func 

STOP_WORDS = set([
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", 
    "he", "him", "his", "she", "her", "it", "its", "they", "them", "their",
    "a", "an", "the", "and", "but", "if", "or", "as", "of", "at", "by", "for", 
    "with", "about", "to", "from", "in", "out", "on", "is", "am", "are", "was", 
    "were", "be", "been", "have", "has", "had", "do", "does", "did", "got", "a's",
    "get", "what", "which", "who", "whom", "this", "that", "how", "what's", "i'm"
    "please", "help", "me", "can", "want", "find", "know", "my", "rights", "legal"
])

app = Flask(__name__)
app.config['SECRET_KEY']='SUPER-SECRET-KEY'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'


db  = SQLAlchemy(app)
api = Api(app)
CORS(app)
jwt = JWTManager(app)


# === EXISTING USER MODEL ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique = True, nullable = False)
    password = db.Column(db.String(100), nullable = False)

# === UPDATED MODEL FOR RIGHTS SUGGESTIONS ===
class RightsInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    situation = db.Column(db.String(200), nullable=False, index=True) 
    rights = db.Column(db.Text, nullable=False)
    best_action = db.Column(db.Text, nullable=False)
    legal_section = db.Column(db.String(100), nullable=True) # For IPC sections
    keywords = db.Column(db.Text, nullable=True, index=True) # For better search

# === UPDATED FUNCTION TO ADD 20 SAMPLES ===
def add_sample_data():
    if RightsInfo.query.first() is None:
        print("Adding 20 sample rights info entries...")
        sample_data = [
            # ... (All 20 of your sample data entries go here) ...
            RightsInfo(
                situation="Consumer Complaint (Defective Product)",
                rights="You have the right to a refund, replacement, or repair for a defective product. You can file a complaint in consumer court.",
                best_action="Keep the receipt/invoice and warranty details. Contact customer service. If unresolved, file a complaint with the National Consumer Helpline (NCH).",
                legal_section="Consumer Protection Act, 2019",
                keywords="broken, warranty, refund, return, faulty, product, item, store"
            ),
            RightsInfo(
                situation="Cyberbullying or Online Harassment",
                rights="You have the right to report online harassment, stalking, or threats. Platforms are required to have a mechanism to report such content.",
                best_action="Do not delete the messages. Take screenshots as evidence. Block the user. Report the account to the platform and to the cyber crime portal ('cybercrime.gov.in').",
                legal_section="IT Act, 2000; IPC Sec 354D, 507",
                keywords="online, instagram, facebook, troll, threat, stalking, harassment, cyber"
            ),
            RightsInfo(
                situation="Landlord Eviction Notice",
                rights="A landlord cannot evict you without a valid reason (e.g., non-payment of rent, end of lease) and must provide a written notice as per the rent agreement.",
                best_action="Read your rental agreement. Do not move out immediately. Pay your rent. Seek legal aid or contact a rent control authority if the eviction is illegal.",
                legal_section="State-specific Rent Control Act",
                keywords="rent, tenant, lease, eviction, apartment, house, landlord, notice"
            ),
            RightsInfo(
                situation="Filing an FIR (First Information Report)",
                rights="Police are obligated to file an FIR for a cognizable offense (a serious crime). You have the right to receive a copy of the FIR for free.",
                best_action="Go to the police station in the area the crime occurred. State the facts clearly. If they refuse, you can send a written complaint to the Superintendent of Police (SP) by post.",
                legal_section="CrPC Sec 154",
                keywords="fir, complaint, report, police, station, crime, incident, file"
            ),
            RightsInfo(
                situation="Workplace Harassment (POSH)",
                rights="You have the right to a safe work environment free from sexual harassment. Companies with 10+ employees must have an Internal Complaints Committee (ICC).",
                best_action="Document every incident (date, time, location, what was said/done). Report it to your HR, manager, or the ICC as per your company's POSH policy.",
                legal_section="Sexual Harassment of Women at Workplace (POSH) Act, 2013",
                keywords="posh, boss, colleague, office, job, unwanted, inappropriate, icc"
            ),
            RightsInfo(
                situation="Bounced Cheque",
                rights="If a cheque you received bounces due to 'insufficient funds', it is a criminal offense. You can take legal action to recover the amount.",
                best_action="Send a formal legal notice to the person who issued the cheque within 30 days of it bouncing. If they don't pay within 15 days, you can file a case.",
                legal_section="Negotiable Instruments Act, 1881 (Sec 138)",
                keywords="check, bank, payment, bounce, signature, insufficient, funds"
            ),
            RightsInfo(
                situation="Domestic Violence",
                rights="You have the right to be safe from physical, emotional, or economic abuse by a partner or family member. You can seek a protection order.",
                best_action="Go to a safe place. Call the police (100/112) or a women's helpline (1091). You can file a Domestic Incident Report (DIR) with a Protection Officer or police.",
                legal_section="Protection of Women from Domestic Violence Act, 2005",
                keywords="abuse, husband, wife, partner, family, violence, assault, home"
            ),
            RightsInfo(
                situation="Medical Negligence",
                rights="You have the right to competent medical care. If a doctor or hospital provides substandard care that causes harm, you can seek compensation.",
                best_action="Gather all medical records, bills, and prescriptions. Get a second opinion from another doctor. Contact a lawyer specializing in medical negligence.",
                legal_section="Consumer Protection Act; IPC Sec 304A",
                keywords="doctor, hospital, surgery, wrong, treatment, negligence, harm"
            ),
            RightsInfo(
                situation="E-commerce Fraud (Wrong Item/Scam)",
                rights="You have the right to receive the exact product you ordered. E-commerce sites are responsible for sellers on their platform.",
                best_action="Do not throw away the packaging. Take photos/videos of the wrong item and the package. File a complaint with the platform's customer care immediately. If unresolved, go to the NCH.",
                legal_section="Consumer Protection Act, 2019",
                keywords="amazon, flipkart, myntra, refund, return, wrong, item, scam, delivery"
            ),
            RightsInfo(
                situation="Accident (Road/Traffic)",
                rights="As a victim, you have the right to medical treatment. You can file an FIR against the person at fault and claim compensation from their insurance.",
                best_action="Call the police immediately. Get medical help (Good Samaritans are protected by law). Take photos of the vehicles and scene. Get contact details of witnesses.",
                legal_section="Motor Vehicles Act; IPC Sec 279, 337",
                keywords="crash, hit, car, bike, injury, road, collision, compensation, insurance"
            ),
            RightsInfo(
                situation="Arrest by Police",
                rights="You have the right to remain silent. You have the right to an attorney. Police must inform you of the grounds for arrest.",
                best_action="Clearly state 'I am going to remain silent and I would like a lawyer.' Do not resist arrest.",
                legal_section="CrPC Sec 41, 50, 50A",
                keywords="cops, detained, police, handcuffs, station, custody"
            ),
            RightsInfo(
                situation="Police Stop (Traffic)",
                rights="You must provide your license and registration. Police need probable cause to search your car without a warrant. You can film the interaction.",
                best_action="Stay calm and polite. Do not consent to a search. Ask if you are being detained or free to go.",
                legal_section="Motor Vehicles Act",
                keywords="car, bike, pulled over, checkpost, driving, license, traffic"
            ),
            RightsInfo(
                situation="Workplace Discrimination",
                rights="You have the right to a workplace free from discrimination based on gender, caste, religion, or disability. You have the right to equal pay for equal work.",
                best_action="Document all instances of discrimination. Report the issue to your HR department or internal committee. If unresolved, you can file a complaint with the Labour Court.",
                legal_section="Equal Remuneration Act, 1976; Persons with Disabilities Act, 2016",
                keywords="job, office, discrimination, gender, caste, pay, salary, bias"
            ),
            RightsInfo(
                situation="Bank Account Fraud",
                rights="If you report an unauthorized transaction within 3 days, your liability is zero. The bank must resolve the complaint and credit the amount within 90 days.",
                best_action="Call your bank immediately to block your account/card. File a complaint on 'cybercrime.gov.in' and get an acknowledgement. Formally file a dispute with your bank.",
                legal_section="RBI Master Circular on Customer Liability",
                keywords="bank, account, fraud, unauthorized, transaction, debit, money, stolen"
            ),
            RightsInfo(
                situation="Lost or Damaged Luggage (Airlines)",
                rights="You are entitled to compensation for lost, delayed, or damaged baggage. Airlines have a fixed liability amount. You must file a report immediately.",
                best_action="Do not leave the airport. File a Property Irregularity Report (PIR) at the airline counter. Keep your baggage tag and boarding pass. Follow up via email.",
                legal_section="Carriage by Air Act, 1972",
                keywords="airline, flight, bag, luggage, lost, damaged, airport, compensation"
            ),
            RightsInfo(
                situation="Street Harassment (Eve Teasing)",
                rights="You have the right to be in public without being harassed. Making lewd comments, stalking, or inappropriate gestures is a punishable offense.",
                best_action="If safe, firmly tell the person to stop. Move to a crowded area. Call the police (100 or 112) or a women's helpline (e.g., 1091). Note the time, place, and details.",
                legal_section="IPC Sec 354A (Harassment), 354D (Stalking), 509 (Insulting modesty)",
                keywords="eve teasing, street, harassment, catcall, comment, woman, safety"
            ),
            RightsInfo(
                situation="Online Harassment / Stalking",
                rights="You have the right to report online stalking, threats, or defamation. Police can take action against the perpetrator, even if they are anonymous.",
                best_action="Do not engage with the harasser. Take screenshots of everything (messages, profiles, comments). Block the user. Report the profile to the social media platform and file a complaint on 'cybercrime.gov.in'.",
                legal_section="IPC Sec 354D (Stalking); IT Act Sec 67",
                keywords="instagram, facebook, stalk, threat, online, message, cyber"
            ),
            RightsInfo(
                situation="Passport Application Delay",
                rights="You have the right to have your passport application processed within a reasonable timeframe. You can check the status and escalate if delayed.",
                best_action="Check your status on the Passport Seva website. If delayed, raise a grievance on the same portal. If still unresolved, you can file an RTI or contact the Regional Passport Officer (RPO).",
                legal_section="Passport Act, 1967",
                keywords="passport, delay, application, status, police, verification, rpo"
            ),
            RightsInfo(
                situation="Noise Pollution (Loud Neighbours)",
                rights="You have a right to peaceful enjoyment of your home. Use of loudspeakers or high-volume music during night hours (10 PM to 6 AM) is generally prohibited.",
                best_action="Politely request your neighbour to lower the volume. If it continues, call the police control room (100 or 112). They are obligated to address noise complaints.",
                legal_section="Noise Pollution (Regulation and Control) Rules, 2000",
                keywords="loud, music, noise, neighbour, party, disturbance, police"
            ),
            RightsInfo(
                situation="Landlord Refusing to Return Deposit",
                rights="Your landlord must return your security deposit after deducting for valid damages or unpaid rent, as per your rental agreement. They cannot keep it without reason.",
                best_action="Send a formal written demand (email or letter) for the deposit. Provide your new address. If they refuse, you can send a legal notice and file a case in Small Causes Court.",
                legal_section="Based on State Rent Control Act / Rental Agreement",
                keywords="rent, deposit, security, landlord, return, move, out, agreement"
            ),
            RightsInfo(
                situation="Faulty Vehicle Repair",
                rights="You have the right to a proper repair as promised by the service center. If they do a faulty job or overcharge, you can file a complaint.",
                best_action="Keep all bills and job sheets. Get a second opinion from another mechanic in writing. Send a formal complaint to the service center head. If unresolved, approach a consumer court.",
                legal_section="Consumer Protection Act, 2019",
                keywords="car, bike, repair, mechanic, service, center, faulty, overcharge"
            ),
            RightsInfo(
                situation="Unfair Debt Collection",
                rights="Recovery agents cannot harass you. They cannot call you at odd hours (before 8 AM, after 7 PM), use abusive language, or threaten you.",
                best_action="Do not get intimidated. Record the call (if legal in your state). Ask the agent to provide their ID and authorization letter. Complain to the bank and the RBI Ombudsman.",
                legal_section="RBI Guidelines on Recovery Agents",
                keywords="loan, emi, debt, collection, recovery, agent, harass, bank"
            ),
            RightsInfo(
                situation="Overcharged by Auto/Taxi",
                rights="Drivers must use the meter. They cannot charge more than the fare displayed. They cannot refuse a ride (in most cities).",
                best_action="Take a picture of the vehicle's number plate. Note the time and route. Pay the demanded fare if you feel unsafe, but immediately file a complaint with the regional transport office (RTO) or traffic police app.",
                legal_section="Motor Vehicles Act; State Transport Rules",
                keywords="auto, taxi, rickshaw, meter, overcharge, fare, refuse, ride"
            ),
            RightsInfo(
                situation="Property Purchase (Builder Delay)",
                rights="If a builder delays possession of your flat, you are entitled to compensation or a full refund with interest, as per your agreement and RERA rules.",
                best_action="Check your builder-buyer agreement for the possession date. File a complaint with the Real Estate Regulatory Authority (RERA) in your state. This is highly effective.",
                legal_section="Real Estate (Regulation and Development) Act, 2016 (RERA)",
                keywords="flat, apartment, builder, delay, possession, rera, property, refund"
            ),
            RightsInfo(
                situation="Wrongful Towing of Vehicle",
                rights="Your vehicle can only be towed from a designated 'No Parking' zone. Towing must be done by authorized personnel (traffic police) and not by private entities.",
                best_action="Look for 'No Parking' signs. If towed, go to the nearest traffic police chowki. You have to pay the fine, but you can file a complaint if you believe the towing was illegal or if your car was damaged.",
                legal_section="Motor Vehicles Act",
                keywords="car, bike, towed, towing, no parking, police, fine, traffic"
            ),
            RightsInfo(
                situation="Defamation (Online/Offline)",
                rights="You have the right to protect your reputation. Publishing false statements that harm your reputation is a civil and criminal offense.",
                best_action="Do not react publicly. Take screenshots or keep records. Send a legal notice to the person to retract the statement and apologize. You can then file a civil suit for damages or a criminal complaint.",
                legal_section="IPC Sec 499 (Defamation), 500 (Punishment)",
                keywords="defamation, slander, libel, false, reputation, online, post"
            ),
            RightsInfo(
                situation="Food Quality (Restaurant)",
                rights="You have the right to safe and hygienic food. Restaurants cannot serve stale food, add artificial colors, or have unhygienic kitchens.",
                best_action="Stop eating. Complain to the restaurant manager. Take photos if you see something (e.g., insect in food). Keep the bill. You can file a complaint with the Food Safety and Standards Authority of India (FSSAI).",
                legal_section="Food Safety and Standards Act, 2006 (FSSAI)",
                keywords="restaurant, food, quality, stale, unhygienic, sick, fssai, bill"

            ),
            RightsInfo(
                situation="Power Cut / Electricity Issues",
                rights="You have the right to a stable supply of electricity. You must be compensated for damages (e.g., to appliances) caused by voltage fluctuations, and notified of scheduled power cuts.",
                best_action="Note the time and duration of the outage. Complain to your electricity provider's helpline and get a complaint number. For appliance damage, file a claim with the provider; if rejected, go to the consumer forum.",
                legal_section="Electricity Act, 2003",
                keywords="power, cut, electricity, bill, outage, voltage, appliance, damaged"
            ),
            RightsInfo(
                situation="Pet Owner Disputes (Neighbours)",
                rights="You have the right to own a pet. A building society cannot ban you from having pets. However, you are responsible for cleaning up after your pet and controlling noise (barking).",
                best_action="Follow society rules on pet waste and leash use. If a neighbour harasses you, you can file a complaint with the Animal Welfare Board of India (AWBI). If your pet is a nuisance, the neighbour can complain.",
                legal_section="Animal Welfare Board of India (AWBI) Guidelines",
                keywords="pet, dog, cat, neighbour, society, barking, complaint, ban"
            ),
            RightsInfo(
                situation="Credit Score Error",
                rights="You have the right to an accurate credit report. You can dispute any errors (e.g., a loan you never took) with the credit bureau (CIBIL, Experian, etc.).",
                best_action="Get your credit report. Identify the error. File a dispute directly on the credit bureau's website. They are legally required to investigate and resolve it with the bank within 30 days.",
                legal_section="Credit Information Companies (Regulation) Act, 2005",
                keywords="cibil, credit, score, report, error, loan, dispute, experian"
            ),
            RightsInfo(
                situation="Insurance Claim Rejection",
                rights="Your insurance company cannot reject your claim for arbitrary or unstated reasons. They must clearly state the reason for rejection based on the policy terms.",
                best_action="Read your policy document carefully. Write a formal complaint to the insurance company's grievance cell. If unresolved, escalate the complaint to the Insurance Ombudsman.",
                legal_section="Insurance Regulatory and Development Authority of India (IRDAI)",
                keywords="insurance, claim, health, car, rejection, irdai, ombudsman, policy"
            ),
            RightsInfo(
                situation="Right to Vote",
                rights="If you are an eligible citizen and your name is on the voter list, you cannot be denied the right to vote. No one can force you to vote for a specific candidate.",
                best_action="Ensure your name is on the electoral roll beforehand. Carry your Voter ID (EPIC) card or another approved photo ID. If someone stops you, report it to the Presiding Officer at the polling booth or the police.",
                legal_section="Representation of the People Act, 1951",
                keywords="vote, election, voter, id, card, polling, booth, deny"
            ),

        ]
        
        db.session.bulk_save_objects(sample_data)
        db.session.commit()
        print("Sample data added.")

# Create database tables and add sample data
with app.app_context():
    db.create_all()
    add_sample_data() # Call the function to add data


# ===============================================
# === API ROUTES (These return JSON)
# ===============================================

# ===============================================
# === API ROUTES (These return JSON)
# ===============================================

# ===============================================
# === API ROUTES (These return JSON)
# ===============================================

# ===============================================
# === API ROUTES (These return JSON)
# ===============================================

@app.route('/api/search')
def api_search():
    user_input = request.args.get('q')
    results_list = []
    
    if user_input:
        # 1. Clean the input and get keywords (same as before)
        search_term = user_input.lower()
        words = search_term.split()
        keywords = [word for word in words if word not in STOP_WORDS]

        if keywords:
            # 2. Build scoring and filtering logic for both situation and keywords
            situation_score_expressions = []
            situation_filter_expressions = []
            
            keyword_score_expressions = []
            keyword_filter_expressions = []
            
            situation_weight = 5  # 5 points for a title match
            keywords_weight = 1   # 1 point for a keyword match

            for key in keywords:
                search_key = f"%{key}%"
                
                # Create expressions for matching
                situation_match = func.lower(RightsInfo.situation).like(search_key)
                keywords_match = func.lower(RightsInfo.keywords).like(search_key)
                
                # Add to SITUATION lists
                situation_score_expressions.append(case((situation_match, situation_weight), else_=0))
                situation_filter_expressions.append(situation_match)
                
                # Add to KEYWORD lists
                keyword_score_expressions.append(case((keywords_match, keywords_weight), else_=0))
                keyword_filter_expressions.append(keywords_match)

            # 3. Create the final "total_score" columns
            situation_total_score = sum(situation_score_expressions).label("total_score")
            keyword_total_score = sum(keyword_score_expressions).label("total_score")

            # --- 4. TIER 1 SEARCH: Try to "Resolve" by matching the SITUATION (Title) ---
            query = db.session.query(RightsInfo, situation_total_score)
            results = (
                query
                .filter(or_(*situation_filter_expressions)) # Must match at least one situation keyword
                .group_by(RightsInfo.id)
                .order_by(situation_total_score.desc()) # Order by highest score
                .all()
            )

            # 5. Check if Tier 1 was successful
            if results:
                # We found high-confidence matches! "Resolve" is complete.
                print("--- Tier 1 (Situation) search successful. ---")
                for item, score in results:
                    results_list.append({
                        "id": item.id,
                        "situation": item.situation,
                        "rights": item.rights,
                        "best_action": item.best_action,
                        "legal_section": item.legal_section
                    })
            else:
                # --- 6. TIER 2 SEARCH: Fallback to matching general KEYWORDS ---
                # No situation matches found. Run the search again on the keywords column.
                print("--- Tier 1 failed. Falling back to Tier 2 (Keyword) search. ---")
                query = db.session.query(RightsInfo, keyword_total_score)
                results = (
                    query
                    .filter(or_(*keyword_filter_expressions)) # Must match at least one keyword
                    .group_by(RightsInfo.id)
                    .order_by(keyword_total_score.desc()) # Order by highest score
                    .all()
                )
                
                for item, score in results:
                    results_list.append({
                        "id": item.id,
                        "situation": item.situation,
                        "rights": item.rights,
                        "best_action": item.best_action,
                        "legal_section": item.legal_section
                    })
    
    return jsonify(results_list)

# ... (rest of your app.py file: /signup, /login, etc.)

@app.route('/signup', methods = ['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"message": "Username already exists"}), 400
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"}), 200

@app.route('/login', methods = ['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        access_token = create_access_token(identity=username)
        return jsonify({"message": "Login successful!", "access_token": access_token}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401

@app.route('/user-info')
@jwt_required()
def user_info():
    current_user = get_jwt_identity()
    return jsonify({"username": current_user})

# ===============================================
# === PAGE SERVING ROUTES (These return HTML)
# ===============================================

# === HOMEPAGE ROUTE (CHANGED) ===
# This now serves your login page
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

# === LOGIN PAGE ROUTE (CHANGED) ===
# This also serves the login page, which is fine.
# Your login.js POSTs to this, which is correct.
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

# === NEW DASHBOARD ROUTE (CHANGED) ===
# This is the new home for your dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)