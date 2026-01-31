const sidebar = document.getElementById('dynamic-sidebar');
const elements = Array.from(document.querySelectorAll('h2, h3, h4'));

elements.forEach(element => {
    if (!element.id) {
        element.id = `${element.tagName.toLowerCase()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    const link = document.createElement('a');
    link.href = `#${element.id}`;
    link.textContent = element.textContent;

    const listItem = document.createElement('li');
    if (element.tagName.toLowerCase() === 'h4') {
        listItem.style.marginLeft = '10px';
    }
    listItem.appendChild(link);

    sidebar.appendChild(listItem);
});

function highlightCurrentLink(targetId) {
    const links = sidebar.querySelectorAll('a');
    links.forEach(link => {
        if (link.getAttribute('href') === `#${targetId}`) {
            link.classList.add('highlight-link');
        } else {
            link.classList.remove('highlight-link');
        }
    });
}

window.addEventListener('scroll', () => {
    let found = false;
    elements.forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.top <= window.innerHeight / 2 && rect.bottom >= 0) {
            if (!found) {
                highlightCurrentLink(el.id);
                found = true;
            }
        }
    });
});

const links = sidebar.querySelectorAll('a');
links.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const targetId = link.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
            targetElement.scrollIntoView({ behavior: 'smooth' });
            highlightCurrentLink(targetId);
        }
    });
});
