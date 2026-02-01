document.addEventListener("DOMContentLoaded", () => {
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("userFileInput");
  const previewImg = document.getElementById("uImagePreview");
  const previewPlaceholder = document.getElementById("uPreviewContainer");

  const uploadForm = document.getElementById("userUploadForm");
  const submitBtn = document.getElementById("userSubmitBtn");
  const textLabel = document.getElementById("uText");
  const loadingLabel = document.getElementById("uLoading");

  if (dropZone && fileInput) {
    dropZone.addEventListener("click", () => fileInput.click());

    dropZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZone.classList.add("active");
    });

    ["dragleave", "drop"].forEach((evt) =>
      dropZone.addEventListener(evt, () => dropZone.classList.remove("active")),
    );

    dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        showPreview(fileInput.files[0]);
      }
    });

    fileInput.addEventListener("change", () => {
      if (fileInput.files.length) {
        showPreview(fileInput.files[0]);
      }
    });
  }

  function showPreview(file) {
    if (!file.type.startsWith("image/")) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      previewImg.style.display = "block";
      previewPlaceholder.style.display = "none";
    };
    reader.readAsDataURL(file);
  }

  if (uploadForm) {
    uploadForm.addEventListener("submit", () => {
      textLabel.classList.add("u-hidden");
      loadingLabel.classList.remove("u-hidden");
      loadingLabel.style.display = "inline-flex";

      submitBtn.disabled = true;
      submitBtn.classList.add("btn-loading");
    });
  }

  const modal = document.getElementById("editModalOverlay");
  const editForm = document.getElementById("editForm");
  const editDesc = document.getElementById("editDescription");
  const editSent = document.getElementById("editSentiment");
  const closeModalBtn = document.querySelector(".js-close-modal");

  document.querySelectorAll(".js-edit-trigger").forEach((btn) => {
    btn.addEventListener("click", () => {
      editForm.action = `/edit/${btn.dataset.id}`;
      editDesc.value = btn.dataset.desc || "";
      editSent.value = btn.dataset.sent || "Neutral";
      modal.style.display = "flex";
    });
  });

  closeModalBtn?.addEventListener("click", () => {
    modal.style.display = "none";
  });

  window.addEventListener("click", (e) => {
    if (e.target === modal) {
      modal.style.display = "none";
    }
  });
});
