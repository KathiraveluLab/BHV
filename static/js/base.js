document.addEventListener("DOMContentLoaded", function () {
  const alertZone = document.getElementById("alertZone");

  if (alertZone) {
    const dismissAlert = (alert) => {
      alert.style.opacity = "0";
      alert.style.transform = "translateX(20px)";
      setTimeout(() => alert.remove(), 300);
    };

    alertZone.addEventListener("click", (e) => {
      const closeBtn = e.target.closest(".js-close-alert");
      if (closeBtn) {
        const alert = closeBtn.closest(".js-alert");
        if (alert) dismissAlert(alert);
      }
    });

    const alerts = alertZone.querySelectorAll(".js-alert");
    alerts.forEach((alert) => {
      setTimeout(() => {
        if (alert.parentNode) dismissAlert(alert);
      }, 3000);
    });
  }

  const navToggler = document.querySelector(".js-nav-toggler");
  const navMenu = document.querySelector(".js-nav-menu");

  if (navToggler && navMenu) {
    navToggler.addEventListener("click", (e) => {
      e.stopPropagation();
      navMenu.classList.toggle("is-open");
      navToggler.classList.toggle("is-active");
    });

    document.addEventListener("click", (e) => {
      if (!navMenu.contains(e.target) && !navToggler.contains(e.target)) {
        navMenu.classList.remove("is-open");
        navToggler.classList.remove("is-active");
      }
    });
  }
});
