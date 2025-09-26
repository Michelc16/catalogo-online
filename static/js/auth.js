// Configuração da API
const API_BASE = window.location.origin + '/api';

// Verificar autenticação
async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE}/user`);
        const data = await response.json();
        
        if (data.user) {
            // Usuário está logado, redirecionar para admin se for admin
            if (data.user.is_admin) {
                window.location.href = '/admin';
            } else {
                window.location.href = '/';
            }
            return true;
        }
        return false;
    } catch (error) {
        console.error('Erro ao verificar autenticação:', error);
        return false;
    }
}

// Login
document.getElementById('login-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const submitButton = this.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    
    try {
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Entrando...';
        submitButton.disabled = true;
        
        const formData = {
            username: document.getElementById('username').value.trim(),
            password: document.getElementById('password').value
        };
        
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('Login realizado com sucesso!', 'success');
            
            // Redirecionar após login
            setTimeout(() => {
                if (result.user.is_admin) {
                    window.location.href = '/admin';
                } else {
                    window.location.href = '/';
                }
            }, 1000);
            
        } else {
            throw new Error(result.error);
        }
        
    } catch (error) {
        showMessage('Erro: ' + error.message, 'error');
    } finally {
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    }
});

// Registro
document.getElementById('register-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const submitButton = this.querySelector('button[type="submit"]');
    const originalText = submitButton.innerHTML;
    
    try {
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Registrando...';
        submitButton.disabled = true;
        
        const formData = {
            username: document.getElementById('reg-username').value.trim(),
            email: document.getElementById('reg-email').value.trim(),
            password: document.getElementById('reg-password').value
        };
        
        // Validar senha
        if (formData.password.length < 6) {
            throw new Error('A senha deve ter pelo menos 6 caracteres');
        }
        
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showMessage('Registro realizado com sucesso!', 'success');
            
            // Redirecionar após registro
            setTimeout(() => {
                if (result.user.is_admin) {
                    window.location.href = '/admin';
                } else {
                    window.location.href = '/';
                }
            }, 1000);
            
        } else {
            throw new Error(result.error);
        }
        
    } catch (error) {
        showMessage('Erro: ' + error.message, 'error');
    } finally {
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    }
});

// Mostrar mensagens
function showMessage(message, type = 'info') {
    const messageDiv = document.getElementById('message');
    messageDiv.innerHTML = `
        <div class="alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
}

// Alternar entre login e registro
function showLoginForm() {
    document.getElementById('login-section').style.display = 'block';
    document.getElementById('register-section').style.display = 'none';
}

function showRegisterForm() {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('register-section').style.display = 'block';
}

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se já está logado
    checkAuth();
});