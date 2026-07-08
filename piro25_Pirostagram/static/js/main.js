function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

const csrftoken = getCookie('csrftoken');

/* ---------------------------------------------------------------------
 * 1440px 고정 디자인을 화면 폭에 맞춰 "비율 그대로" 축소시키기
 * (zoom 속성으로 .layout 박스 자체의 실제 레이아웃 크기를 줄인다.
 *  transform: scale()과 달리 zoom은 브라우저가 계산하는 실제 박스 크기와
 *  스크롤 가능 영역을 함께 바꿔주므로, 별도 래퍼나 크기 동기화 없이도
 *  가로 스크롤이 생기거나 그림자/드롭다운이 잘리는 문제 없이 깔끔하게 축소된다.)
 * ------------------------------------------------------------------- */
function applyLayoutZoom() {
    const layout = document.querySelector('.layout');
    if (!layout) return;

    const baseWidth = 1440;
    // window.innerWidth는 세로 스크롤바 두께까지 포함한 값이라,
    // 세로 스크롤이 생기는 페이지에서는 실제 가로로 쓸 수 있는 폭보다 커진다.
    // 그 차이(보통 15~17px)만큼 매번 계산이 살짝 커져서 결과적으로 항상
    // 가로 스크롤이 아주 조금씩 남아있었던 것 — document.documentElement.clientWidth는
    // 스크롤바 두께를 뺀 "진짜" 가로 폭이라 이걸 기준으로 계산해야 정확하다.
    const viewportWidth = document.documentElement.clientWidth;
    const scale = Math.min(1, viewportWidth / baseWidth);

    layout.style.zoom = scale;
}

window.addEventListener('resize', applyLayoutZoom);
document.addEventListener('DOMContentLoaded', applyLayoutZoom);
applyLayoutZoom();

function postForm(url, data) {
    const body = new URLSearchParams(data);
    return fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: body,
    }).then((res) => res.json().then((json) => ({ ok: res.ok, json })));
}

document.addEventListener('DOMContentLoaded', () => {
    // 좋아요 토글
    document.querySelectorAll('.like-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
            const postId = btn.dataset.postId;
            postForm(`/posts/${postId}/like/`, {}).then(({ json }) => {
                btn.classList.toggle('liked', json.liked);
                const countEl = document.querySelector(`.like-count[data-post-id="${postId}"]`);
                if (countEl) countEl.textContent = json.like_count;
            });
        });
    });

    // 팔로우 토글 (피드 추천 목록/프로필)
    document.querySelectorAll('.follow-toggle-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
            const username = btn.dataset.username;
            postForm(`/accounts/profile/${username}/follow/`, {}).then(({ json }) => {
                btn.textContent = json.is_following ? '팔로잉' : '팔로우';
                btn.classList.toggle('following', json.is_following);
                const countEl = document.querySelector('.follower-count');
                if (countEl) countEl.textContent = json.follower_count;
            });
        });
    });

    // 댓글창 토글
    document.querySelectorAll('.comment-toggle-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
            const postId = btn.dataset.postId;
            const section = document.querySelector(`.comments-section[data-post-id="${postId}"]`);
            if (section) section.classList.toggle('hidden');
        });
    });

    // 댓글 작성
    document.querySelectorAll('.comment-form').forEach((form) => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const postId = form.dataset.postId;
            const input = form.querySelector('input[name=content]');
            const content = input.value.trim();
            if (!content) return;
            postForm(`/posts/${postId}/comments/`, { content }).then(({ ok, json }) => {
                if (!ok) return;
                const list = document.querySelector(`.comment-list[data-post-id="${postId}"]`);
                const row = document.createElement('div');
                row.className = 'comment-row';
                row.dataset.commentId = json.id;
                row.innerHTML = `<div><span class="username">${json.author}</span><span class="comment-content">${json.content}</span></div>
                    <div class="comment-row-actions">
                        <button type="button" class="comment-edit-btn">수정</button>
                        <button type="button" class="comment-delete-btn">삭제</button>
                    </div>`;
                list.appendChild(row);
                bindCommentRow(row, postId);
                input.value = '';
                const countEl = document.querySelector(`.comment-count[data-post-id="${postId}"]`);
                if (countEl) countEl.textContent = json.comment_count;
            });
        });
    });

    document.querySelectorAll('.comment-row').forEach((row) => {
        const postId = row.closest('.comment-list').dataset.postId;
        bindCommentRow(row, postId);
    });

    // 검색 결과 페이지 상단의 "..." 메뉴 토글
    const menuBtn = document.getElementById('search-menu-btn');
    const menuDropdown = document.getElementById('search-menu-dropdown');
    if (menuBtn && menuDropdown) {
        menuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            menuDropdown.classList.toggle('hidden');
        });
        document.addEventListener('click', (e) => {
            if (!menuDropdown.contains(e.target) && e.target !== menuBtn) {
                menuDropdown.classList.add('hidden');
            }
        });
    }
});

function bindCommentRow(row, postId) {
    const editBtn = row.querySelector('.comment-edit-btn');
    const deleteBtn = row.querySelector('.comment-delete-btn');
    const contentSpan = row.querySelector('.comment-content');
    const commentId = row.dataset.commentId;

    editBtn.addEventListener('click', () => {
        if (row.querySelector('.comment-edit-input')) return;
        const current = contentSpan.textContent;
        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'comment-edit-input';
        input.value = current;
        contentSpan.replaceWith(input);
        input.focus();
        editBtn.textContent = '저장';

        const save = () => {
            const newContent = input.value.trim();
            if (!newContent) return;
            postForm(`/comments/${commentId}/edit/`, { content: newContent }).then(({ ok, json }) => {
                if (!ok) return;
                const span = document.createElement('span');
                span.className = 'comment-content';
                span.textContent = json.content;
                input.replaceWith(span);
                editBtn.textContent = '수정';
            });
        };
        editBtn.onclick = save;
    });

    deleteBtn.addEventListener('click', () => {
        if (!confirm('댓글을 삭제할까요?')) return;
        postForm(`/comments/${commentId}/delete/`, {}).then(({ ok, json }) => {
            if (!ok) return;
            row.remove();
            const countEl = document.querySelector(`.comment-count[data-post-id="${postId}"]`);
            if (countEl) countEl.textContent = json.comment_count;
        });
    });
}