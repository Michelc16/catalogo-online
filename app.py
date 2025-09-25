import os
import csv
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from models import db, Product
from werkzeug.utils import secure_filename
from PIL import Image
import secrets

# Configurações básicas
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
    template_folder='templates', 
    static_folder='static',
    static_url_path=''
)

# Configuração do banco de dados
if os.environ.get('DATABASE_URL'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL'].replace('postgres://', 'postgresql://')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "catalogo.db")}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sua-chave-secreta-aqui-12345')

# Criar diretórios necessários
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/images', exist_ok=True)

db.init_app(app)
CORS(app)

# Extensões permitidas para upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(file):
    try:
        image = Image.open(file)
        image.thumbnail((800, 800))
        
        # Nome único para evitar conflitos
        filename = secrets.token_hex(8) + '_' + secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
        
        return filename
    except Exception as e:
        raise Exception(f"Erro ao processar imagem: {str(e)}")

def process_csv(file):
    try:
        # Ler arquivo CSV
        csv_content = file.stream.read().decode('utf-8').splitlines()
        csv_reader = csv.DictReader(csv_content)
        
        products_created = 0
        for row in csv_reader:
            try:
                # Verificar colunas obrigatórias
                if 'name' not in row or 'price' not in row:
                    continue
                
                product = Product(
                    name=str(row['name']),
                    description=str(row.get('description', '')),
                    price=float(row['price']),
                    category=str(row.get('category', '')),
                    image_url=str(row.get('image_url', ''))
                )
                db.session.add(product)
                products_created += 1
            except Exception as e:
                print(f"Erro ao processar linha: {e}")
                continue
        
        db.session.commit()
        return products_created
        
    except Exception as e:
        raise Exception(f"Erro ao processar CSV: {str(e)}")

# ===== ROTAS DAS PÁGINAS WEB =====
@app.route('/')
def catalog_page():
    return render_template('index.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

# ===== API ROUTES =====
@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        products = Product.query.all()
        return jsonify([product.to_dict() for product in products])
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar produtos: {str(e)}"}), 500

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get(product_id)
        if product is None:
            return jsonify({"error": "Produto não encontrado"}), 404
        return jsonify(product.to_dict())
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar produto: {str(e)}"}), 500

@app.route('/api/products', methods=['POST'])
def create_product():
    try:
        data = request.json
        if not data or 'name' not in data or 'price' not in data:
            return jsonify({"error": "Nome e preço são obrigatórios"}), 400
        
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            category=data.get('category', ''),
            image_url=data.get('image_url', '')
        )
        db.session.add(product)
        db.session.commit()
        return jsonify(product.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao criar produto: {str(e)}"}), 400

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        product = Product.query.get(product_id)
        if product is None:
            return jsonify({"error": "Produto não encontrado"}), 404
        
        data = request.json
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = float(data.get('price', product.price))
        product.category = data.get('category', product.category)
        product.image_url = data.get('image_url', product.image_url)
        
        db.session.commit()
        return jsonify(product.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao atualizar produto: {str(e)}"}), 400

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        product = Product.query.get(product_id)
        if product is None:
            return jsonify({"error": "Produto não encontrado"}), 404
        
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Produto deletado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao deletar produto: {str(e)}"}), 400

@app.route('/api/upload', methods=['POST'])
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
                # Processar arquivo CSV
                try:
                    products_created = process_csv(file)
                    return jsonify({'message': f'{products_created} produtos importados com sucesso'})
                except Exception as e:
                    return jsonify({'error': f'Erro ao processar arquivo: {str(e)}'}), 500
            
            else:
                # Processar imagem
                try:
                    filename = process_image(file)
                    return jsonify({'filename': filename, 'message': 'Imagem enviada com sucesso'})
                except Exception as e:
                    return jsonify({'error': f'Erro ao processar imagem: {str(e)}'}), 500
        
        return jsonify({'error': 'Tipo de arquivo não permitido'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Erro no upload: {str(e)}'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        categories = db.session.query(Product.category).distinct().all()
        categories_list = [cat[0] for cat in categories if cat[0] and cat[0].strip()]
        return jsonify(categories_list)
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar categorias: {str(e)}"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "message": "API está funcionando corretamente"})

# ===== INICIALIZAÇÃO =====
with app.app_context():
    db.create_all()
    print("✅ Sistema de Catálogo Online inicializado!")
    print(f"🌐 Modo: {'Produção' if os.environ.get('RENDER') else 'Desenvolvimento'}")
    print(f"📊 Dashboard: http://localhost:5000/admin")
    print(f"🛍️  Catálogo: http://localhost:5000/")
    print(f"💾 Banco: {app.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = not os.environ.get('RENDER')
    app.run(host='0.0.0.0', port=port, debug=debug)