/**
 * Publication Bar Component
 * Floating bar that shows active publications
 */

const PublicationBar = (function () {
    let barElement = null;

    // CSS styles for the bar
    const styles = `
        .pub-bar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: linear-gradient(135deg, #6b5b95 0%, #524175 100%);
            color: white;
            padding: 0.5rem 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            z-index: 9999;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
            animation: pubBarSlideDown 0.3s ease-out;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        @keyframes pubBarSlideDown {
            from { transform: translateY(-100%); }
            to { transform: translateY(0); }
        }

        .pub-bar-icon {
            font-size: 1.1rem;
        }

        .pub-bar-text {
            font-size: 0.9rem;
            font-weight: 500;
        }

        .pub-bar-count {
            background: rgba(255, 255, 255, 0.2);
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .pub-bar-btn {
            background: white;
            color: #6b5b95;
            border: none;
            padding: 0.4rem 1rem;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
        }

        .pub-bar-btn:hover {
            background: #f0edf5;
            transform: translateY(-1px);
        }

        .pub-bar-close {
            background: transparent;
            border: none;
            color: rgba(255, 255, 255, 0.8);
            font-size: 1.2rem;
            cursor: pointer;
            padding: 0.2rem 0.5rem;
            margin-left: 0.5rem;
            border-radius: 4px;
            transition: all 0.2s;
        }

        .pub-bar-close:hover {
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }

        /* Adjust page content when bar is visible */
        body.has-pub-bar {
            padding-top: 45px !important;
        }

        body.has-pub-bar .header,
        body.has-pub-bar header {
            top: 45px !important;
        }
    `;

    // Inject styles
    function injectStyles() {
        if (document.getElementById('pub-bar-styles')) return;
        const styleEl = document.createElement('style');
        styleEl.id = 'pub-bar-styles';
        styleEl.textContent = styles;
        document.head.appendChild(styleEl);
    }

    // Get the base path for links
    function getBasePath() {
        // Robust way: find the script tag that loaded this or favorites.js
        const scripts = document.querySelectorAll('script[src*="publication-bar.js"], script[src*="favorites.js"]');
        if (scripts.length > 0) {
            const src = scripts[0].src;
            // Remove the script filename and the 'scripts/' folder to get root
            // e.g. http://site.com/repo/scripts/publication-bar.js -> http://site.com/repo/
            return src.replace(/scripts\/[\w-]+\.js(\?.*)?$/, '');
        }

        // Fallback: relative depth (fragile, but works for local flat files)
        const path = window.location.pathname;
        const depth = (path.match(/\//g) || []).length - 1;
        return depth > 0 ? '../'.repeat(depth) : './';
    }

    // Create and show the bar
    function show() {
        if (barElement) return;

        const publications = FavoritesManager.getPublications();
        const pubList = Object.values(publications);
        const totalItems = FavoritesManager.getTotalItemsCount();

        if (pubList.length === 0 || totalItems === 0) {
            hide();
            return;
        }

        injectStyles();

        const basePath = getBasePath();
        const pubNames = pubList.map(p => p.name).slice(0, 3).join(', ');
        const moreCount = pubList.length > 3 ? ` +${pubList.length - 3}` : '';

        barElement = document.createElement('div');
        barElement.className = 'pub-bar';
        barElement.id = 'publicationBar';
        barElement.innerHTML = `
            <span class="pub-bar-icon">📚</span>
            <span class="pub-bar-text">${pubNames}${moreCount}</span>
            <span class="pub-bar-count">${totalItems} artigo${totalItems !== 1 ? 's' : ''}</span>
            <a href="${basePath}publicacao.html" class="pub-bar-btn">
                Ver Publicação →
            </a>
            <button class="pub-bar-close" onclick="PublicationBar.hide()" title="Fechar">×</button>
        `;

        document.body.prepend(barElement);
        document.body.classList.add('has-pub-bar');
    }

    // Hide the bar
    function hide() {
        if (barElement && barElement.parentNode) {
            barElement.parentNode.removeChild(barElement);
            barElement = null;
        }
        document.body.classList.remove('has-pub-bar');
    }

    // Update bar content
    function update() {
        hide();
        const totalItems = FavoritesManager.getTotalItemsCount();
        if (totalItems > 0) {
            show();
        }
    }

    // Initialize - show bar if there are publications
    function init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                update();
            });
        } else {
            update();
        }

        // Listen for publication updates
        window.addEventListener('publications-updated', () => {
            update();
        });
    }

    // Public API
    return {
        show,
        hide,
        update,
        init
    };
})();

// Make available globally
window.PublicationBar = PublicationBar;

// Auto-initialize
PublicationBar.init();
