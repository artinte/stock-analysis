/* =========================================================
   STOCK LAB - 学习文章
   目录滚动定位
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const tocLinks =
            document.querySelectorAll(
                ".toc-list a"
            );

        const sections = [];

        tocLinks.forEach(
            link => {

                const id =
                    link.getAttribute(
                        "href"
                    );

                if (
                    !id ||
                    !id.startsWith("#")
                ) {
                    return;
                }

                const section =
                    document.querySelector(
                        id
                    );

                if (section) {

                    sections.push({
                        element: section,
                        link: link
                    });

                }

            }
        );


        if (!sections.length) {
            return;
        }


        const observer =
            new IntersectionObserver(
                entries => {

                    entries.forEach(
                        entry => {

                            if (
                                !entry.isIntersecting
                            ) {
                                return;
                            }

                            sections.forEach(
                                item => {

                                    item.link.classList.remove(
                                        "active"
                                    );

                                }
                            );


                            const current =
                                sections.find(
                                    item =>
                                        item.element ===
                                        entry.target
                                );


                            if (current) {

                                current.link.classList.add(
                                    "active"
                                );

                            }

                        }
                    );

                },
                {
                    root: null,
                    rootMargin:
                        "-15% 0px -65% 0px",
                    threshold: 0
                }
            );


        sections.forEach(
            item => {

                observer.observe(
                    item.element
                );

            }
        );

    }
);