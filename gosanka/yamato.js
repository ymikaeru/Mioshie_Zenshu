
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    try {
        const response = await fetch('yamato_full.json');
        const data = await response.json();
        renderApp(data);

        // Check for deep link after rendering
        const urlParams = new URLSearchParams(window.location.search);
        const poemId = urlParams.get('poem');
        if (poemId) {
            // Give a slight delay to ensure DOM is ready and lookup is populated
            setTimeout(() => {
                const targetPoem = window.poemLookup && window.poemLookup['poem_' + poemId];
                if (targetPoem) {
                    openModal(targetPoem);
                }
            }, 500);
        }
    } catch (e) {
        console.error("Failed to load yamato_full.json", e);
        document.getElementById('app').innerHTML = '<p style="color:red; text-align:center;">Erro ao carregar dados. Verifique yamato_full.json</p>';
    }
}

function renderApp(data) {
    const app = document.getElementById('app');

    // CRITICAL: Clear the "Carregando..." message
    app.innerHTML = '';

    // Global lookup for poems by ID (for inline onclick fallback)
    window.poemLookup = window.poemLookup || {};

    // 1. Render Preface immediately
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

        app.appendChild(prefSection);
    }

    // 2. Render Sections with Chunked Loading (Virtualization-lite)
    // Rendering all items at once blocks the UI. detailed breakdown below.
    const sections = data.sections || [];
    let sectionIndex = 0;

    function renderNextChunk() {
        if (sectionIndex >= sections.length) return; // Done

        // Render one section per frame/tick
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

        // Grid for poems
        const poemsGrid = document.createElement('div');
        poemsGrid.style.display = 'grid';
        poemsGrid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(250px, 1fr))';
        poemsGrid.style.gap = '10px';

        // Render all poems in this section (usually 20-50, which is fast enough for one frame)
        sec.poems.forEach(poem => {
            // Store poem in global lookup
            const poemId = 'poem_' + poem.number;
            window.poemLookup[poemId] = poem;

            const pCard = document.createElement('div');
            pCard.className = 'poem-list-item';
            pCard.id = poemId;
            pCard.style.padding = '10px';
            pCard.style.border = '1px solid #eee';
            pCard.style.borderRadius = '6px';
            pCard.style.cursor = 'pointer';
            pCard.style.transition = 'all 0.2s';
            pCard.style.background = '#fcfdfc';

            pCard.onmouseover = () => { pCard.style.background = '#e6f4ea'; pCard.style.borderColor = '#2c7744'; };
            pCard.onmouseout = () => { pCard.style.background = '#fcfdfc'; pCard.style.borderColor = '#eee'; };

            // Use setAttribute for onclick as a more reliable fallback
            pCard.setAttribute('onclick', `window.openModal(window.poemLookup['${poemId}'])`);

            pCard.innerHTML = `<div style="font-weight:bold; color:#2c7744;">${poem.number}.</div><div>${poem.title}</div>`;
            poemsGrid.appendChild(pCard);
        });

        secDiv.appendChild(poemsGrid);
        app.appendChild(secDiv);

        sectionIndex++;
        // Schedule next chunk
        requestAnimationFrame(renderNextChunk);
    }

    // Start the chunked rendering
    renderNextChunk();
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
