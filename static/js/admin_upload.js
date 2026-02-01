document.addEventListener("DOMContentLoaded", function () {
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");
  const dropContent = document.getElementById("dropContent");
  const outputImage = document.getElementById("outputImage");
  const targetUserSelect = document.getElementById("targetUserSelect");
  const targetNameInput = document.getElementById("target_name");
  const adminModal = document.getElementById("adminModalOverlay");
  const adminEditForm = document.getElementById("adminEditForm");
  const uploadForm = document.getElementById("uploadForm");


  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ["dragenter", "dragover"].forEach((eventName) => {
    dropZone.addEventListener(
      eventName,
      () => {
        dropZone.classList.add("drag-active");
      },
      false,
    );
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropZone.addEventListener(
      eventName,
      () => {
        dropZone.classList.remove("drag-active");
      },
      false,
    );
  });

  dropZone.addEventListener("drop", (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length > 0) {
      fileInput.files = files; 
      handleFileSelect(fileInput);
    }
  });

  dropZone.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", function () {
    handleFileSelect(this);
  });


  function handleFileSelect(input) {
    const file = input.files[0];

    if (!file) return;

    if (!file.type.startsWith("image/")) {
      alert("Please upload a valid image file (JPG, PNG, etc).");
      input.value = ""; 
      return;
    }

    const reader = new FileReader();

    dropContent.innerHTML =
      '<i class="fas fa-circle-notch fa-spin"></i><p>Processing...</p>';

    reader.onload = function (e) {
      outputImage.src = e.target.result;
      outputImage.style.display = "block";
      dropContent.style.display = "none";

      dropZone.style.borderColor = "var(--success-green)";
    };

    reader.readAsDataURL(file);
  }


  if (targetUserSelect) {
    targetUserSelect.addEventListener("change", function () {
      targetNameInput.value = this.options[this.selectedIndex].text;
    });
  }


  document.body.addEventListener("click", function (e) {
    const editBtn = e.target.closest(".js-edit-btn");

    if (editBtn) {
      const uploadId = editBtn.getAttribute("data-id");
      const description = editBtn.getAttribute("data-desc");
      const sentiment = editBtn.getAttribute("data-sent");
      const aiDesc = editBtn.getAttribute("data-ai");

      adminEditForm.action = `/admin/edit/${uploadId}`;
      document.getElementById("modalDesc").value = description;
      document.getElementById("modalSent").value = sentiment;
      document.getElementById("modalAiDesc").value = aiDesc;

      adminModal.style.display = "flex";
    }

    if (
      e.target.id === "closeModal" ||
      e.target.id === "cancelModal" ||
      e.target === adminModal
    ) {
      adminModal.style.display = "none";
    }
  });


  if (uploadForm) {
    uploadForm.addEventListener("submit", function () {
      const btn = document.getElementById("submitBtn");
      btn.classList.add("btn-loading");
      btn.disabled = true; 
      btn.innerHTML =
        '<i class="fas fa-spinner fa-spin"></i> Uploading...';
    });
  }
});
