/**
 * Favorites/Publications System
 * Manages publications and favorite articles in localStorage
 */

const FavoritesManager = (function () {
    const STORAGE_KEY = 'mioshie_publications';

    // Predefined color palette for publications
    const COLORS = [
        '#6b5b95', // Murasaki Purple
        '#88b04b', // Greenery
        '#f7cac9', // Rose Quartz
        '#92a8d1', // Serenity Blue
        '#955251', // Marsala
        '#b565a7', // Orchid
        '#009b77', // Emerald
        '#dd4124', // Tangerine Tango
        '#45b8ac', // Turquoise
        '#efc050', // Mimosa Yellow
    ];

    // Generate unique ID
    function generateId() {
        return 'pub_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    // Get all publications from localStorage
    function getPublications() {
        try {
            const data = localStorage.getItem(STORAGE_KEY);
            return data ? JSON.parse(data) : {};
        } catch (e) {
            console.error('Error reading publications:', e);
            return {};
        }
    }

    // Save publications to localStorage
    function savePublications(publications) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(publications));
            // Dispatch event for UI updates
            window.dispatchEvent(new CustomEvent('publications-updated', { detail: publications }));
        } catch (e) {
            console.error('Error saving publications:', e);
        }
    }

    // Get next available color
    function getNextColor() {
        const publications = getPublications();
        const usedColors = Object.values(publications).map(p => p.color).filter(Boolean);
        // Find first unused color
        for (const color of COLORS) {
            if (!usedColors.includes(color)) {
                return color;
            }
        }
        // If all used, pick random
        return COLORS[Math.floor(Math.random() * COLORS.length)];
    }

    // Create a new publication
    function createPublication(name) {
        if (!name || !name.trim()) {
            throw new Error('Publication name is required');
        }

        const publications = getPublications();
        const id = generateId();

        publications[id] = {
            id: id,
            name: name.trim(),
            color: getNextColor(),
            createdAt: new Date().toISOString(),
            items: [],
            settings: {
                fontSize: '16px',
                textAlign: 'justify'
            }
        };

        savePublications(publications);
        return publications[id];
    }

    // Delete a publication
    function deletePublication(id) {
        const publications = getPublications();
        if (publications[id]) {
            delete publications[id];
            savePublications(publications);
            return true;
        }
        return false;
    }

    // Get a single publication by ID
    function getPublication(id) {
        const publications = getPublications();
        return publications[id] || null;
    }

    // Add article to publication
    function addToPublication(pubId, article) {
        const publications = getPublications();
        const pub = publications[pubId];

        if (!pub) {
            throw new Error('Publication not found');
        }

        // Check if article already exists
        const exists = pub.items.some(item => item.id === article.id);
        if (exists) {
            return false; // Already in publication
        }

        // Add article with required fields
        pub.items.push({
            id: article.id,
            title: article.title || 'Sem título',
            url: article.url || '',
            category: article.category || '',
            date: article.date || article.year || '',
            source: article.source || article.publication || '',
            tags: article.tags || [],
            content_snippet: article.content_snippet || '',
            part_file: article.part_file || '',
            addedAt: new Date().toISOString()
        });

        savePublications(publications);
        return true;
    }

    // Add multiple articles to publication (Single Save)
    function addMultipleToPublication(pubId, articles) {
        const publications = getPublications();
        const pub = publications[pubId];

        if (!pub) {
            throw new Error('Publication not found');
        }

        let addedCount = 0;
        const now = new Date().toISOString();

        articles.forEach(article => {
            // Check if article already exists
            const exists = pub.items.some(item => item.id === article.id);
            if (!exists) {
                // Add article with required fields
                pub.items.push({
                    id: article.id,
                    title: article.title || 'Sem título',
                    url: article.url || '',
                    category: article.category || '',
                    date: article.date || article.year || '',
                    source: article.source || article.publication || '',
                    tags: article.tags || [],
                    content_snippet: article.content_snippet || '',
                    part_file: article.part_file || '',
                    addedAt: now
                });
                addedCount++;
            }
        });

        if (addedCount > 0) {
            savePublications(publications);
        }
        return addedCount;
    }

    // Remove article from publication
    function removeFromPublication(pubId, articleId) {
        const publications = getPublications();
        const pub = publications[pubId];

        if (!pub) {
            return false;
        }

        const initialLength = pub.items.length;
        pub.items = pub.items.filter(item => item.id !== articleId);

        if (pub.items.length < initialLength) {
            savePublications(publications);
            return true;
        }
        return false;
    }

    // Update publication settings
    function updatePublicationSettings(pubId, settings) {
        const publications = getPublications();
        const pub = publications[pubId];

        if (!pub) {
            return false;
        }

        pub.settings = { ...pub.settings, ...settings };
        savePublications(publications);
        return true;
    }

    // Rename publication
    function renamePublication(pubId, newName) {
        if (!newName || !newName.trim()) {
            return false;
        }

        const publications = getPublications();
        const pub = publications[pubId];

        if (!pub) {
            return false;
        }

        pub.name = newName.trim();
        savePublications(publications);
        return true;
    }

    // Reorder items in publication
    function reorderItems(pubId, fromIndex, toIndex) {
        const publications = getPublications();
        const pub = publications[pubId];

        if (!pub || fromIndex < 0 || toIndex < 0 ||
            fromIndex >= pub.items.length || toIndex >= pub.items.length) {
            return false;
        }

        const [item] = pub.items.splice(fromIndex, 1);
        pub.items.splice(toIndex, 0, item);
        savePublications(publications);
        return true;
    }

    // Check if article is in any publication
    function isInAnyPublication(articleId) {
        const publications = getPublications();
        for (const pubId in publications) {
            if (publications[pubId].items.some(item => item.id === articleId)) {
                return true;
            }
        }
        return false;
    }

    // Get all publications containing article
    function getPublicationsContaining(articleId) {
        const publications = getPublications();
        const result = [];
        for (const pubId in publications) {
            if (publications[pubId].items.some(item => item.id === articleId)) {
                result.push(publications[pubId]);
            }
        }
        return result;
    }

    // Get total count of publications
    function getPublicationCount() {
        return Object.keys(getPublications()).length;
    }

    // Get total items across all publications
    function getTotalItemsCount() {
        const publications = getPublications();
        let count = 0;
        for (const pubId in publications) {
            count += publications[pubId].items.length;
        }
        return count;
    }

    // Get color for article (from first publication containing it)
    function getArticleColor(articleId) {
        const publications = getPublications();
        for (const pubId in publications) {
            const pub = publications[pubId];
            if (pub.items.some(item => item.id === articleId)) {
                return pub.color || '#6b5b95'; // Default to Murasaki
            }
        }
        return null;
    }

    // Public API
    return {
        getPublications,
        createPublication,
        deletePublication,
        getPublication,
        addToPublication,
        addMultipleToPublication,
        removeFromPublication,
        updatePublicationSettings,
        renamePublication,
        reorderItems,
        isInAnyPublication,
        getPublicationsContaining,
        getPublicationCount,
        getTotalItemsCount,
        getArticleColor
    };
})();

// Make available globally
window.FavoritesManager = FavoritesManager;

/**
 * Reading History Manager
 * Tracks last 20 visited articles
 */
const HistoryManager = (function () {
    const STORAGE_KEY = 'mioshie_reading_history';
    const MAX_ITEMS = 20;

    function getHistory() {
        try {
            const data = localStorage.getItem(STORAGE_KEY);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            console.error('Error reading history:', e);
            return [];
        }
    }

    function addToHistory(item) {
        if (!item || !item.id) return;

        let history = getHistory();

        // Remove existing if present (to move to top)
        history = history.filter(h => h.id !== item.id);

        // Add to top
        history.unshift({
            id: item.id,
            title: item.title,
            timestamp: Date.now()
        });

        // Limit size
        if (history.length > MAX_ITEMS) {
            history = history.slice(0, MAX_ITEMS);
        }

        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
            // Dispatch event
            window.dispatchEvent(new CustomEvent('history-updated', { detail: history }));
        } catch (e) {
            console.error('Error saving history:', e);
        }
    }

    function clearHistory() {
        localStorage.removeItem(STORAGE_KEY);
        window.dispatchEvent(new CustomEvent('history-updated', { detail: [] }));
    }

    return {
        get: getHistory,
        add: addToHistory,
        clear: clearHistory
    };
})();

// Make available globally
window.HistoryManager = HistoryManager;
