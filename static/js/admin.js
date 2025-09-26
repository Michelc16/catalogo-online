// Configuração da API
const API_BASE = window.location.origin + '/api';

// Verificar autenticação
async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE}/admin/users`, {
            credentials: 'include'  // 🔥 IMPORTANTE para cookies
        });
        
        if (!response.ok) {
            throw new Error('Erro de autenticação');
        }
        
        const data = await response.json();
        
        if (!data.user || !data.user.is_admin) {
            window.location.href = '/login';
            return false;
        }
        return true;
    } catch (error) {
        console.error('Erro ao verificar autenticação:', error);
        window.location.href = '/login';
        return false;
    }
}
// Gerenciar usuários
async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE}/admin/users`);
        if (!response.ok) throw new Error('Erro ao carregar usuários');
        
        const users = await response.json();
        displayUsers(users);
    } catch (error) {
        document.getElementById('users-list').innerHTML = `
            <div class="alert alert-danger">Erro ao carregar usuários: ${error.message}</div>
        `;
    }
}

function displayUsers(users) {
    const usersList = document.getElementById('users-list');
    
    if (users.length === 0) {
        usersList.innerHTML = '<p class="text-muted">Nenhum usuário encontrado</p>';
        return;
    }
    
    usersList.innerHTML = users.map(user => `
        <div class="d-flex justify-content-between align-items-center mb-3 p-3 border rounded">
            <div class="flex-grow-1">
                <div class="d-flex align-items-center mb-2">
                    <strong class="me-2">${user.username}</strong>
                    <span class="badge ${user.is_admin ? 'bg-success' : 'bg-secondary'}">
                        ${user.is_admin ? 'Administrador' : 'Usuário'}
                    </span>
                    <span class="badge ${user.is_active ? 'bg-primary' : 'bg-danger'} ms-1">
                        ${user.is_active ? 'Ativo' : 'Inativo'}
                    </span>
                </div>
                <div>
                    <small class="text-muted">${user.email}</small><br>
                    <small class="text-muted">ID: ${user.id} | Criado: ${new Date(user.created_at).toLocaleDateString('pt-BR')}</small>
                </div>
            </div>
            <div class="btn-group-vertical">
                ${user.id !== currentUser.id ? `
                    <button class="btn btn-sm ${user.is_active ? 'btn-warning' : 'btn-success'}" 
                            onclick="toggleUser(${user.id})" title="${user.is_active ? 'Desativar' : 'Ativar'}">
                        <i class="fas fa-${user.is_active ? 'pause' : 'play'}"></i>
                    </button>
                    ${user.is_admin ? `
                        <button class="btn btn-sm btn-secondary" onclick="demoteUser(${user.id})" title="Rebaixar para Usuário">
                            <i class="fas fa-arrow-down"></i>
                        </button>
                    ` : `
                        <button class="btn btn-sm btn-primary" onclick="promoteUser(${user.id})" title="Promover a Admin">
                            <i class="fas fa-arrow-up"></i>
                        </button>
                    `}
                ` : `
                    <small class="text-muted">Você</small>
                `}
            </div>
        </div>
    `).join('');
}

// Promover usuário a admin
async function promoteUser(userId) {
    if (!confirm('Tem certeza que deseja promover este usuário a administrador?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/admin/users/${userId}/promote`, {
            method: 'PUT'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage(result.message, 'success');
            loadUsers();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        showMessage('Erro: ' + error.message, 'error');
    }
}

// Rebaixar admin para usuário normal
async function demoteUser(userId) {
    if (!confirm('Tem certeza que deseja rebaixar este administrador para usuário comum?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/admin/users/${userId}/demote`, {
            method: 'PUT'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage(result.message, 'success');
            loadUsers();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        showMessage('Erro: ' + error.message, 'error');
    }
}

// Convidar admin
document.getElementById('invite-admin-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const button = this.querySelector('button');
    const originalText = button.innerHTML;
    
    try {
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
        button.disabled = true;
        
        const formData = {
            username: document.getElementById('invite-username').value.trim(),
            email: document.getElementById('invite-email').value.trim()
        };
        
        const response = await fetch(`${API_BASE}/admin/invite`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage(`Convite enviado! Senha temporária: <strong>${result.temporary_password}</strong> - Compartilhe com segurança!`, 'success');
            this.reset();
            loadUsers();
        } else {
            throw new Error(result.error);
        }
        
    } catch (error) {
        showMessage('Erro: ' + error.message, 'error');
    } finally {
        button.innerHTML = originalText;
        button.disabled = false;
    }
});

// Ativar/desativar usuário
async function toggleUser(userId) {
    if (!confirm('Tem certeza que deseja alterar o status deste usuário?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/admin/users/${userId}/toggle`, {
            method: 'PUT'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage(result.message, 'success');
            loadUsers();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        showMessage('Erro: ' + error.message, 'error');
    }
}

// Usuário atual
let currentUser = { id: 0 };

// Carregar usuário atual
async function loadCurrentUser() {
    try {
        const response = await fetch(`${API_BASE}/user`);
        const data = await response.json();
        if (data.user) {
            currentUser = data.user;
        }
    } catch (error) {
        console.error('Erro ao carregar usuário:', error);
    }
}

// Logout
async function logout() {
    try {
        await fetch(`${API_BASE}/logout`, { method: 'POST' });
        window.location.href = '/login';
    } catch (error) {
        console.error('Erro no logout:', error);
    }
}

// Mostrar seção específica
async function showSection(sectionName) {
    const isAuthenticated = await checkAuth();
    if (!isAuthenticated) return;

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
    
    // Verificar status do sistema
    await checkSystemStatus();
    
    // Carregar dados se necessário
    if (sectionName === 'products') {
        loadProductsTable();
    } else if (sectionName === 'users') {
        await loadUsers();
    }
}

// Adicione esta função para verificar o status do sistema:
async function checkSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/health`, {
            credentials: 'include'
        });
        const data = await response.json();
        
        const statusDiv = document.getElementById('system-status');
        if (data.status === 'OK') {
            statusDiv.innerHTML = '<small class="text-success"><i class="fas fa-check-circle"></i> Sistema Online</small>';
        } else {
            statusDiv.innerHTML = '<small class="text-danger"><i class="fas fa-exclamation-triangle"></i> Sistema com problemas</small>';
        }
    } catch (error) {
        document.getElementById('system-status').innerHTML = 
            '<small class="text-danger"><i class="fas fa-times-circle"></i> Erro de conexão</small>';
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
            <td colspan="7" class="text-center">
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
            <td colspan="7" class="text-center text-danger">
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

// Confirmar exclusão
function confirmDelete(productId, productName) {
    if (confirm(`Tem certeza que deseja excluir o produto "${productName}"?`)) {
        deleteProduct(productId);
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
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao excluir produto');
        }
        
        showMessage('Produto excluído com sucesso!', 'success');
        loadProductsTable();
        
    } catch (error) {
        console.error('Erro:', error);
        showMessage('Erro ao excluir produto: ' + error.message, 'error');
    }
}

// Mostrar mensagens
function showMessage(message, type = 'info') {
    const messageDiv = document.getElementById('message');
    messageDiv.innerHTML = `
        <div class="alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Adicionar no topo do main content
    const mainContent = document.querySelector('.main-content');
    const firstSection = mainContent.querySelector('.section');
    mainContent.insertBefore(messageDiv, firstSection);
    
    // Auto-remover após 5 segundos
    setTimeout(() => {
        const alert = messageDiv.querySelector('.alert');
        if (alert) {
            bootstrap.Alert.getOrCreateInstance(alert).close();
        }
    }, 5000);
}

// Função auxiliar para escapar HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Inicialização
document.addEventListener('DOMContentLoaded', async function() {
    const isAuthenticated = await checkAuth();
    
    if (isAuthenticated) {
        await loadCurrentUser();   // 🔥 garante que currentUser está setado
        await showSection('dashboard');
        
        document.getElementById('current-username').textContent = currentUser.username;
    }
});
