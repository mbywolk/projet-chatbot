from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app import app, db
from models import User, Conversation, Message
from gemini_service import get_chat_response
import logging

@app.route('/')
def index():
    """Main route - shows splash screen or redirects to home if logged in"""
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('splash.html')

@app.route('/auth')
def auth():
    """Authentication page with login and register forms"""
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('auth.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle user login"""
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        flash('Veuillez remplir tous les champs', 'error')
        return redirect(url_for('auth'))
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        session['user_id'] = user.id
        session['user_name'] = user.get_full_name()
        flash(f'Bienvenue {user.get_full_name()}!', 'success')
        return redirect(url_for('home'))
    else:
        flash('Email ou mot de passe incorrect', 'error')
        return redirect(url_for('auth'))

@app.route('/register', methods=['POST'])
def register():
    """Handle user registration"""
    nom = request.form.get('nom')
    postnom = request.form.get('postnom')
    prenom = request.form.get('prenom')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    # Validation
    if not all([nom, postnom, prenom, email, password, confirm_password]):
        flash('Veuillez remplir tous les champs', 'error')
        return redirect(url_for('auth'))
    
    if password != confirm_password:
        flash('Les mots de passe ne correspondent pas', 'error')
        return redirect(url_for('auth'))
    
    if len(password) < 6:
        flash('Le mot de passe doit contenir au moins 6 caractères', 'error')
        return redirect(url_for('auth'))
    
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        flash('Un compte avec cet email existe déjà', 'error')
        return redirect(url_for('auth'))
    
    # Create new user
    user = User(nom=nom, postnom=postnom, prenom=prenom, email=email)
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        session['user_name'] = user.get_full_name()
        flash('Compte créé avec succès!', 'success')
        return redirect(url_for('home'))
    except Exception as e:
        db.session.rollback()
        logging.error(f"Registration error: {e}")
        flash('Erreur lors de la création du compte', 'error')
        return redirect(url_for('auth'))

@app.route('/home')
def home():
    """Home page with chatbot presentation"""
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth'))
    
    return render_template('home.html', user=user)

@app.route('/chat')
@app.route('/chat/<int:conversation_id>')
def chat(conversation_id=None):
    """Chat interface"""
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth'))
    
    conversation = None
    messages = []
    
    if conversation_id:
        conversation = Conversation.query.filter_by(id=conversation_id, user_id=user.id).first()
        if conversation:
            messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.timestamp).all()
    
    return render_template('chat.html', user=user, conversation=conversation, messages=messages)

@app.route('/new_conversation', methods=['POST'])
def new_conversation():
    """Create a new conversation"""
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth'))
    
    conversation = Conversation(user_id=user.id)
    
    try:
        db.session.add(conversation)
        db.session.commit()
        return redirect(url_for('chat', conversation_id=conversation.id))
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating conversation: {e}")
        flash('Erreur lors de la création de la conversation', 'error')
        return redirect(url_for('home'))

@app.route('/send_message', methods=['POST'])
def send_message():
    """Send a message in the chat"""
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorisé'}), 401
    
    conversation_id = request.form.get('conversation_id')
    message_content = request.form.get('message')
    
    if not conversation_id or not message_content:
        return jsonify({'error': 'Données manquantes'}), 400
    
    user = User.query.get(session['user_id'])
    conversation = Conversation.query.filter_by(id=conversation_id, user_id=user.id).first()
    
    if not conversation:
        return jsonify({'error': 'Conversation non trouvée'}), 404
    
    try:
        # Save user message
        user_message = Message(
            content=message_content,
            is_user=True,
            conversation_id=conversation.id
        )
        db.session.add(user_message)
        
        # Get bot response
        bot_response = get_chat_response(message_content, conversation.id)
        
        # Save bot message
        bot_message = Message(
            content=bot_response,
            is_user=False,
            conversation_id=conversation.id
        )
        db.session.add(bot_message)
        
        # Update conversation title if it's the first message
        if conversation.title == "Nouvelle conversation":
            # Use first few words of the message as title
            title_words = message_content.split()[:5]
            conversation.title = ' '.join(title_words) + ('...' if len(title_words) == 5 else '')
        
        db.session.commit()
        
        return redirect(url_for('chat', conversation_id=conversation.id))
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error sending message: {e}")
        flash('Erreur lors de l\'envoi du message', 'error')
        return redirect(url_for('chat', conversation_id=conversation_id))

@app.route('/profile')
def profile():
    """User profile page with conversation history"""
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth'))
    
    conversations = Conversation.query.filter_by(user_id=user.id).order_by(Conversation.updated_at.desc()).all()
    
    return render_template('profile.html', user=user, conversations=conversations)

@app.route('/delete_conversation/<int:conversation_id>', methods=['POST'])
def delete_conversation(conversation_id):
    """Delete a conversation"""
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    user = User.query.get(session['user_id'])
    conversation = Conversation.query.filter_by(id=conversation_id, user_id=user.id).first()
    
    if conversation:
        try:
            db.session.delete(conversation)
            db.session.commit()
            flash('Conversation supprimée', 'success')
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error deleting conversation: {e}")
            flash('Erreur lors de la suppression', 'error')
    
    return redirect(url_for('profile'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    """Update user profile"""
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth'))
    
    nom = request.form.get('nom')
    postnom = request.form.get('postnom')
    prenom = request.form.get('prenom')
    email = request.form.get('email')
    
    if not all([nom, postnom, prenom, email]):
        flash('Veuillez remplir tous les champs', 'error')
        return redirect(url_for('profile'))
    
    # Check if email is already taken by another user
    existing_user = User.query.filter_by(email=email).first()
    if existing_user and existing_user.id != user.id:
        flash('Cet email est déjà utilisé par un autre compte', 'error')
        return redirect(url_for('profile'))
    
    try:
        user.nom = nom
        user.postnom = postnom
        user.prenom = prenom
        user.email = email
        
        db.session.commit()
        session['user_name'] = user.get_full_name()
        flash('Profil mis à jour avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating profile: {e}")
        flash('Erreur lors de la mise à jour', 'error')
    
    return redirect(url_for('profile'))

@app.route('/settings')
def settings():
    """Settings page"""
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth'))
    
    return render_template('settings.html', user=user)

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('index'))

@app.route('/change_password', methods=['POST'])
def change_password():
    """Change user password"""
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth'))
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        flash('Veuillez remplir tous les champs', 'error')
        return redirect(url_for('settings'))
    
    if not user.check_password(current_password):
        flash('Mot de passe actuel incorrect', 'error')
        return redirect(url_for('settings'))
    
    if new_password != confirm_password:
        flash('Les nouveaux mots de passe ne correspondent pas', 'error')
        return redirect(url_for('settings'))
    
    if len(new_password) < 6:
        flash('Le nouveau mot de passe doit contenir au moins 6 caractères', 'error')
        return redirect(url_for('settings'))
    
    try:
        user.set_password(new_password)
        db.session.commit()
        flash('Mot de passe modifié avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error changing password: {e}")
        flash('Erreur lors de la modification du mot de passe', 'error')
    
    return redirect(url_for('settings'))
