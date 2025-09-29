import os
import csv
from flask import Flask, request, jsonify, send_from_directory, render_template, session, redirect, url_for
from flask_cors import CORS
from models import db, Product, User
from werkzeug.utils import secure_filename
from PIL import Image
import secrets
from datetime import timedelta
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações básicas
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
    template_folder='templates', 
    static_folder='static',
    static_url_path=''
)

# 🔥 CONFIGURAÇÃO CORRIGIDA PARA RENDER
def get_database_uri():
    database_url = os.environ.get('DATABASE_URL', '')
    
    logger.info(f"🔍 DATABASE_URL encontrada: {database_url}")
    
    if database_url:
        # Corrige postgres:// para postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url
    else:
        # Fallback para SQLite
        sqlite_path = f"sqlite:///{os.path.join(basedir, 'catalogo.db')}"
        logger.info(f"🔍 Usando SQLite: {sqlite_path}")
        return sqlite_path

app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua-chave-secreta-muito-longa-aqui-12345')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# 🔥 CORS CONFIGURADO CORRETAMENTE PARA RENDER
CORS(app, 
    supports_credentials=True, 
    origins=[
        "https://catalogo-online-0196.onrender.com",
        "http://localhost:5000",
        "http://127.0.0.1:5000"
    ],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)

# Criar diretórios necessários
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/images', exist_ok=True)

db.init_app(app)

# ===== MIDDLEWARES DE SEGURANÇA =====
@app.after_request
def after_request(response):
    # Adicionar headers de segurança
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Login requerido"}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Login requerido"}), 401
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            return jsonify({"error": "Acesso admin requerido"}), 403
        return f(*args, **kwargs)
    return decorated_function

# ===== FUNÇÕES AUXILIARES MELHORADAS =====
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_product_data(data):
    """Valida dados do produto"""
    errors = []
    
    if not data.get('name') or not data['name'].strip():
        errors.append("Nome é obrigatório")
    
    try:
        price = float(data.get('price', 0))
        if price <= 0:
            errors.append("Preço deve ser maior que zero")
    except (ValueError, TypeError):
        errors.append("Preço deve ser um número válido")
    
    if len(data.get('name', '')) > 100:
        errors.append("Nome deve ter no máximo 100 caracteres")
    
    if len(data.get('category', '')) > 50:
        errors.append("Categoria deve ter no máximo 50 caracteres")
    
    return errors

def process_image(file):
    try:
        image = Image.open(file)
        # Otimizar imagem
        image.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
        # Converter para RGB se necessário
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        filename = secrets.token_hex(8) + '_' + secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Salvar com qualidade otimizada
        image.save(filepath, 'JPEG', quality=85, optimize=True)
        return filename
    except Exception as e:
        logger.error(f"Erro ao processar imagem: {str(e)}")
        raise Exception(f"Erro ao processar imagem: {str(e)}")

def process_csv(file):
    try:
        csv_content = file.stream.read().decode('utf-8').splitlines()
        csv_reader = csv.DictReader(csv_content)
        
        products_created = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                if 'name' not in row or 'price' not in row:
                    errors.append(f"Linha {row_num}: Colunas 'name' e 'price' são obrigatórias")
                    continue
                
                # Validar dados
                validation_errors = validate_product_data(row)
                if validation_errors:
                    errors.extend([f"Linha {row_num}: {error}" for error in validation_errors])
                    continue
                
                product = Product(
                    name=str(row['name']).strip(),
                    description=str(row.get('description', '')).strip(),
                    price=float(row['price']),
                    category=str(row.get('category', '')).strip(),
                    image_url=str(row.get('image_url', '')).strip()
                )
                db.session.add(product)
                products_created += 1
                
            except Exception as e:
                errors.append(f"Linha {row_num}: {str(e)}")
                continue
        
        if products_created > 0:
            db.session.commit()
        
        result_message = f"{products_created} produtos importados com sucesso"
        if errors:
            result_message += f". {len(errors)} erros encontrados: " + "; ".join(errors[:5])
            if len(errors) > 5:
                result_message += f" e mais {len(errors) - 5} erros..."
        
        return result_message
        
    except Exception as e:
        logger.error(f"Erro ao processar CSV: {str(e)}")
        raise Exception(f"Erro ao processar CSV: {str(e)}")

# ===== SOLUÇÃO 1: ROTA RAIZ ACEITANDO POST PARA WEBHOOK =====
@app.route('/', methods=['GET', 'POST'])
def catalog_page():
    if request.method == 'GET':
        # Sua lógica atual para exibir o catálogo
        return render_template('index.html')
    else:
        # Processar webhook da Umbler Talk
        try:
            data = request.get_json()
            if data:
                logger.info(f"📨 Webhook recebido na raiz: {data}")
                return jsonify({"status": "success", "message": "Webhook recebido com sucesso"}), 200
            else:
                # Se não for JSON, tentar form data
                form_data = request.form.to_dict()
                if form_data:
                    logger.info(f"📨 Webhook recebido (form): {form_data}")
                    return jsonify({"status": "success", "message": "Webhook recebido com sucesso"}), 200
                else:
                    logger.info("📨 Webhook recebido (vazio)")
                    return jsonify({"status": "success", "message": "Webhook recebido"}), 200
        except Exception as e:
            logger.error(f"❌ Erro ao processar webhook: {str(e)}")
            return jsonify({"status": "error", "message": f"Erro: {str(e)}"}), 400

# ===== SOLUÇÃO 2: ROTA ESPECÍFICA PARA WEBHOOKS =====
@app.route('/webhook/umbler', methods=['POST'])
def umbler_webhook():
    try:
        data = request.get_json()
        if data:
            logger.info(f"📨 Webhook da Umbler (JSON): {data}")
        else:
            form_data = request.form.to_dict()
            if form_data:
                logger.info(f"📨 Webhook da Umbler (form): {form_data}")
            else:
                logger.info("📨 Webhook da Umbler recebido (vazio)")
        
        # Processar os dados do webhook aqui
        # Ex: atualizar produtos, verificar estoque, etc.
        
        return jsonify({
            "status": "success", 
            "message": "Webhook da Umbler processado com sucesso"
        }), 200
    except Exception as e:
        logger.error(f"❌ Erro no webhook da Umbler: {e}")
        return jsonify({"status": "error", "message": f"Erro: {str(e)}"}), 400

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

# ===== ROTAS DE AUTENTICAÇÃO MELHORADAS =====
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'email' not in data or 'password' not in data:
            return jsonify({"error": "Username, email e password são obrigatórios"}), 400
        
        # Validações melhoradas
        username = data['username'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        if len(username) < 3:
            return jsonify({"error": "Username deve ter pelo menos 3 caracteres"}), 400
        
        if len(password) < 6:
            return jsonify({"error": "Password deve ter pelo menos 6 caracteres"}), 400
        
        if '@' not in email or '.' not in email:
            return jsonify({"error": "Email inválido"}), 400
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username já existe"}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email já cadastrado"}), 400
        
        # Criar primeiro usuário como admin
        is_first_user = User.query.count() == 0
        user = User(
            username=username,
            email=email,
            is_admin=is_first_user
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Login automático após registro
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        session.permanent = True
        
        logger.info(f"Novo usuário registrado: {username}")
        
        return jsonify({
            "message": "Usuário criado com sucesso", 
            "user": user.to_dict(),
            "is_admin": user.is_admin
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar usuário: {str(e)}")
        return jsonify({"error": f"Erro ao criar usuário: {str(e)}"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({"error": "Username e password são obrigatórios"}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({"error": "Username ou password incorretos"}), 401
        
        if not user.is_active:
            return jsonify({"error": "Usuário desativado"}), 401
        
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        session.permanent = True
        
        logger.info(f"Login realizado: {username}")
        
        return jsonify({
            "message": "Login realizado com sucesso",
            "user": user.to_dict(),
            "is_admin": user.is_admin
        })
        
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        return jsonify({"error": f"Erro no login: {str(e)}"}), 400

@app.route('/api/logout', methods=['POST'])
def logout():
    username = session.get('username', 'Desconhecido')
    session.clear()
    logger.info(f"Logout realizado: {username}")
    return jsonify({"message": "Logout realizado com sucesso"})

@app.route('/api/user')
def get_current_user():
    if 'user_id' not in session:
        return jsonify({"user": None})
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return jsonify({"user": None})
    
    return jsonify({"user": user.to_dict()})

# ===== CONFIGURAÇÃO DE SESSÃO PARA RENDER =====
@app.before_request
def make_session_permanent():
    session.permanent = True

# ===== ROTAS DE PERFIL =====
@app.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    try:
        user = User.query.get(session['user_id'])
        return jsonify({"user": user.to_dict()})
    except Exception as e:
        logger.error(f"Erro ao buscar perfil: {str(e)}")
        return jsonify({"error": f"Erro ao buscar perfil: {str(e)}"}), 500

@app.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    try:
        data = request.get_json()
        user = User.query.get(session['user_id'])
        
        if 'email' in data:
            email = data['email'].strip().lower()
            if '@' not in email or '.' not in email:
                return jsonify({"error": "Email inválido"}), 400
            
            existing_user = User.query.filter(User.email == email, User.id != user.id).first()
            if existing_user:
                return jsonify({"error": "Email já está em uso"}), 400
            user.email = email
        
        if 'username' in data:
            username = data['username'].strip()
            if len(username) < 3:
                return jsonify({"error": "Username deve ter pelo menos 3 caracteres"}), 400
            
            existing_user = User.query.filter(User.username == username, User.id != user.id).first()
            if existing_user:
                return jsonify({"error": "Username já está em uso"}), 400
            user.username = username
        
        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                return jsonify({"error": "Password deve ter pelo menos 6 caracteres"}), 400
            user.set_password(data['password'])
        
        db.session.commit()
        logger.info(f"Perfil atualizado: {user.username}")
        return jsonify({"message": "Perfil atualizado com sucesso", "user": user.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar perfil: {str(e)}")
        return jsonify({"error": f"Erro ao atualizar perfil: {str(e)}"}), 400

# ===== ROTAS DE ADMIN MELHORADAS =====
@app.route('/api/admin/invite', methods=['POST'])
@admin_required
def invite_admin():
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'username' not in data:
            return jsonify({"error": "Email e username são obrigatórios"}), 400
        
        email = data['email'].strip().lower()
        username = data['username'].strip()
        
        # Validações
        if '@' not in email or '.' not in email:
            return jsonify({"error": "Email inválido"}), 400
        
        if len(username) < 3:
            return jsonify({"error": "Username deve ter pelo menos 3 caracteres"}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email já cadastrado"}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username já existe"}), 400
        
        user = User(
            username=username,
            email=email,
            is_admin=True,
            invited_by=session['user_id']
        )
        temporary_password = secrets.token_urlsafe(12)
        user.set_password(temporary_password)
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"Admin convidado: {username} por {session['username']}")
        
        return jsonify({
            "message": "Administrador convidado com sucesso",
            "temporary_password": temporary_password,
            "user": user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao convidar admin: {str(e)}")
        return jsonify({"error": f"Erro ao convidar admin: {str(e)}"}), 400

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def list_users():
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        return jsonify([user.to_dict() for user in users])
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {str(e)}")
        return jsonify({"error": f"Erro ao listar usuários: {str(e)}"}), 500

# Novas rotas para promover/rebaixar usuários
@app.route('/api/admin/users/<int:user_id>/promote', methods=['PUT'])
@admin_required
def promote_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        if user.is_admin:
            return jsonify({"error": "Usuário já é administrador"}), 400
        
        user.is_admin = True
        db.session.commit()
        
        logger.info(f"Usuário promovido a admin: {user.username} por {session['username']}")
        return jsonify({"message": f"Usuário {user.username} promovido a administrador"})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao promover usuário: {str(e)}")
        return jsonify({"error": f"Erro ao promover usuário: {str(e)}"}), 400

@app.route('/api/admin/users/<int:user_id>/demote', methods=['PUT'])
@admin_required
def demote_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        if not user.is_admin:
            return jsonify({"error": "Usuário não é administrador"}), 400
        
        # Verificar se não é o último admin
        admin_count = User.query.filter_by(is_admin=True, is_active=True).count()
        if admin_count <= 1:
            return jsonify({"error": "Não é possível rebaixar o último administrador"}), 400
        
        user.is_admin = False
        db.session.commit()
        
        logger.info(f"Admin rebaixado: {user.username} por {session['username']}")
        return jsonify({"message": f"Administrador {user.username} rebaixado para usuário comum"})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao rebaixar usuário: {str(e)}")
        return jsonify({"error": f"Erro ao rebaixar usuário: {str(e)}"}), 400

@app.route('/api/admin/users/<int:user_id>/toggle', methods=['PUT'])
@admin_required
def toggle_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        # Não permitir desativar a si mesmo
        if user.id == session['user_id']:
            return jsonify({"error": "Você não pode desativar sua própria conta"}), 400
        
        # Se for admin ativo, verificar se não é o último
        if user.is_admin and user.is_active:
            admin_count = User.query.filter_by(is_admin=True, is_active=True).count()
            if admin_count <= 1:
                return jsonify({"error": "Não é possível desativar o último administrador ativo"}), 400
        
        user.is_active = not user.is_active
        db.session.commit()
        
        status = "ativado" if user.is_active else "desativado"
        logger.info(f"Usuário {status}: {user.username} por {session['username']}")
        
        return jsonify({"message": f"Usuário {user.username} {status} com sucesso"})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao alterar status do usuário: {str(e)}")
        return jsonify({"error": f"Erro ao alterar status do usuário: {str(e)}"}), 400

# ===== ROTAS PROTEGIDAS =====
@app.route('/admin')
def admin_page():
    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.query.get(session['user_id'])
    if not user or not user.is_admin or not user.is_active:
        return redirect('/login')
    
    return render_template('admin.html')

# ===== API DE PRODUTOS MELHORADA =====
@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        # Adicionar filtros opcionais
        category = request.args.get('category')
        search = request.args.get('search')
        
        query = Product.query
        
        if category and category != 'all':
            query = query.filter(Product.category == category)
        
        if search:
            query = query.filter(Product.name.contains(search))
        
        products = query.order_by(Product.created_at.desc()).all()
        return jsonify([product.to_dict() for product in products])
        
    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {str(e)}")
        return jsonify({"error": f"Erro ao buscar produtos: {str(e)}"}), 500

@app.route('/api/products', methods=['POST'])
@admin_required
def create_product():
    try:
        data = request.get_json()
        
        # Validar dados
        validation_errors = validate_product_data(data)
        if validation_errors:
            return jsonify({"error": "; ".join(validation_errors)}), 400
        
        product = Product(
            name=data['name'].strip(),
            description=data.get('description', '').strip(),
            price=float(data['price']),
            category=data.get('category', '').strip(),
            image_url=data.get('image_url', '').strip()
        )
        
        db.session.add(product)
        db.session.commit()
        
        logger.info(f"Produto criado: {product.name} por {session['username']}")
        return jsonify(product.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao criar produto: {str(e)}")
        return jsonify({"error": f"Erro ao criar produto: {str(e)}"}), 400

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Produto não encontrado"}), 404
        return jsonify(product.to_dict())
    except Exception as e:
        logger.error(f"Erro ao buscar produto: {str(e)}")
        return jsonify({"error": f"Erro ao buscar produto: {str(e)}"}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
@admin_required
def update_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Produto não encontrado"}), 404
        
        data = request.get_json()
        
        # Validar dados
        validation_errors = validate_product_data(data)
        if validation_errors:
            return jsonify({"error": "; ".join(validation_errors)}), 400
        
        product.name = data.get('name', product.name).strip()
        product.description = data.get('description', product.description).strip()
        product.price = float(data.get('price', product.price))
        product.category = data.get('category', product.category).strip()
        product.image_url = data.get('image_url', product.image_url).strip()
        
        db.session.commit()
        
        logger.info(f"Produto atualizado: {product.name} por {session['username']}")
        return jsonify(product.to_dict())
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao atualizar produto: {str(e)}")
        return jsonify({"error": f"Erro ao atualizar produto: {str(e)}"}), 400

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@admin_required
def delete_product(product_id):
    try:
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Produto não encontrado"}), 404
        
        # Remover arquivo de imagem se existir
        if product.image_url:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image_url)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    logger.warning(f"Erro ao remover imagem: {str(e)}")
        
        product_name = product.name
        db.session.delete(product)
        db.session.commit()
        
        logger.info(f"Produto deletado: {product_name} por {session['username']}")
        return jsonify({'message': 'Produto deletado com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao deletar produto: {str(e)}")
        return jsonify({"error": f"Erro ao deletar produto: {str(e)}"}), 400

@app.route('/api/upload', methods=['POST'])
@admin_required
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_ext = filename.rsplit('.', 1)[1].lower()
            
            if file_ext == 'csv':
                result_message = process_csv(file)
                logger.info(f"CSV importado por {session['username']}: {result_message}")
                return jsonify({'message': result_message})
            else:
                filename = process_image(file)
                logger.info(f"Imagem enviada por {session['username']}: {filename}")
                return jsonify({'filename': filename, 'message': 'Imagem enviada com sucesso'})
        
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
    except Exception as e:
        logger.error(f"Erro no upload: {str(e)}")
        return jsonify({'error': f'Erro no upload: {str(e)}'}), 500

# ===== ROTAS PÚBLICAS DA API =====
@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        categories = db.session.query(Product.category).distinct().all()
        categories_list = [cat[0] for cat in categories if cat[0] and cat[0].strip()]
        return jsonify(sorted(categories_list))
    except Exception as e:
        logger.error(f"Erro ao buscar categorias: {str(e)}")
        return jsonify({"error": f"Erro ao buscar categorias: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Testar conexão com banco
        db.session.execute('SELECT 1')
        db_status = True
    except Exception:
        db_status = False
    
    return jsonify({
        "status": "OK" if db_status else "ERROR", 
        "message": "API está funcionando corretamente" if db_status else "Problemas na conexão com banco",
        "database_connected": db_status
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ===== INICIALIZAÇÃO DO BANCO =====
def setup_database():
    """Configura o banco preservando dados existentes"""
    with app.app_context():
        try:
            db.create_all()
            logger.info("✅ Banco de dados inicializado!")
            
            # Criar usuário admin padrão se não existir
            if User.query.count() == 0:
                admin_user = User(
                    username="admin",
                    email="admin@catalogo.com",
                    is_admin=True
                )
                admin_user.set_password("admin123")
                db.session.add(admin_user)
                db.session.commit()
                logger.info("👤 Usuário admin criado: admin / admin123")
                
            # Verificar produtos
            product_count = Product.query.count()
            logger.info(f"📦 Total de produtos: {product_count}")
            
        except Exception as e:
            logger.error(f"❌ Erro durante inicialização do banco: {e}")

# Inicialização quando o app inicia
with app.app_context():
    try:
        setup_database()
    except Exception as e:
        logger.warning(f"⚠️ Aviso na inicialização: {e}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)