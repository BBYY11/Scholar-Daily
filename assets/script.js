// 每日一书 · 客户端脚本 v2
// 归档页：按月份分块渲染 + 领域筛选 + 月份折叠

(function () {
  // ---------- 首页日期 ----------
  const dateEl = document.getElementById('today-date');
  if (dateEl) {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    dateEl.textContent = `${yyyy}-${mm}-${dd}`;
  }

  // ---------- 归档页：月份分块 + 筛选 ----------
  const timeline = document.getElementById('archive-timeline');
  if (!timeline) return;

  const filterBar = document.getElementById('filter-bar');
  let activeFilter = 'all';

  function applyFilter() {
    if (!timeline) return;
    const months = timeline.querySelectorAll('.month-block');
    months.forEach(month => {
      const items = month.querySelectorAll('.timeline-item');
      let visibleCount = 0;
      items.forEach(item => {
        const tags = (item.dataset.tags || '').split('|').map(s => s.trim());
        const match = activeFilter === 'all' || tags.includes(activeFilter);
        item.classList.toggle('hidden', !match);
        if (match) visibleCount++;
        // 高亮匹配的 tag
        item.querySelectorAll('.timeline-tags span').forEach(span => {
          const t = span.textContent.replace(/（.*）/, '').trim();
          if (activeFilter === 'all') {
            span.classList.remove('match', 'nomatch');
          } else {
            span.classList.toggle('match', t === activeFilter);
            span.classList.toggle('nomatch', t !== activeFilter);
          }
        });
      });
      // 如果整个月份都没匹配，隐藏月份标题
      month.style.display = visibleCount === 0 ? 'none' : '';
    });
  }

  if (filterBar) {
    filterBar.addEventListener('click', e => {
      const chip = e.target.closest('.filter-chip');
      if (!chip) return;
      filterBar.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      activeFilter = chip.dataset.filter;
      applyFilter();
    });
  }

  // 月份折叠
  document.body.addEventListener('click', e => {
    const header = e.target.closest('.month-header');
    if (!header) return;
    header.parentElement.classList.toggle('collapsed');
  });

  // 拉取归档
  fetch('archive/index.json', { cache: 'no-store' })
    .then(r => r.ok ? r.json() : [])
    .then(blocks => {
      if (!blocks.length) return;
      timeline.innerHTML = '';
      blocks.forEach(block => {
        const wrap = document.createElement('div');
        wrap.className = 'month-block';
        const header = document.createElement('h2');
        header.className = 'month-header';
        const [y, m] = block.month.split('-');
        header.textContent = `${y} 年 ${parseInt(m, 10)} 月`;
        wrap.appendChild(header);

        const body = document.createElement('div');
        body.className = 'month-body';
        block.items.forEach(it => {
          const el = document.createElement('div');
          el.className = 'timeline-item';
          el.dataset.tags = (it.tags || []).join('|');
          // 6.15 起点首期 特殊处理
          const firstBadge = it.date === '2026-06-16' ? ' <span class="timeline-first">起点 · 首期</span>' : '';
          el.innerHTML = `
            <div class="timeline-date">${it.date}${firstBadge}</div>
            <div class="timeline-tags">${(it.tags || []).map(t => `<span>${t}</span>`).join('')}</div>
            <a class="timeline-link" href="archive/${it.date}.html">查看 →</a>
          `;
          body.appendChild(el);
        });
        wrap.appendChild(body);
        timeline.appendChild(wrap);
      });
    })
    .catch(() => {});
})();
