/**
 * 加载公共 HTML 组件
 *
 * @param {string} selector - 组件容器选择器
 * @param {string} url - 组件 HTML 路径
 * @param {string|null} currentPage - 当前页面标识
 */
async function loadComponent(selector, url, currentPage = null) {
    const container = document.querySelector(selector);

    if (!container) {
        return;
    }

    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`组件加载失败: ${response.status}`);
        }

        container.innerHTML = await response.text();

        // 设置当前页面导航高亮
        if (currentPage) {
            const navItems = container.querySelectorAll(".nav-item");

            navItems.forEach((item) => {
                item.classList.toggle(
                    "active",
                    item.dataset.page === currentPage
                );
            });
        }

    } catch (error) {
        console.error("组件加载失败:", error);
    }
}