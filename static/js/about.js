document.addEventListener("DOMContentLoaded", () => {
  const valueCards = document.querySelectorAll(".js-value-card");
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            entry.target.classList.add("is-visible");
          }, index * 100);
          revealObserver.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 },
  );

  valueCards.forEach((card) => revealObserver.observe(card));

  const cta = document.querySelector(".js-cta-section");
  if (cta) {
    cta.addEventListener("mousemove", (e) => {
      const rect = cta.getBoundingClientRect();
      cta.style.setProperty("--mouse-x", `${e.clientX - rect.left}px`);
      cta.style.setProperty("--mouse-y", `${e.clientY - rect.top}px`);
    });
  }
});
