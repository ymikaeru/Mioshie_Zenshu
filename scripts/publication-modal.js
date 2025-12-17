/**
 * Publication Modal Component
 * Modal for creating and selecting publications
 */

const PublicationModal = (function () {
    let modalElement = null;
    let currentArticle = null;
    let onSuccessCallback = null;

    // CSS styles for the modal
    const styles = `
        .pub-modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(4px);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            animation: pubModalFadeIn 0.2s ease-out;
        }

        @keyframes pubModalFadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .pub-modal-window {
            background: white;
            border-radius: 12px;
            width: 90%;
            max-width: 450px;
            max-height: 80vh;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
            animation: pubModalSlideUp 0.3s ease-out;
        }

        @keyframes pubModalSlideUp {
            from { transform: translateY(20px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }

        .pub-modal-header {
            padding: 1.25rem 1.5rem;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .pub-modal-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1a202c;
            margin: 0;
        }

        .pub-modal-close {
            background: none;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            color: #718096;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            transition: all 0.2s;
        }

        .pub-modal-close:hover {
            background: #f7fafc;
            color: #1a202c;
        }

        .pub-modal-body {
            padding: 1.5rem;
            overflow-y: auto;
            max-height: 50vh;
        }

        .pub-modal-section {
            margin-bottom: 1.5rem;
        }

        .pub-modal-section:last-child {
            margin-bottom: 0;
        }

        .pub-modal-section-title {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #718096;
            margin-bottom: 0.75rem;
            font-weight: 600;
        }

        .pub-modal-input-group {
            display: flex;
            gap: 0.5rem;
        }

        .pub-modal-input {
            flex: 1;
            padding: 0.75rem 1rem;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            font-size: 0.95rem;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .pub-modal-input:focus {
            outline: none;
            border-color: #6b5b95;
            box-shadow: 0 0 0 3px rgba(107, 91, 149, 0.1);
        }

        .pub-modal-btn {
            padding: 0.75rem 1.25rem;
            border: none;
            border-radius: 8px;
            font-size: 0.95rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }

        .pub-modal-btn-primary {
            background: #6b5b95;
            color: white;
        }

        .pub-modal-btn-primary:hover {
            background: #5a4a7e;
        }

        .pub-modal-btn-primary:disabled {
            background: #a0aec0;
            cursor: not-allowed;
        }

        .pub-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .pub-list-item {
            display: flex;
            align-items: center;
            padding: 0.75rem 1rem;
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .pub-list-item:hover {
            border-color: #6b5b95;
            background: #f0edf5;
        }

        .pub-list-item-name {
            flex: 1;
            font-weight: 500;
            color: #1a202c;
        }

        .pub-list-item-count {
            font-size: 0.85rem;
            color: #718096;
            margin-left: 0.5rem;
        }

        .pub-list-item-icon {
            color: #6b5b95;
            margin-left: 0.5rem;
        }

        .pub-list-empty {
            text-align: center;
            padding: 1.5rem;
            color: #718096;
            font-size: 0.9rem;
        }

        .pub-modal-article-preview {
            background: #f7fafc;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border-left: 3px solid #6b5b95;
        }

        .pub-modal-article-title {
            font-weight: 500;
            color: #1a202c;
            font-size: 0.95rem;
        }

        .pub-modal-success {
            background: #f0edf5;
            color: #6b5b95;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .pub-modal-success svg {
            width: 20px;
            height: 20px;
        }
    `;

    // Inject styles
    function injectStyles() {
        if (document.getElementById('pub-modal-styles')) return;
        const styleEl = document.createElement('style');
        styleEl.id = 'pub-modal-styles';
        styleEl.textContent = styles;
        document.head.appendChild(styleEl);
    }

    // Create modal HTML
    function createModal() {
        if (modalElement) return;

        injectStyles();

        modalElement = document.createElement('div');
        modalElement.className = 'pub-modal-overlay';
        modalElement.innerHTML = `
            <div class="pub-modal-window">
                <div class="pub-modal-header">
                    <h3 class="pub-modal-title">Adicionar à Publicação</h3>
                    <button class="pub-modal-close" onclick="PublicationModal.close()">×</button>
                </div>
                <div class="pub-modal-body" id="pubModalBody">
                    <!-- Content injected dynamically -->
                </div>
            </div>
        `;

        // Close on overlay click
        modalElement.addEventListener('click', (e) => {
            if (e.target === modalElement) close();
        });

        // Close on ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modalElement && modalElement.parentNode) {
                close();
            }
        });
    }

    // Render modal content
    function renderContent() {
        const body = document.getElementById('pubModalBody');
        if (!body) return;

        const publications = FavoritesManager.getPublications();
        const pubList = Object.values(publications);

        let html = '';

        // Article preview
        if (currentArticle) {
            html += `
                <div class="pub-modal-article-preview">
                    <div class="pub-modal-article-title">${currentArticle.title || 'Artigo selecionado'}</div>
                </div>
            `;
        }

        // Create new publication section
        html += `
            <div class="pub-modal-section">
                <div class="pub-modal-section-title">Criar Nova Publicação</div>
                <div class="pub-modal-input-group">
                    <input type="text" class="pub-modal-input" id="newPubName" 
                           placeholder="Nome da publicação..." 
                           onkeypress="if(event.key==='Enter')PublicationModal.createNew()">
                    <button class="pub-modal-btn pub-modal-btn-primary" onclick="PublicationModal.createNew()">
                        Criar
                    </button>
                </div>
            </div>
        `;

        // Existing publications section
        if (pubList.length > 0) {
            html += `
                <div class="pub-modal-section">
                    <div class="pub-modal-section-title">Ou Adicionar a Existente</div>
                    <div class="pub-list">
            `;

            pubList.forEach(pub => {
                const isAlreadyAdded = currentArticle &&
                    pub.items.some(item => item.id === currentArticle.id);

                html += `
                    <div class="pub-list-item" onclick="PublicationModal.addToExisting('${pub.id}')" 
                         ${isAlreadyAdded ? 'style="opacity:0.5;pointer-events:none;"' : ''}>
                        <span class="pub-list-item-name">${pub.name}</span>
                        <span class="pub-list-item-count">${pub.items.length} artigo${pub.items.length !== 1 ? 's' : ''}</span>
                        ${isAlreadyAdded
                        ? '<span class="pub-list-item-icon">✓ Adicionado</span>'
                        : '<span class="pub-list-item-icon">+</span>'
                    }
                    </div>
                `;
            });

            html += `</div></div>`;
        }

        body.innerHTML = html;

        // Focus input
        setTimeout(() => {
            const input = document.getElementById('newPubName');
            if (input) input.focus();
        }, 100);
    }

    // Show success message
    function showSuccess(message) {
        const body = document.getElementById('pubModalBody');
        if (!body) return;

        body.innerHTML = `
            <div class="pub-modal-success">
                <svg viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                ${message}
            </div>
        `;

        setTimeout(() => {
            close();
            if (onSuccessCallback) onSuccessCallback();
        }, 1500);
    }

    // Open modal with article
    function open(article, callback) {
        console.log('PublicationModal.open called with:', article);
        currentArticle = article;
        onSuccessCallback = callback || null;
        createModal();
        document.body.appendChild(modalElement);
        renderContent();
    }

    // Close modal
    function close() {
        if (modalElement && modalElement.parentNode) {
            modalElement.parentNode.removeChild(modalElement);
        }
        currentArticle = null;
    }

    // Create new publication and add article
    function createNew() {
        const input = document.getElementById('newPubName');
        if (!input || !input.value.trim()) {
            input.focus();
            return;
        }

        const name = input.value.trim();

        try {
            const pub = FavoritesManager.createPublication(name);

            if (currentArticle) {
                FavoritesManager.addToPublication(pub.id, currentArticle);
            }

            showSuccess(`Publicação "${name}" criada!`);
        } catch (e) {
            console.error('Error creating publication:', e);
            alert('Erro ao criar publicação');
        }
    }

    // Add article to existing publication
    function addToExisting(pubId) {
        if (!currentArticle) return;

        try {
            const added = FavoritesManager.addToPublication(pubId, currentArticle);
            const pub = FavoritesManager.getPublication(pubId);

            if (added) {
                showSuccess(`Adicionado a "${pub.name}"!`);
            } else {
                showSuccess('Artigo já está nesta publicação');
            }
        } catch (e) {
            console.error('Error adding to publication:', e);
            alert('Erro ao adicionar artigo');
        }
    }

    // Public API
    return {
        open,
        close,
        createNew,
        addToExisting
    };
})();

// Make available globally
window.PublicationModal = PublicationModal;
