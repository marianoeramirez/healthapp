(function () {
  const dropzone = document.getElementById("upload-dropzone");
  const formset = document.getElementById("attachment-formset");
  if (!dropzone || !formset) return;

  const totalForms = document.getElementById("id_attachments-TOTAL_FORMS");
  const fileInputs = () =>
    Array.from(formset.querySelectorAll('input[type="file"]'));

  function nextEmptyInput() {
    return fileInputs().find((input) => !input.files || input.files.length === 0);
  }

  function assignFiles(fileList) {
    const files = Array.from(fileList || []);
    files.forEach((file) => {
      let input = nextEmptyInput();
      if (!input) {
        const current = parseInt(totalForms.value, 10);
        const emptyRow = formset.querySelector(".attachment-form");
        if (!emptyRow) return;
        const clone = emptyRow.cloneNode(true);
        clone.innerHTML = clone.innerHTML.replaceAll(
          `attachments-${current - 1}`,
          `attachments-${current}`
        );
        clone.querySelectorAll("input").forEach((el) => {
          if (el.type === "checkbox") el.checked = false;
          else el.value = "";
        });
        formset.appendChild(clone);
        totalForms.value = String(current + 1);
        input = nextEmptyInput();
      }
      if (!input) return;
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      input.files = dataTransfer.files;
      input.dispatchEvent(new Event("change", { bubbles: true }));
    });
  }

  ["dragenter", "dragover"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropzone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropzone.classList.remove("dragover");
    });
  });

  dropzone.addEventListener("drop", (event) => {
    assignFiles(event.dataTransfer.files);
  });

  dropzone.addEventListener("click", () => {
    const input = nextEmptyInput() || fileInputs()[0];
    if (input) input.click();
  });

  const personSelect = document.getElementById("id_person");
  const eventSelect = document.getElementById("id_event");
  const eventsByPerson = window.EVENTS_BY_PERSON || {};

  function refreshEvents() {
    if (!personSelect || !eventSelect) return;
    const personId = personSelect.value;
    const current = eventSelect.value;
    const options = eventsByPerson[personId] || [];
    eventSelect.innerHTML = '<option value="">---------</option>';
    options.forEach((event) => {
      const option = document.createElement("option");
      option.value = event.id;
      option.textContent = event.title;
      if (String(event.id) === String(current)) option.selected = true;
      eventSelect.appendChild(option);
    });
  }

  if (personSelect) {
    personSelect.addEventListener("change", refreshEvents);
    refreshEvents();
  }
})();
