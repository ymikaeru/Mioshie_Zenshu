function toggleLang(lang) {
    const ptContent = document.getElementById('pt-content');
    const jpContent = document.getElementById('jp-content');
    const btnPt = document.getElementById('btn-pt');
    const btnJp = document.getElementById('btn-jp');
    const btnCompare = document.getElementById('btn-compare');

    if (lang === 'pt') {
        ptContent.style.display = 'block';
        jpContent.style.display = 'none';
        btnPt.classList.add('active');
        btnJp.classList.remove('active');
        btnCompare.classList.remove('active');
    } else if (lang === 'jp') {
        ptContent.style.display = 'none';
        jpContent.style.display = 'block';
        btnPt.classList.remove('active');
        btnJp.classList.add('active');
        btnCompare.classList.remove('active');
    } else if (lang === 'compare') {
        ptContent.style.display = 'block';
        jpContent.style.display = 'block';
        btnPt.classList.remove('active');
        btnJp.classList.remove('active');
        btnCompare.classList.add('active');
    }
}
