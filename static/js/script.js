// Configuração da API
const API_BASE = window.location.origin + '/api';

// Elementos DOM
const productsContainer = document.getElementById('products-container');
const categoryFilter = document.querySelector('.category-filter');

// Carregar produtos
async function loadProducts(category = 'all') {
    try {
        showLoading();
        
        const response = await fetch(`${API_BASE}/products`);
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const products = await response.json();
        displayProducts(products, category);
        updateCategoryFilter(products);
        
    } catch (error) {
        console.error('Erro ao carregar produtos:', error);
        showError('Erro ao carregar produtos. Tente novamente mais tarde.');
    }
}

// Mostrar loading
function showLoading() {
    productsContainer.innerHTML = `
        <div class="col-12 text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="mt-2">Carregando produtos...</p>
        </div>
    `;
}

// Mostrar erro
function showError(message) {
    productsContainer.innerHTML = `
        <div class="col-12 text-center">
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle"></i> ${message}
            </div>
            <button class="btn btn-primary" onclick="loadProducts()">
                <i class="fas fa-redo"></i> Tentar Novamente
            </button>
        </div>
    `;
}

// Exibir produtos
function displayProducts(products, category) {
    productsContainer.innerHTML = '';
    
    const filteredProducts = category === 'all' 
        ? products 
        : products.filter(product => product.category === category);
    
    if (filteredProducts.length === 0) {
        productsContainer.innerHTML = `
            <div class="col-12">
                <div class="empty-state">
                    <i class="fas fa-box-open"></i>
                    <h4>Nenhum produto encontrado</h4>
                    <p>${category === 'all' ? 'Não há produtos cadastrados no momento.' : 'Nenhum produto nesta categoria.'}</p>
                </div>
            </div>
        `;
        return;
    }
    
    filteredProducts.forEach(product => {
        const productCard = createProductCard(product);
        productsContainer.appendChild(productCard);
    });
}

// Criar card do produto
function createProductCard(product) {
    const col = document.createElement('div');
    col.className = 'col-md-6 col-lg-4 col-xl-3 mb-4';
    
    const imageUrl = product.image_url 
        ? `${API_BASE.replace('/api', '')}/uploads/${product.image_url}`
        : 'https://via.placeholder.com/300x200?text=Sem+Imagem';
    
    col.innerHTML = `
        <div class="card product-card h-100">
            <img src="${imageUrl}" 
                 class="card-img-top product-image" 
                 alt="${product.name}"
                 onerror="this.src='https://via.placeholder.com/300x200?text=Imagem+Não+Carregada'">
            <div class="card-body d-flex flex-column">
                <h5 class="card-title">${escapeHtml(product.name)}</h5>
                <p class="card-text flex-grow-1 text-muted">${escapeHtml(product.description || 'Sem descrição')}</p>
                <div class="mt-auto">
                    <p class="card-text"><strong class="h5 text-primary">R$ ${product.price.toFixed(2)}</strong></p>
                    ${product.category ? `<span class="badge bg-secondary mb-2">${escapeHtml(product.category)}</span>` : ''}
                    <button class="btn btn-primary btn-sm w-100" onclick="showProductDetails(${product.id})">
                        <i class="fas fa-eye"></i> Ver Detalhes
                    </button>
                </div>
            </div>
        </div>
    `;
    
    return col;
}

// Atualizar filtro de categorias
function updateCategoryFilter(products) {
    const categories = [...new Set(products.map(p => p.category).filter(c => c))];
    
    // Limpar botões existentes (exceto "Todos")
    const existingButtons = categoryFilter.querySelectorAll('button:not([data-category="all"])');
    existingButtons.forEach(btn => btn.remove());
    
    categories.forEach(category => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-outline-primary ms-1 mb-1';
        button.textContent = category;
        button.setAttribute('data-category', category);
        button.onclick = (e) => filterByCategory(category, e);
        
        categoryFilter.appendChild(button);
    });
}

// Filtrar por categoria
function filterByCategory(category, event) {
    // Atualizar botões ativos
    document.querySelectorAll('.category-filter button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    const target = event ? event.target : document.querySelector(`[data-category="${category}"]`);
    if (target) target.classList.add('active');
    
    loadProducts(category);
}

// Mostrar detalhes do produto
async function showProductDetails(productId) {
    try {
        const response = await fetch(`${API_BASE}/products/${productId}`);
        
        if (!response.ok) {
            throw new Error('Produto não encontrado');
        }
        
        const product = await response.json();
        
        const imageUrl = product.image_url 
            ? `${API_BASE.replace('/api', '')}/uploads/${product.image_url}`
            : 'https://via.placeholder.com/400x300?text=Sem+Imagem';
        
        document.getElementById('productModalTitle').textContent = product.name;
        document.getElementById('productModalBody').innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <img src="${imageUrl}" 
                         class="img-fluid rounded" 
                         alt="${product.name}"
                         onerror="this.src='https://via.placeholder.com/400x300?text=Imagem+Não+Carregada'">
                </div>
                <div class="col-md-6">
                    <h4 class="text-primary">${escapeHtml(product.name)}</h4>
                    <p class="text-muted">${escapeHtml(product.description || 'Sem descrição')}</p>
                    <p><strong class="h5">Preço: R$ ${product.price.toFixed(2)}</strong></p>
                    ${product.category ? `<p><strong>Categoria:</strong> <span class="badge bg-secondary">${escapeHtml(product.category)}</span></p>` : ''}
                    <p class="text-muted"><small>Atualizado em: ${new Date(product.updated_at).toLocaleDateString('pt-BR')}</small></p>
                </div>
            </div>
        `;
        
        new bootstrap.Modal(document.getElementById('productModal')).show();
        
    } catch (error) {
        console.error('Erro ao carregar detalhes do produto:', error);
        alert('Erro ao carregar detalhes do produto: ' + error.message);
    }
}

// Utility: Escapar HTML para prevenir XSS
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    loadProducts();
    
    // Configurar botão "Todos"
    const allButton = document.querySelector('[data-category="all"]');
    if (allButton) {
        allButton.onclick = (e) => filterByCategory('all', e);
    }
});