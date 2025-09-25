// Configuração da API
const API_BASE = window.location.origin + '/api';

// Mostrar seção específica
function showSection(sectionName) {
    // Esconder todas as seções
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Mostrar seção selecionada
    const targetSection = document.getElementById(sectionName + '-section');
    if (targetSection) {
        targetSection.style.display = 'block';
    }
    
    // Atualizar menu ativo
    document.querySelectorAll('.sidebar .nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    const activeLink = document.querySelector(`.sidebar .nav-link[href="#"][onclick*="${sectionName}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
    
    // Carregar dados se necessário
    if (sectionName === 'products') {
        loadProductsTable();
    }
}

// Carregar tabela de produtos
async function loadProductsTable() {
    try {
        showTableLoading();
        
        const response = await fetch(`${API_BASE}/products`);
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        const products = await response.json();
        displayProductsTable(products);
        
    } catch (error) {
        console.error('Erro ao carregar produtos:', error);
        showTableError(error.message);
    }
}

// Mostrar loading na tabela
function showTableLoading() {
    const tableBody = document.getElementById('products-table');
    tableBody.innerHTML = `
        <tr>
            <td colspan="6" class="text-center">
                <div class="spinner-border spinner-border-sm" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
                Carregando produtos...
            </td>
        </tr>
    `;
}

// Mostrar erro na tabela
function showTableError(message) {
    const tableBody = document.getElementById('products-table');
    tableBody.innerHTML = `
        <tr>
            <td colspan="6" class="text-center text-danger">
                <i class="fas fa-exclamation-triangle"></i> Erro ao carregar produtos: ${message}
                <br><small>Verifique se a API está respondendo</small>
                <br><button class="btn btn-sm btn-primary mt-2" onclick="loadProductsTable()">
                    <i class="fas fa-redo"></i> Tentar Novamente
                </button>
            </td>
        </tr>
    `;
}

// Exibir produtos na tabela
function displayProductsTable(products) {
    const tableBody = document.getElementById('products-table');
    
    if (products.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">
                    <i class="fas fa-box-open fa-2x mb-2 d-block"></i>
                    Nenhum produto cadastrado
                    <br><small>Adicione seu primeiro produto usando o formulário ao lado</small>
                </td>
            </tr>
        `;
        return;
    }
    
    tableBody.innerHTML = '';
    
    products.forEach(product => {
        const row = document.createElement('tr');
        
        const imageUrl = product.image_url 
            ? `${API_BASE.replace('/api', '')}/uploads/${product.image_url}`
            : 'https://via.placeholder.com/50x50?text=Sem+Imagem';
        
        row.innerHTML = `
            <td>${product.id}</td>
            <td>
                <img src="${imageUrl}" 
                     width="50" height="50" 
                     style="object-fit: cover; border-radius: 5px;"
                     onerror="this.src='https://via.placeholder.com/50x50?text=Erro'"
                     alt="${product.name}">
            </td>
            <td>${escapeHtml(product.name)}</td>
            <td><strong class="text-success">R$ ${product.price.toFixed(2)}</strong></td>
            <td>${product.category ? `<span class="badge bg-secondary">${escapeHtml(product.category)}</span>` : '-'}</td>
            <td class="table-actions">
                <button class="btn btn-sm btn-warning" onclick="editProduct(${product.id})" title="Editar">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteProduct(${product.id})" title="Excluir">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Adicionar novo produto
document.getElementById('add-product-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const submitButton = this.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    
    try {
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adicionando...';
        submitButton.disabled = true;
        
        const productData = {
            name: document.getElementById('product-name').value.trim(),
            description: document.getElementById('product-description').value.trim(),
            price: parseFloat(document.getElementById('product-price').value),
            category: document.getElementById('product-category').value.trim(),
            image_url: ''
        };
        
        // Validar dados
        if (!productData.name || !productData.price) {
            throw new Error('Nome e preço são obrigatórios');
        }
        
        const imageFile = document.getElementById('product-image').files[0];
        
        // Upload de imagem se existir
        if (imageFile) {
            const formData = new FormData();
            formData.append('file', imageFile);
            
            const uploadResponse = await fetch(`${API_BASE}/upload`, {
                method: 'POST',
                body: formData
            });
            
            if (!uploadResponse.ok) {
                const error = await uploadResponse.json();
                throw new Error(error.error || 'Erro no upload da imagem');
            }
            
            const uploadResult = await uploadResponse.json();
            productData.image_url = uploadResult.filename;
        }
        
        // Criar produto
        const response = await fetch(`${API_BASE}/products`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(productData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao adicionar produto');
        }
        
        showMessage('Produto adicionado com sucesso!', 'success');
        document.getElementById('add-product-form').reset();
        loadProductsTable();
        showSection('products');
        
    } catch (error) {
        console.error('Erro:', error);
        showMessage('Erro ao adicionar produto: ' + error.message, 'error');
    } finally {
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    }
});

// Importar produtos
document.getElementById('import-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const submitButton = this.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    
    try {
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Importando...';
        submitButton.disabled = true;
        
        const file = document.getElementById('import-file').files[0];
        if (!file) {
            throw new Error('Selecione um arquivo CSV');
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage(result.message, 'success');
            document.getElementById('import-form').reset();
            loadProductsTable();
            showSection('products');
        } else {
            throw new Error(result.error || 'Erro ao importar produtos');
        }
        
    } catch (error) {
        console.error('Erro:', error);
        showMessage('Erro ao importar produtos: ' + error.message, 'error');
    } finally {
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    }
});

// Editar produto
async function editProduct(productId) {
    try {
        const response = await fetch(`${API_BASE}/products/${productId}`);
        
        if (!response.ok) {
            throw new Error('Produto não encontrado');
        }
        
        const product = await response.json();
        
        document.getElementById('edit-product-id').value = product.id;
        document.getElementById('edit-product-name').value = product.name;
        document.getElementById('edit-product-description').value = product.description || '';
        document.getElementById('edit-product-price').value = product.price;
        document.getElementById('edit-product-category').value = product.category || '';
        document.getElementById('edit-product-image').value = product.image_url || '';
        
        new bootstrap.Modal(document.getElementById('editProductModal')).show();
        
    } catch (error) {
        console.error('Erro ao carregar produto:', error);
        showMessage('Erro ao carregar produto: ' + error.message, 'error');
    }
}

// Atualizar produto
async function updateProduct() {
    const submitButton = document.querySelector('#editProductModal .btn-primary');
    const originalText = submitButton.innerHTML;
    
    try {
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Salvando...';
        submitButton.disabled = true;
        
        const productId = document.getElementById('edit-product-id').value;
        const productData = {
            name: document.getElementById('edit-product-name').value.trim(),
            description: document.getElementById('edit-product-description').value.trim(),
            price: parseFloat(document.getElementById('edit-product-price').value),
            category: document.getElementById('edit-product-category').value.trim(),
            image_url: document.getElementById('edit-product-image').value.trim()
        };
        
        // Validar dados
        if (!productData.name || !productData.price) {
            throw new Error('Nome e preço são obrigatórios');
        }
        
        const response = await fetch(`${API_BASE}/products/${productId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(productData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao atualizar produto');
        }
        
        bootstrap.Modal.getInstance(document.getElementById('editProductModal')).hide();
        showMessage('Produto atualizado com sucesso!', 'success');
        loadProductsTable();
        
    } catch (error) {
        console.error('Erro:', error);
        showMessage('Erro ao atualizar produto: ' + error.message, 'error');
    } finally {
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    }
}

// Excluir produto
async function deleteProduct(productId) {
    if (!confirm('Tem certeza que deseja excluir este produto? Esta ação não pode ser desfeita.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/products/${productId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showMessage('Produto excluído com sucesso!', 'success');
            loadProductsTable();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao excluir produto');
        }
        
    } catch (error) {
        console.error('Erro:', error);
        showMessage('Erro ao excluir produto: ' + error.message, 'error');
    }
}

// Utility: Mostrar mensagem
function showMessage(message, type) {
    // Remover mensagens anteriores
    const existingMessages = document.querySelectorAll('.alert-message');
    existingMessages.forEach(msg => msg.remove());
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-message mt-3`;
    messageDiv.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'check-circle'}"></i>
        ${message}
        <button type="button" class="btn-close float-end" data-bs-dismiss="alert"></button>
    `;
    
    // Adicionar no topo do main content
    const mainContent = document.querySelector('.main-content');
    const firstSection = mainContent.querySelector('.section');
    mainContent.insertBefore(messageDiv, firstSection);
    
    // Auto-remover após 5 segundos
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.remove();
        }
    }, 5000);
}

// Utility: Escapar HTML
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
    loadProductsTable();
    
    // Configurar fechamento de mensagens
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-close')) {
            e.target.closest('.alert').remove();
        }
    });
});
// Calcular estatísticas
function calculateStats(products) {
    const totalProducts = products.length;
    const categories = [...new Set(products.map(p => p.category).filter(c => c))];
    const productsWithImages = products.filter(p => p.image_url).length;
    const avgPrice = products.length > 0 
        ? products.reduce((sum, p) => sum + p.price, 0) / products.length 
        : 0;

    // Atualizar elementos
    document.getElementById('total-products').textContent = totalProducts;
    document.getElementById('total-categories').textContent = categories.length;
    document.getElementById('products-with-images').textContent = productsWithImages;
    document.getElementById('avg-price').textContent = 'R$ ' + avgPrice.toFixed(2);
    document.getElementById('products-count').textContent = totalProducts + ' produtos';
    
    // Mostrar seção de estatísticas
    document.getElementById('stats-section').style.display = 'flex';
}

// Atualizar a função displayProductsTable para incluir estatísticas
function displayProductsTable(products) {
    const tableBody = document.getElementById('products-table');
    
    if (products.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center text-muted py-5">
                    <i class="fas fa-box-open fa-3x mb-3 d-block"></i>
                    <h5>Nenhum produto cadastrado</h5>
                    <p class="mb-0">Adicione seu primeiro produto usando o formulário acima</p>
                </td>
            </tr>
        `;
        
        // Esconder estatísticas se não há produtos
        document.getElementById('stats-section').style.display = 'none';
        document.getElementById('products-count').textContent = '0 produtos';
        return;
    }
    
    tableBody.innerHTML = '';
    
    products.forEach(product => {
        const row = document.createElement('tr');
        
        const imageUrl = product.image_url 
            ? `${API_BASE.replace('/api', '')}/uploads/${product.image_url}`
            : 'https://via.placeholder.com/50x50?text=Sem+Imagem';
        
        const createdDate = new Date(product.created_at).toLocaleDateString('pt-BR');
        
        row.innerHTML = `
            <td><span class="badge bg-secondary">#${product.id}</span></td>
            <td>
                <img src="${imageUrl}" 
                     width="50" height="50" 
                     style="object-fit: cover; border-radius: 5px;"
                     onerror="this.src='https://via.placeholder.com/50x50?text=Erro'"
                     alt="${product.name}"
                     class="img-thumbnail">
            </td>
            <td>
                <strong>${escapeHtml(product.name)}</strong>
                ${product.description ? `<br><small class="text-muted">${escapeHtml(product.description.substring(0, 50))}...</small>` : ''}
            </td>
            <td><span class="badge bg-success">R$ ${product.price.toFixed(2)}</span></td>
            <td>${product.category ? `<span class="badge bg-primary">${escapeHtml(product.category)}</span>` : '<span class="text-muted">-</span>'}</td>
            <td><small class="text-muted">${createdDate}</small></td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-warning" onclick="editProduct(${product.id})" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="confirmDelete(${product.id}, '${escapeHtml(product.name)}')" title="Excluir">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Calcular e mostrar estatísticas
    calculateStats(products);
}

// Função de confirmação de exclusão
function confirmDelete(productId, productName) {
    document.getElementById('delete-product-name').textContent = productName;
    
    const confirmBtn = document.getElementById('confirm-delete-btn');
    confirmBtn.onclick = function() {
        deleteProduct(productId);
    };
    
    new bootstrap.Modal(document.getElementById('deleteConfirmModal')).show();
}

// Atualizar a função deleteProduct para fechar o modal
async function deleteProduct(productId) {
    const modal = bootstrap.Modal.getInstance(document.getElementById('deleteConfirmModal'));
    
    try {
        const response = await fetch(`${API_BASE}/products/${productId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            modal.hide();
            showMessage('Produto excluído com sucesso!', 'success');
            loadProductsTable();
        } else {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao excluir produto');
        }
        
    } catch (error) {
        console.error('Erro:', error);
        showMessage('Erro ao excluir produto: ' + error.message, 'error');
    }
}