document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".js-reveal");

  const observerOptions = {
    threshold: 0.15,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target); 
      }
    });
  }, observerOptions);

  cards.forEach((card) => observer.observe(card));

  document.querySelectorAll(".js-hero-btn").forEach((btn) => {
    btn.addEventListener("mousedown", () => {
      btn.style.transform = "scale(0.97)";
    });
    btn.addEventListener("mouseup", () => {
      btn.style.transform = "";
    });
  });
});
