// Theme init (runs immediately)
(function(){var t=localStorage.getItem('kumo-theme');if(t&&t!=='default')document.body.classList.add('theme-'+t);})();

// Main UI components
(function() {
    // ── Scroll Progress Bar ──
    var progressBar = document.createElement('div');
    progressBar.className = 'scroll-progress';
    document.body.prepend(progressBar);

    // ── Word Count ──
    var ps = document.querySelectorAll('p');
    var total = 0;
    for (var i = 0; i < ps.length; i++) {
        var t = ps[i].textContent.trim();
        if (t.length > 0) {
            total += t.split(/\s+/).length;
        }
    }
    var h1 = document.querySelector('h1');
    if (h1) {
        var wc = document.createElement('div');
        wc.className = 'word-count';
        wc.textContent = '\u270E T\u1ed5ng s\u1ed1 t\u1eeb: ' + total.toLocaleString('vi-VN');
        var nextEl = h1.nextElementSibling;
        h1.parentNode.insertBefore(wc, nextEl && nextEl.tagName === 'H2' ? nextEl.nextSibling : h1.nextSibling);
    }

    // ── Floating Nav ──
    var navs = document.querySelectorAll('.chapter-nav');
    if (navs.length > 0) {
        var src = navs[0];
        var floatNav = document.createElement('div');
        floatNav.className = 'floating-nav';
        floatNav.id = 'floatingNav';

        for (var j = 0; j < src.children.length; j++) {
            var ch = src.children[j];
            var el;
            if (ch.tagName === 'A') {
                el = document.createElement('a');
                el.href = ch.getAttribute('href');
                el.innerHTML = ch.innerHTML;
            } else {
                el = document.createElement('span');
                el.className = 'nav-disabled';
                el.innerHTML = ch.innerHTML;
            }
            floatNav.appendChild(el);
        }
        document.body.appendChild(floatNav);

        // Toggle tab
        var toggle = document.createElement('div');
        toggle.className = 'nav-toggle';
        toggle.id = 'navToggle';
        toggle.innerHTML = '\u25C0';
        document.body.appendChild(toggle);

        var isOpen = false;
        function toggleNav() {
            isOpen = !isOpen;
            floatNav.classList.toggle('visible', isOpen);
            toggle.classList.toggle('shifted', isOpen);
            toggle.innerHTML = isOpen ? '\u25B6' : '\u25C0';
        }

        toggle.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleNav();
        });

        var isMobile = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
        if (isMobile) {
            document.addEventListener('click', function(e) {
                if (!floatNav.contains(e.target) && e.target !== toggle && !toggle.contains(e.target)) {
                    if (isOpen) toggleNav();
                }
            });
        }
    }

    // ── Scroll to Top Button ──
    var scrollBtn = document.createElement('div');
    scrollBtn.className = 'scroll-top';
    scrollBtn.innerHTML = '\u2191';
    scrollBtn.title = 'V\u1ec1 \u0111\u1ea7u trang';
    document.body.appendChild(scrollBtn);

    scrollBtn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // ── Scroll Events ──
    window.addEventListener('scroll', function() {
        var scrollTop = window.scrollY || document.documentElement.scrollTop;
        var docHeight = document.documentElement.scrollHeight - window.innerHeight;
        var progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
        progressBar.style.width = progress + '%';
        scrollBtn.classList.toggle('visible', scrollTop > 400);
    }, { passive: true });
})();

// Theme Picker
(function() {
    var themes = [
        { id: 'default', label: 'M\u1eb7c \u0111\u1ecbnh', color: 'linear-gradient(135deg, #2d8b70, #50c8aa)' },
        { id: 'gray', label: 'X\u00e1m', color: '#555' },
        { id: 'black', label: '\u0110en', color: '#111' },
        { id: 'white', label: 'Tr\u1eafng', color: '#eee' }
    ];

    var saved = localStorage.getItem('kumo-theme') || 'default';

    var picker = document.createElement('div');
    picker.className = 'theme-picker';

    var btn = document.createElement('div');
    btn.className = 'theme-picker-btn';
    btn.innerHTML = '\uD83C\uDFA8';
    btn.title = '\u0110\u1ed5i giao di\u1ec7n';

    var opts = document.createElement('div');
    opts.className = 'theme-options';

    themes.forEach(function(t) {
        var o = document.createElement('div');
        o.className = 'theme-option' + (t.id === saved ? ' active' : '');
        o.style.background = t.color;
        o.title = t.label;
        if (t.id === 'white') o.style.border = '2px solid #ccc';
        o.addEventListener('click', function(e) {
            e.stopPropagation();
            themes.forEach(function(th) { document.body.classList.remove('theme-' + th.id); });
            if (t.id !== 'default') document.body.classList.add('theme-' + t.id);
            localStorage.setItem('kumo-theme', t.id);
            opts.querySelectorAll('.theme-option').forEach(function(el) { el.classList.remove('active'); });
            o.classList.add('active');
        });
        opts.appendChild(o);
    });

    var open = false;
    btn.addEventListener('click', function(e) {
        e.stopPropagation();
        open = !open;
        opts.classList.toggle('visible', open);
    });

    document.addEventListener('click', function() {
        if (open) { open = false; opts.classList.remove('visible'); }
    });

    picker.appendChild(opts);
    picker.appendChild(btn);
    document.body.appendChild(picker);
})();
