async function loadComponent(selector, url) {
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

    } catch (error) {
        console.error("组件加载失败:", error);
    }
}