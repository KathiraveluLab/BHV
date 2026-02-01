document.addEventListener("DOMContentLoaded", () => {
  const cards = document.querySelectorAll(".js-reveal");
  cards.forEach((card, index) => {
    setTimeout(() => {
      card.style.opacity = "1";
      card.style.transform = "translateY(0)";
    }, index * 40); 
  });

  document.querySelectorAll(".js-delete-form").forEach((form) => {
    form.addEventListener("submit", (e) => {
      if (!confirm("Are you sure you want to delete this clinical record?")) {
        e.preventDefault();
      } else {
        const btn = form.querySelector("button");
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Removing...';
        btn.disabled = true;
      }
    });
  });
});
