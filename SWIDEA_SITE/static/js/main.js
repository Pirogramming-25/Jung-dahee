// CSRF 토큰 쿠키에서 읽기
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}
const CSRF_TOKEN = getCookie('csrftoken');

/* ---------- 찜(star) 토글 ---------- */
function bindStarButtons(root = document) {
  root.querySelectorAll('.star-btn[data-idea-id]').forEach((btn) => {
    if (btn.dataset.bound) return;
    btn.dataset.bound = '1';
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const ideaId = btn.dataset.ideaId;

      try {
        const res = await fetch(`/${ideaId}/star/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': CSRF_TOKEN,
            'Content-Type': 'application/json',
          },
        });
        if (!res.ok) throw new Error('요청 실패');
        const data = await res.json();
        btn.classList.toggle('starred', data.starred);
        btn.classList.add('animate');
        setTimeout(() => btn.classList.remove('animate'), 300);
        btn.textContent = data.starred ? '★' : '☆';

        document.querySelectorAll(`.star-count[data-idea-id="${ideaId}"]`).forEach((el) => {
          el.textContent = data.star_count;
        });
      } catch (err) {
        console.error('찜 처리 오류:', err);
      }
    });
  });
}

/* ---------- 관심도 +/- ---------- */
function bindInterestButtons(root = document) {
  root.querySelectorAll('.interest-btn[data-idea-id]').forEach((btn) => {
    if (btn.dataset.bound) return;
    btn.dataset.bound = '1';
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const ideaId = btn.dataset.ideaId;
      const delta = parseInt(btn.dataset.delta, 10);

      try {
        const res = await fetch(`/${ideaId}/interest/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': CSRF_TOKEN,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ delta }),
        });
        if (!res.ok) throw new Error('요청 실패');
        const data = await res.json();
        document.querySelectorAll(`.interest-value[data-idea-id="${ideaId}"]`).forEach((el) => {
          el.textContent = data.interest;
        });
      } catch (err) {
        console.error('관심도 처리 오류:', err);
      }
    });
  });
}

/* ---------- AJAX 검색/정렬/필터/페이지네이션 (메인 리스트 페이지) ---------- */
function initIdeaSearch() {
  const form = document.getElementById('idea-filter-form');
  const grid = document.getElementById('idea-grid-container');
  if (!form || !grid) return;

  let debounceTimer = null;

  async function loadIdeas(params, pushState = true) {
    const query = new URLSearchParams(params).toString();
    try {
      const res = await fetch(`/search/?${query}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
      });
      const data = await res.json();
      grid.innerHTML = data.html;
      bindStarButtons(grid);
      bindInterestButtons(grid);
      bindPaginationLinks();
      if (pushState) {
        const newUrl = `${window.location.pathname}?${query}`;
        window.history.replaceState({}, '', newUrl);
      }
    } catch (err) {
      console.error('검색 오류:', err);
    }
  }

  function currentParams(page = 1) {
    const formData = new FormData(form);
    const params = {};
    for (const [key, value] of formData.entries()) {
      if (value) params[key] = value;
    }
    params.page = page;
    return params;
  }

  function bindPaginationLinks() {
    grid.querySelectorAll('.ajax-page-link').forEach((link) => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const page = link.dataset.page;
        loadIdeas(currentParams(page));
      });
    });
  }

  form.querySelectorAll('select[name="sort"], select[name="devtool"]').forEach((el) => {
    el.addEventListener('change', () => loadIdeas(currentParams(1)));
  });

  const searchInput = form.querySelector('input[name="q"]');
  if (searchInput) {
    searchInput.addEventListener('input', () => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => loadIdeas(currentParams(1)), 350);
    });
  }

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    loadIdeas(currentParams(1));
  });

  bindPaginationLinks();
}

document.addEventListener('DOMContentLoaded', () => {
  bindStarButtons();
  bindInterestButtons();
  initIdeaSearch();
});
