/**
 * Global Publication Injector
 * Adds publication features to any article page on the site
 */

(function () {
    'use strict';

    // Don't run on publication page itself or search pages
    const isPublicationPage = window.location.pathname.includes('publicacao.html');
    const isSearchPage = window.location.pathname.includes('advanced_search.html');
    const isLoginPage = window.location.pathname.includes('login.html');
    const isIndexPage = window.location.pathname.endsWith('index.html') || window.location.pathname === '/';

    if (isPublicationPage || isLoginPage) return;

    // Wait for DOM and dependencies
    function init() {
        // Load dependencies if not already loaded
        loadDependencies(() => {
            if (!isSearchPage) {
                injectPublicationButton();
            }
            initPublicationBar();
        });
    }

    function loadDependencies(callback) {
        // Check if FavoritesManager is already loaded
        if (typeof FavoritesManager !== 'undefined') {
            callback();
            return;
        }

        // Load favorites.js
        const script = document.createElement('script');
        script.src = getBasePath() + 'scripts/favorites.js';
        script.onload = callback;
        script.onerror = () => console.log('Could not load favorites.js');
        document.head.appendChild(script);
    }

    function getBasePath() {
        // Find the base path by looking for scripts folder
        // Try common patterns based on current URL
        const path = window.location.pathname;

        // Try to find scripts folder relative to current page
        const scripts = document.querySelectorAll('script[src*="favorites"]');
        if (scripts.length > 0) {
            const src = scripts[0].src;
            return src.replace(/scripts\/favorites\.js.*$/, '');
        }

        // Calculate based on path depth from root
        const baseUrl = window.location.origin;
        const pathParts = path.split('/').filter(s => s && !s.endsWith('.html'));

        // Known folder structure
        if (pathParts.includes('search2')) {
            return baseUrl + '/';
        } else if (pathParts.includes('hakkousi') || pathParts.includes('filetop') ||
            pathParts.includes('kanren') || pathParts.includes('gosanka')) {
            return baseUrl + '/';
        }

        return baseUrl + '/';
    }

    // Inject floating "Add to Publication" button on article pages
    function injectPublicationButton() {
        // Extract article info from the page
        const articleInfo = extractArticleInfo();
        if (!articleInfo || !articleInfo.title) return;

        // Create floating button
        const btn = document.createElement('button');
        btn.id = 'global-pub-btn';
        btn.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
            </svg>
            <span>Adicionar à Publicação</span>
        `;

        // Styles
        const style = document.createElement('style');
        style.textContent = `
            #global-pub-btn {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: linear-gradient(135deg, #6b5b95 0%, #524175 100%);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 50px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 8px;
                box-shadow: 0 4px 15px rgba(107, 91, 149, 0.4);
                transition: all 0.3s ease;
                z-index: 9998;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }
            #global-pub-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(107, 91, 149, 0.5);
            }
            #global-pub-btn.added {
                background: linear-gradient(135deg, #5a9c6b 0%, #3d7a4e 100%);
            }
            #global-pub-btn.added svg {
                fill: currentColor;
            }

            /* Publication Modal */
            .global-pub-modal {
                position: fixed;
                inset: 0;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 10000;
                opacity: 0;
                visibility: hidden;
                transition: all 0.2s;
            }
            .global-pub-modal.active {
                opacity: 1;
                visibility: visible;
            }
            .global-pub-modal-content {
                background: white;
                border-radius: 12px;
                width: 90%;
                max-width: 400px;
                padding: 1.5rem;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
            }
            .global-pub-modal h3 {
                margin: 0 0 1rem 0;
                font-size: 1.1rem;
                color: #1a202c;
            }
            .global-pub-modal-close {
                position: absolute;
                top: 1rem;
                right: 1rem;
                background: none;
                border: none;
                font-size: 1.5rem;
                cursor: pointer;
                color: #718096;
            }
            .global-pub-input {
                width: 100%;
                padding: 0.75rem;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 0.95rem;
                margin-bottom: 0.5rem;
            }
            .global-pub-btn-create {
                width: 100%;
                padding: 0.75rem;
                background: #6b5b95;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 0.95rem;
                font-weight: 500;
                cursor: pointer;
                margin-bottom: 1rem;
            }
            .global-pub-btn-create:hover {
                background: #5a4a7e;
            }
            .global-pub-list {
                max-height: 200px;
                overflow-y: auto;
            }
            .global-pub-item {
                padding: 0.75rem;
                background: #f7fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin-bottom: 0.5rem;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                transition: all 0.2s;
            }
            .global-pub-item:hover {
                border-color: #6b5b95;
                background: #f0edf5;
            }
            .global-pub-item-name {
                font-weight: 500;
            }
            .global-pub-item-count {
                font-size: 0.85rem;
                color: #718096;
            }
            .global-pub-success {
                background: #f0edf5;
                color: #6b5b95;
                padding: 1rem;
                border-radius: 8px;
                text-align: center;
            }
        `;
        document.head.appendChild(style);

        // Check if already added
        updateButtonState(btn, articleInfo);

        btn.onclick = () => showPublicationModal(articleInfo, btn);
        document.body.appendChild(btn);
    }

    function updateButtonState(btn, articleInfo) {
        if (typeof FavoritesManager !== 'undefined' && FavoritesManager.isInAnyPublication(articleInfo.id)) {
            btn.classList.add('added');
            btn.querySelector('span').textContent = 'Já Adicionado';
            btn.querySelector('svg').setAttribute('fill', 'currentColor');
        }
    }

    function extractArticleInfo() {
        // Try to get title from various sources
        let title = document.querySelector('h1')?.textContent?.trim()
            || document.querySelector('.teaching-title')?.textContent?.trim()
            || document.querySelector('title')?.textContent?.trim()
            || document.querySelector('.modal-title')?.textContent?.trim();

        if (!title) return null;

        // Get other metadata
        const url = window.location.href;
        const id = 'page_' + url.replace(/[^a-zA-Z0-9]/g, '_').substring(0, 50);

        // Try to get category and source
        const category = document.querySelector('.category')?.textContent?.trim() || '';
        const source = document.querySelector('.source')?.textContent?.trim() || '';

        // Get content snippet
        const contentEl = document.querySelector('.content-body, .teaching-content, article, main, .modal-content');
        const content_snippet = contentEl?.textContent?.substring(0, 300)?.trim() || '';

        return {
            id,
            title,
            url,
            category,
            source,
            content_snippet
        };
    }

    function showPublicationModal(articleInfo, btn) {
        // Remove existing modal if any
        document.querySelector('.global-pub-modal')?.remove();

        const modal = document.createElement('div');
        modal.className = 'global-pub-modal';

        const publications = typeof FavoritesManager !== 'undefined'
            ? Object.values(FavoritesManager.getPublications())
            : [];

        modal.innerHTML = `
            <div class="global-pub-modal-content" style="position: relative;">
                <button class="global-pub-modal-close" onclick="this.closest('.global-pub-modal').remove()">×</button>
                <h3>📚 Adicionar à Publicação</h3>
                <div style="background: #f7fafc; padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; border-left: 3px solid #6b5b95;">
                    <strong style="font-size: 0.9rem;">${articleInfo.title}</strong>
                </div>
                <input type="text" class="global-pub-input" id="newPubNameGlobal" placeholder="Nome da nova publicação...">
                <button class="global-pub-btn-create" onclick="window._globalPubCreate()">Criar e Adicionar</button>
                ${publications.length > 0 ? `
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: #718096; margin-bottom: 0.5rem;">Ou adicionar a existente:</div>
                    <div class="global-pub-list">
                        ${publications.map(p => `
                            <div class="global-pub-item" onclick="window._globalPubAdd('${p.id}')">
                                <span class="global-pub-item-name">${p.name}</span>
                                <span class="global-pub-item-count">${p.items.length} artigos</span>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;

        document.body.appendChild(modal);
        setTimeout(() => modal.classList.add('active'), 10);

        // Click outside to close
        modal.onclick = (e) => {
            if (e.target === modal) modal.remove();
        };

        // Store article info and btn reference
        window._globalArticleInfo = articleInfo;
        window._globalPubBtn = btn;

        // Focus input
        setTimeout(() => document.getElementById('newPubNameGlobal')?.focus(), 100);
    }

    // Global functions for modal
    window._globalPubCreate = function () {
        const input = document.getElementById('newPubNameGlobal');
        const name = input?.value?.trim();
        if (!name) {
            input?.focus();
            return;
        }

        const pub = FavoritesManager.createPublication(name);
        FavoritesManager.addToPublication(pub.id, window._globalArticleInfo);

        showSuccess(`Adicionado a "${name}"!`);
    };

    window._globalPubAdd = function (pubId) {
        const pub = FavoritesManager.getPublication(pubId);
        FavoritesManager.addToPublication(pubId, window._globalArticleInfo);

        showSuccess(`Adicionado a "${pub.name}"!`);
    };

    function showSuccess(message) {
        const modal = document.querySelector('.global-pub-modal-content');
        if (modal) {
            modal.innerHTML = `
                <div class="global-pub-success">
                    <svg width="24" height="24" viewBox="0 0 20 20" fill="currentColor" style="margin-bottom: 0.5rem;">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                    </svg>
                    <div>${message}</div>
                </div>
            `;
        }

        // Update button state
        if (window._globalPubBtn && window._globalArticleInfo) {
            updateButtonState(window._globalPubBtn, window._globalArticleInfo);
        }

        // Close after delay
        setTimeout(() => {
            document.querySelector('.global-pub-modal')?.remove();
        }, 1500);
    }

    // Initialize publication bar
    function initPublicationBar() {
        // Load and init the publication bar script
        if (typeof PublicationBar !== 'undefined') {
            PublicationBar.init();
            return;
        }

        const script = document.createElement('script');
        script.src = getBasePath() + 'scripts/publication-bar.js';
        document.head.appendChild(script);
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
