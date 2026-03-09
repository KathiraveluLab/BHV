(function () {
    const THEME_KEY = "bhv-theme";

    const applyTheme = (theme) => {
        const nextTheme = theme === "light" ? "light" : "dark";
        document.documentElement.setAttribute("data-theme", nextTheme);
        try {
            localStorage.setItem(THEME_KEY, nextTheme);
        } catch (err) {
            // Ignore storage errors and keep runtime theme.
        }
    };

    const getSavedTheme = () => {
        try {
            return localStorage.getItem(THEME_KEY) || "dark";
        } catch (err) {
            return "dark";
        }
    };

    const bindSelectors = () => {
        const selectors = document.querySelectorAll("[data-theme-selector]");
        const toggles = document.querySelectorAll("[data-theme-toggle]");
        const icons = document.querySelectorAll("[data-theme-icon]");
        const current = document.documentElement.getAttribute("data-theme") || getSavedTheme();

        const updateToggleLabel = (theme) => {
            toggles.forEach((btn) => {
                btn.setAttribute(
                    "title",
                    theme === "dark" ? "Switch to light mode" : "Switch to dark mode"
                );
                btn.setAttribute(
                    "aria-label",
                    theme === "dark" ? "Switch to light mode" : "Switch to dark mode"
                );
            });

            icons.forEach((icon) => {
                icon.textContent = theme === "dark" ? "☀" : "☾";
            });
        };

        selectors.forEach((select) => {
            select.value = current;
            select.addEventListener("change", () => {
                applyTheme(select.value);
                selectors.forEach((other) => {
                    other.value = select.value;
                });
                updateToggleLabel(select.value);
            });
        });

        toggles.forEach((btn) => {
            btn.addEventListener("click", () => {
                const active = document.documentElement.getAttribute("data-theme") || getSavedTheme();
                const next = active === "dark" ? "light" : "dark";
                applyTheme(next);
                selectors.forEach((select) => {
                    select.value = next;
                });
                updateToggleLabel(next);
            });
        });

        updateToggleLabel(current);
    };

    if (!document.documentElement.getAttribute("data-theme")) {
        applyTheme(getSavedTheme());
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bindSelectors);
    } else {
        bindSelectors();
    }
})();
