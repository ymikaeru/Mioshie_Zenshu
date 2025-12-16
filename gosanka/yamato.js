
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    try {
        const response = await fetch('yamato_full.json');
        const data = await response.json();
        renderApp(data);
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

        document.getElementById('modalTitle').innerText = poem.title;

        const body = document.getElementById('modalBodyContent');
        body.innerHTML = ''; // basic clear

        // Build content matching Home design
        let html = `
            <div class="poem-modal-content">
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
    } catch (e) {
        console.error("Error in openModal:", e);
        alert("Erro ao abrir o modal. Verifique o console.");
    }
}

function closeModal() {
    const modal = document.getElementById('contentModal');
    if (modal) modal.classList.remove('active');
}

// Ensure global access
window.openModal = openModal;
window.closeModal = closeModal;

// Close on outside click is handled in HTML inline or we add listener here
document.addEventListener('click', (e) => {
    if (e.target && e.target.id === 'contentModal') {
        closeModal();
    }
});
