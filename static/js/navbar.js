document.addEventListener("DOMContentLoaded", function () {
  const menuItems = document.querySelectorAll(".menu li");
  const border = document.querySelector(".border");

  if (!menuItems.length || !border) return;

  menuItems.forEach(item => {
    item.addEventListener("mouseenter", () => {
      const itemRect = item.getBoundingClientRect();
      const menuRect = item.parentNode.getBoundingClientRect();

      border.style.transform =
        `translateX(${itemRect.left - menuRect.left}px)`;
      border.style.width = `${itemRect.width}px`;
    });

    item.addEventListener("mouseleave", () => {
      border.style.width = "0px";
    });
  });
});
