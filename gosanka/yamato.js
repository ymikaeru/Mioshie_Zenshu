
// State
let globalData = null;
let allPoemsFlat = [];
let currentRenderId = 0; // To cancel old renders if filter changes fast

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    try {
        const response = await fetch('yamato_full.json');
        globalData = await response.json();

        // Preprocess logic
        preprocessData(globalData);

        // Initial Render
        renderFilters(globalData);
        applyFilters(); // Defaults to showing all (original structure)

        // Check for deep link
        const urlParams = new URLSearchParams(window.location.search);
        const poemId = urlParams.get('poem');
        if (poemId) {
            setTimeout(() => {
                const targetPoem = window.poemLookup && window.poemLookup['poem_' + poemId];
                if (targetPoem) {
                    openModal(targetPoem);
                }
            }, 500);
        }
    } catch (e) {
        console.error("Failed to load yamato_full.json", e);
        document.getElementById('poems-container').innerHTML = '<p style="color:red; text-align:center;">Erro ao carregar dados. Verifique yamato_full.json</p>';
    }
}

// Mood Mapping Configuration
const SECTION_MOOD_MAP = {
    // Contemplativo (Natureza/Cosmos) - Serene, Nature, Cosmos
    "Lua": "Contemplativo",
    "Neve": "Contemplativo",
    "Estrela": "Contemplativo",
    "Cerejeiras se Dispersam": "Contemplativo",
    "Outono": "Contemplativo",

    // Crítico (Sociedade/Humanidade) - Critical, Social Commentary
    "Sociedade e Pensamento": "Crítico",
    "Ídolos": "Crítico",
    "O Mundo Agora": "Crítico",
    "Indignação": "Crítico",

    // Melancólico (Solidão/Sadness) - Melancholic
    "Trem Noturno": "Melancólico",
    "Pescaria": "Melancólico", // Often solitary/waiting

    // Vibrante (Vida/Movimento) - Vibrant, Movement, Life
    "Mover-se": "Vibrante",
    "Círculo": "Vibrante",

    // Reflexivo (Eu/Interior) - Reflective, Self
    "Sentimentos": "Reflexivo",
    "Meu Agora": "Reflexivo",

    // Fallback/Mixed
    "Oh, Japão": "Crítico"
};

function preprocessData(data) {
    window.poemLookup = {};
    allPoemsFlat = [];

    if (!data.sections) return;

    data.sections.forEach(section => {
        section.poems.forEach(poem => {
            // Enrich poem object
            poem.sectionTitle = section.title_pt;
            poem.detectedSeason = detectSeason(poem.kigo || "");

            // Assign Mood based on Section title mapping
            poem.mood = SECTION_MOOD_MAP[section.title_pt] || "Outros";

            // Add to lookup
            const pid = 'poem_' + poem.number;
            window.poemLookup[pid] = poem;

            // Add to flat list
            allPoemsFlat.push(poem);
        });
    });
}

function detectSeason(kigoText) {
    if (!kigoText) return "Outros";
    const text = kigoText.toLowerCase();

    if (text.includes('primavera') || text.includes('spring')) return 'Primavera';
    if (text.includes('verão') || text.includes('verao') || text.includes('summer')) return 'Verão';
    if (text.includes('outono') || text.includes('autumn') || text.includes('fall')) return 'Outono';
    if (text.includes('inverno') || text.includes('winter')) return 'Inverno';
    if (text.includes('ano novo') || text.includes('new year')) return 'Ano Novo';

    return "Outros";
}

function renderFilters(data) {
    const catSelect = document.getElementById('filter-category');
    if (!data.sections) return;

    // Populate Categories
    data.sections.forEach(sec => {
        const opt = document.createElement('option');
        opt.value = sec.title_pt;
        opt.textContent = sec.title_pt;
        catSelect.appendChild(opt);
    });
}

function applyFilters() {
    const moodFilter = document.getElementById('filter-mood').value;
    const catFilter = document.getElementById('filter-category').value;
    const seasonFilter = document.getElementById('filter-season').value;
    const sortOrder = document.getElementById('sort-order').value;

    const container = document.getElementById('poems-container');
    container.innerHTML = '';

    // Stop any previous ongoing render
    currentRenderId++;
    const thisRenderId = currentRenderId;

    // Filter
    let filtered = allPoemsFlat.filter(poem => {
        if (moodFilter && poem.mood !== moodFilter) return false;
        if (catFilter && poem.sectionTitle !== catFilter) return false;
        if (seasonFilter && poem.detectedSeason !== seasonFilter) return false;
        return true;
    });

    // Sort
    if (sortOrder === 'az') {
        filtered.sort((a, b) => a.title.localeCompare(b.title));
    } else if (sortOrder === 'za') {
        filtered.sort((a, b) => b.title.localeCompare(a.title));
    } else {
        // Original order (by number)
        filtered.sort((a, b) => a.number - b.number);
    }

    // Logic: If ANY filter is active OR sort is not original, render FLAT grid.
    // If NO filters and Original sort, render SECTIONS (Original View).
    const isDefaultView = !moodFilter && !catFilter && !seasonFilter && sortOrder === 'original';

    if (isDefaultView) {
        renderOriginalView(globalData, container, thisRenderId);
    } else {
        renderFlatView(filtered, container, thisRenderId);
    }
}

function resetFilters() {
    document.getElementById('filter-mood').value = "";
    document.getElementById('filter-category').value = "";
    document.getElementById('filter-season').value = "";
    document.getElementById('sort-order').value = "original";
    applyFilters();
}

// --- Rendering Logic ---

function renderOriginalView(data, container, renderId) {
    // 1. Render Preface
    if (data.preface) {
        const prefSection = document.createElement('section');
        prefSection.className = 'preface-container';
        prefSection.style.padding = '20px';
        prefSection.style.background = '#fff';
        prefSection.style.marginBottom = '20px';
        prefSection.style.borderRadius = '8px';
        prefSection.innerHTML = `<h2 style="color:#2c7744; border-bottom:1px solid #ddd; padding-bottom:10px;">${data.preface.title_pt}</h2>`;
        data.preface.content_pt.forEach(pText => {
            const p = document.createElement('p');
            p.className = 'honbun';
            p.innerHTML = parseMarkdownSimple(pText);
            prefSection.appendChild(p);
        });
        container.appendChild(prefSection);
    }

    // 2. Render Sections Chunked
    const sections = data.sections || [];
    let sectionIndex = 0;

    function renderNextChunk() {
        if (renderId !== currentRenderId) return; // Cancelled
        if (sectionIndex >= sections.length) return; // Done

        const sec = sections[sectionIndex];
        const secDiv = document.createElement('div');
        secDiv.className = 'section-container';
        secDiv.style.marginBottom = '30px';
        secDiv.style.background = '#fff';
        secDiv.style.padding = '20px';
        secDiv.style.borderRadius = '8px';
        secDiv.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';

        const jpTitle = sec.title_jp ? `<span style="font-weight:normal; font-size:0.8em; color:#666; margin-left:10px;">(${sec.title_jp})</span>` : '';
        secDiv.innerHTML = `<h3 style="color:#2c7744; margin-top:0;">📂 ${sec.title_pt} ${jpTitle}</h3>`;

        const poemsGrid = createGrid();
        sec.poems.forEach(poem => {
            poemsGrid.appendChild(createPoemCard(poem));
        });

        secDiv.appendChild(poemsGrid);
        container.appendChild(secDiv);

        sectionIndex++;
        requestAnimationFrame(renderNextChunk);
    }
    renderNextChunk();
}

function renderFlatView(poems, container, renderId) {
    // Header with count
    const info = document.createElement('div');
    info.style.padding = '10px 0';
    info.style.color = '#666';
    info.textContent = `Encontrados: ${poems.length} poemas`;
    container.appendChild(info);

    const grid = createGrid();
    container.appendChild(grid);

    // Render chunked to avoid freezing if large list
    let index = 0;
    const CHUNK_SIZE = 50;

    function renderNextFlatChunk() {
        if (renderId !== currentRenderId) return;
        if (index >= poems.length) return;

        const chunk = poems.slice(index, index + CHUNK_SIZE);
        const fragment = document.createDocumentFragment();

        chunk.forEach(poem => {
            fragment.appendChild(createPoemCard(poem));
        });

        grid.appendChild(fragment);
        index += CHUNK_SIZE;
        requestAnimationFrame(renderNextFlatChunk);
    }
    renderNextFlatChunk();
}

function createGrid() {
    const div = document.createElement('div');
    div.style.display = 'grid';
    div.style.gridTemplateColumns = 'repeat(auto-fill, minmax(250px, 1fr))';
    div.style.gap = '10px';
    return div;
}

function createPoemCard(poem) {
    const poemId = 'poem_' + poem.number;
    const pCard = document.createElement('div');
    pCard.className = 'poem-list-item';
    pCard.id = poemId;
    pCard.style.padding = '10px';
    pCard.style.border = '1px solid #eee';
    pCard.style.borderRadius = '6px';
    pCard.style.cursor = 'pointer';
    pCard.style.transition = 'all 0.2s';
    pCard.style.background = '#fcfdfc';

    // Hover effects
    pCard.onmouseover = () => { pCard.style.background = '#e6f4ea'; pCard.style.borderColor = '#2c7744'; };
    pCard.onmouseout = () => { pCard.style.background = '#fcfdfc'; pCard.style.borderColor = '#eee'; };

    pCard.setAttribute('onclick', `window.openModal(window.poemLookup['${poemId}'])`);

    // Badge for season if filtered view or just helpful info
    const seasonBadge = poem.detectedSeason !== 'Outros'
        ? `<span style="font-size:0.75em; background:#eee; padding:2px 6px; border-radius:10px; color:#555; float:right;">${poem.detectedSeason}</span>`
        : '';

    pCard.innerHTML = `<div style="font-weight:bold; color:#2c7744;">${poem.number}. ${seasonBadge}</div><div>${poem.title}</div>`;
    return pCard;
}

function parseMarkdownSimple(text) {
    if (!text) return '';
    let html = text
        .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>') // Bold
        .replace(/\*(.*?)\*/g, '<i>$1</i>')     // Italic
        .replace(/---/g, '<hr>')                 // HR
        .replace(/\n/g, '<br>');                 // Newlines
    return html;
}

// Modal Logic
function openModal(poem) {
    try {
        console.log("Opening modal for:", poem.number, poem.title);
        const modal = document.getElementById('contentModal');
        if (!modal) {
            console.error("Modal element 'contentModal' not found!");
            return;
        }

        // Update URL
        const newUrl = window.location.pathname + '?poem=' + poem.number;
        window.history.pushState({ path: newUrl }, '', newUrl);

        // Header Title and Copy Button
        const headerTitle = document.getElementById('modalTitle');
        headerTitle.innerHTML = `
            ${poem.title}
             <div style="display:inline-flex; gap:5px; margin-left:10px; vertical-align:middle;">
                <button class="copy-btn" onclick="copyPoemLink()" title="Copiar Link">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                        <path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/>
                    </svg>
                </button>
                <button class="copy-btn" onclick="copyPoemContent()" title="Copiar conteúdo">
                    <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                       <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                    </svg>
                </button>
            </div>
        `;

        const body = document.getElementById('modalBodyContent');
        body.innerHTML = ''; // basic clear

        // Build content matching Home design
        let html = `
            <div class="poem-modal-content" id="poemContentToCopy">
                <!-- Header Badge -->
                <div class="poem-badge">POESIA SAGRADA</div>
                
                <!-- Original Japanese - Large Centered -->
                <div class="poem-original-large">${poem.original || ''}</div>
                
                <!-- Romaji Reading -->
                <div class="poem-reading-romaji">${poem.reading || ''}</div>
                
                <!-- Portuguese Title -->
                <div class="poem-pt-title">${poem.title}</div>
                
                <!-- Portuguese Translation - Italic -->
                <div class="poem-translation-featured">"${poem.translation || ''}"</div>
        `;

        // Store current poem for copy function
        window.currentModalPoem = poem;

        // Kigo Card
        if (poem.kigo) {
            html += `
                <div class="poem-info-card kigo-card">
                    <div class="card-header">🍃 KIGO (ESTAÇÃO E CLIMA)</div>
                    <div class="card-content">${parseMarkdownSimple(poem.kigo)}</div>
                </div>
            `;
        }

        // Kototama Card
        if (poem.kototama) {
            html += `
                <div class="poem-info-card kototama-card">
                    <div class="card-header">🎵 KOTOTAMA (SONORIDADE)</div>
                    <div class="card-content">${parseMarkdownSimple(poem.kototama)}</div>
                </div>
            `;
        }

        // Deepening/Profundidade Section
        if (poem.deepening) {
            html += `
                <div class="poem-deepening-section">
                    <div class="deepening-header">💎 SIGNIFICADO PROFUNDO</div>
                    <div class="deepening-content">${parseMarkdownSimple(poem.deepening)}</div>
                </div>
            `;
        }

        html += `</div>`; // close poem-modal-content

        body.innerHTML = html;
        modal.classList.add('active');

        // Add copy button style if not present
        if (!document.getElementById('copy-btn-style')) {
            const style = document.createElement('style');
            style.id = 'copy-btn-style';
            style.innerHTML = `
                .copy-btn {
                    background: none;
                    border: none;
                    cursor: pointer;
                    color: #666;
                    padding: 4px;
                    border-radius: 4px;
                    margin-left: 10px;
                    transition: all 0.2s;
                    display: inline-flex;
                    align-items: center;
                    vertical-align: middle;
                }
                .copy-btn:hover {
                    background-color: #f0f0f0;
                    color: #2c7744;
                }
                .copy-btn.copied {
                    color: #2c7744;
                    background-color: #e6f4ea;
                }
            `;
            document.head.appendChild(style);
        }

    } catch (e) {
        console.error("Error in openModal:", e);
        alert("Erro ao abrir o modal. Verifique o console.");
    }
}

function closeModal() {
    const modal = document.getElementById('contentModal');
    if (modal) modal.classList.remove('active');

    // Reset URL
    const cleanUrl = window.location.pathname;
    window.history.pushState({ path: cleanUrl }, '', cleanUrl);
    window.currentModalPoem = null;
}

function copyPoemLink() {
    const url = window.location.href;
    navigator.clipboard.writeText(url).then(() => {
        const btns = document.querySelectorAll('.copy-btn');
        // Assuming first button is link copy based on order
        const btn = btns[0];
        if (btn) {
            const originalHtml = btn.innerHTML;
            btn.classList.add('copied');
            btn.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>`;
            setTimeout(() => {
                btn.classList.remove('copied');
                btn.innerHTML = originalHtml;
            }, 2000);
        }
    }).catch(err => console.error('Failed to copy link', err));
}

function copyPoemContent() {
    const poem = window.currentModalPoem;
    if (!poem) return;

    const textToCopy = `
${poem.title}

${poem.original || ''}
${poem.reading || ''}

"${poem.translation || ''}"
`.trim();

    navigator.clipboard.writeText(textToCopy).then(() => {
        const btns = document.querySelectorAll('.copy-btn');
        const btn = btns[1]; // Second button is Content Copy
        if (btn) {
            const originalHtml = btn.innerHTML;
            btn.classList.add('copied');
            btn.innerHTML = `<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>`;
            setTimeout(() => {
                btn.classList.remove('copied');
                btn.innerHTML = originalHtml;
            }, 2000);
        }
    }).catch(err => {
        console.error('Failed to copy text: ', err);
    });
}

// Ensure global access
window.openModal = openModal;
window.closeModal = closeModal;
window.copyPoemContent = copyPoemContent;
window.copyPoemLink = copyPoemLink;

// Close on outside click is handled in HTML inline or we add listener here
document.addEventListener('click', (e) => {
    if (e.target && e.target.id === 'contentModal') {
        closeModal();
    }
});
