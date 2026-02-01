document.addEventListener("DOMContentLoaded", function () {
  const adminGrid = document.querySelector(".admin-image-grid");

  if (adminGrid) {
    adminGrid.addEventListener("submit", function (e) {
      if (e.target.classList.contains("js-delete-form")) {
        if (
          !confirm(
            "This will permanently remove the record from Database and Cloud Storage. Proceed?",
          )
        ) {
          e.preventDefault();
        } else {
          const btn = e.target.querySelector("button");
          btn.disabled = true;
          btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Removing...';
        }
      }
    });
  }

  const cards = document.querySelectorAll(".js-reveal");
  cards.forEach((card, i) => {
    setTimeout(() => {
      card.style.opacity = "1";
      card.style.transform = "translateY(0)";
    }, i * 40);
  });

  document.querySelectorAll(".card-media img").forEach((img) => {
    img.onerror = function () {
      this.parentElement.innerHTML = `<div class="no-image"><i class="fas fa-image-slash"></i></div>`;
    };
  });
});
