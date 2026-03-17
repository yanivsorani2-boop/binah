/* ── Site Search — binah.co.il ── */
(function () {
  var INDEX = [
    { title: 'Claude 3.7 נגד GPT-4o: מי המודל הטוב ביותר?', url: 'article_claude_vs_gpt4o.html', cat: 'השוואה' },
    { title: '5 כלי AI לעריכת וידאו שחוסכים 10 שעות בשבוע', url: 'article2_ai_video_tools.html', cat: 'כלים' },
    { title: 'Vibe Coding: כיצד לבנות אפליקציה בלי לתכנת', url: 'article3_vibe_coding.html', cat: 'מדריך' },
    { title: 'DeepSeek R2: המודל הסיני שמאיים על ChatGPT', url: 'articles/deepseek-r2.html', cat: 'ניתוח' },
    { title: 'Sora של OpenAI: עתיד יצירת הווידאו עם AI', url: 'articles/sora-openai.html', cat: 'חדשות' },
    { title: 'Perplexity AI: מנוע החיפוש שמאיים על גוגל', url: 'articles/perplexity-ai.html', cat: 'כלים' },
    { title: 'Gemini של Google ב-2025: כל מה שצריך לדעת', url: 'articles/gemini-2025.html', cat: 'כלים' },
    { title: 'מדריך Prompt Engineering: כיצד לדבר עם AI נכון', url: 'articles/prompt-engineering.html', cat: 'מדריך' },
    { title: 'Ollama: כיצד להריץ AI בחינם על המחשב שלך', url: 'articles/ollama-guide.html', cat: 'מדריך' },
    { title: 'Midjourney למתחילים: יצירת תמונות AI בקלות', url: 'articles/midjourney-beginners.html', cat: 'מדריך' },
    { title: '7 כלי AI שכל עסק קטן צריך ב-2025', url: 'articles/ai-small-business.html', cat: 'עסקים' },
    { title: 'כיצד AI משנה את שוק העבודה ב-2025', url: 'articles/ai-jobs-2025.html', cat: 'ניתוח' },
    { title: '10 שימושים ל-ChatGPT שלא ידעתם שאפשר', url: 'articles/chatgpt-10-uses.html', cat: 'כלים' },
    { title: 'GPT-5 הושק רשמית — ומשנה את כל הכללים', url: 'articles/gpt5-launch.html', cat: 'חדשות' },
    { title: 'כלי AI שתומכים בעברית — המדריך המלא', url: 'articles/ai-tools-hebrew.html', cat: 'מדריך' },
    { title: 'AI לעסקים ישראלים — מדריך מעשי', url: 'articles/ai-for-business-israel.html', cat: 'עסקים' },
    { title: 'Claude vs GPT vs Gemini — השוואה מלאה 2026', url: 'articles/claude-vs-gpt-vs-gemini.html', cat: 'השוואה' },
    { title: 'מה זה Prompt Engineering ולמה זה חשוב', url: 'articles/what-is-prompt-engineering.html', cat: 'מדריך' },
    { title: 'מדריך הרשמה ל-ChatGPT שלב אחר שלב', url: 'guides/guide-chatgpt.html', cat: 'מדריך' },
    { title: 'מדריך הרשמה ל-Claude AI', url: 'guides/guide-claude.html', cat: 'מדריך' },
    { title: 'Ollama — הרצת AI על המחשב שלך', url: 'guides/guide-ollama.html', cat: 'מדריך' },
    { title: 'Midjourney — יצירת תמונות AI', url: 'guides/guide-midjourney.html', cat: 'מדריך' },
    { title: 'Prompt Engineering — הבסיס', url: 'guides/guide-prompt-basics.html', cat: 'מדריך' },
    { title: 'Chain of Thought — לגרום ל-AI לחשוב בקול', url: 'guides/guide-prompt-cot.html', cat: 'מדריך' },
    { title: 'פרומפטים עם תפקיד ומשימה', url: 'guides/guide-prompt-role.html', cat: 'מדריך' },
    { title: 'כלי AI — מדריך מלא לכל הכלים', url: 'tools.html', cat: 'כלים' },
    { title: 'איזה AI מתאים לך? — שאלון', url: 'quiz.html', cat: 'כלים' },
  ];

  function init() {
    var wrap = document.getElementById('site-search');
    if (!wrap) return;
    var input = wrap.querySelector('.search-input');
    var drop  = wrap.querySelector('.search-dropdown');
    if (!input || !drop) return;

    var timer;
    input.addEventListener('input', function () {
      clearTimeout(timer);
      timer = setTimeout(function () { doSearch(input.value.trim()); }, 180);
    });

    input.addEventListener('focus', function () {
      if (input.value.trim()) drop.classList.add('open');
    });

    document.addEventListener('click', function (e) {
      if (!wrap.contains(e.target)) drop.classList.remove('open');
    });

    function doSearch(q) {
      drop.innerHTML = '';
      if (!q) { drop.classList.remove('open'); return; }
      var lq = q.toLowerCase();
      var hits = INDEX.filter(function (item) {
        return item.title.toLowerCase().indexOf(lq) > -1 ||
               item.cat.toLowerCase().indexOf(lq) > -1;
      }).slice(0, 8);

      if (!hits.length) {
        drop.innerHTML = '<div class="search-empty">לא נמצאו תוצאות</div>';
      } else {
        hits.forEach(function (item) {
          var el = document.createElement('div');
          el.className = 'search-result-item';
          el.innerHTML = '<div class="search-result-title">' + item.title + '</div>' +
                         '<div class="search-result-cat">' + item.cat + '</div>';
          el.addEventListener('click', function () { window.location.href = item.url; });
          drop.appendChild(el);
        });
      }
      drop.classList.add('open');
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
