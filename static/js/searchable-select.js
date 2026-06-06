(function () {
  const instances = new WeakMap();

  function normalizeText(value) {
    return String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .trim();
  }

  function optionLabel(option) {
    return option ? option.textContent.trim() : "";
  }

  class SearchableSelectInstance {
    constructor(select, options) {
      this.select = select;
      this.options = options || {};
      this.isOpen = false;
      this.lastQuery = "";

      this.wrapper = document.createElement("div");
      this.wrapper.className = "searchable-select";

      this.input = document.createElement("input");
      this.input.type = "text";
      this.input.className = "searchable-select-input";
      this.input.autocomplete = "off";
      this.input.spellcheck = false;
      this.input.setAttribute("role", "combobox");
      this.input.setAttribute("aria-expanded", "false");

      this.dropdown = document.createElement("div");
      this.dropdown.className = "searchable-select-dropdown";
      this.dropdown.setAttribute("role", "listbox");

      this.wrapper.appendChild(this.input);
      this.wrapper.appendChild(this.dropdown);

      this.select.classList.add("searchable-select-native");
      this.select.insertAdjacentElement("afterend", this.wrapper);

      this.bindEvents();
      this.observeSelect();
      this.update(options);
    }

    bindEvents() {
      this.input.addEventListener("focus", () => {
        if (this.select.disabled) return;
        if (!this.select.value) this.input.value = "";
        this.open();
        this.renderOptions(this.input.value);
      });

      this.input.addEventListener("input", () => {
        if (this.select.disabled) return;
        this.open();
        this.renderOptions(this.input.value);
      });

      this.input.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
          this.close();
          this.restoreSelectedLabel();
          return;
        }

        if (event.key !== "Enter") return;

        const firstOption = this.dropdown.querySelector(".searchable-select-option");
        if (!firstOption) return;

        event.preventDefault();
        this.choose(firstOption.dataset.value || "");
      });

      this.dropdown.addEventListener("mousedown", (event) => {
        event.preventDefault();
      });

      this.dropdown.addEventListener("click", (event) => {
        if (!(event.target instanceof Element)) return;

        const option = event.target.closest(".searchable-select-option");
        if (!option) return;
        this.choose(option.dataset.value || "");
      });

      this.select.addEventListener("change", () => {
        this.update();
      });

      document.addEventListener("click", (event) => {
        if (this.wrapper.contains(event.target)) return;
        this.close();
        this.restoreSelectedLabel();
      });
    }

    observeSelect() {
      if (!window.MutationObserver) return;

      this.observer = new MutationObserver(() => this.update());
      this.observer.observe(this.select, {
        attributes: true,
        attributeFilter: ["disabled"],
        childList: true,
        subtree: true
      });
    }

    update(options) {
      if (options) this.options = { ...this.options, ...options };

      this.wrapper.classList.toggle("is-disabled", this.select.disabled);
      this.input.disabled = this.select.disabled;
      this.input.placeholder = this.options.placeholder || "Pesquisar";

      this.restoreSelectedLabel();
      this.renderOptions(this.lastQuery);
    }

    selectedOption() {
      return Array.from(this.select.options).find((option) => option.value === this.select.value)
        || this.select.options[this.select.selectedIndex]
        || null;
    }

    restoreSelectedLabel() {
      const selected = this.selectedOption();
      this.input.value = optionLabel(selected);
    }

    open() {
      if (this.select.disabled) return;
      this.isOpen = true;
      this.dropdown.classList.add("is-open");
      this.input.setAttribute("aria-expanded", "true");
    }

    close() {
      this.isOpen = false;
      this.dropdown.classList.remove("is-open");
      this.input.setAttribute("aria-expanded", "false");
    }

    renderOptions(query) {
      this.lastQuery = query || "";
      const normalizedQuery = normalizeText(query);
      const options = Array.from(this.select.options).filter((option) =>
        normalizeText(optionLabel(option)).includes(normalizedQuery)
      );

      if (!options.length) {
        this.dropdown.replaceChildren();
        const empty = document.createElement("div");
        empty.className = "searchable-select-empty";
        empty.textContent = "Nenhum resultado encontrado";
        this.dropdown.appendChild(empty);
        return;
      }

      const fragment = document.createDocumentFragment();

      options.forEach((option) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "searchable-select-option";
        button.dataset.value = option.value;
        button.textContent = optionLabel(option);
        if (option.value === this.select.value) {
          button.classList.add("is-selected");
        }
        fragment.appendChild(button);
      });

      this.dropdown.replaceChildren(fragment);
    }

    choose(value) {
      if (this.select.disabled) return;

      this.select.value = value;
      this.restoreSelectedLabel();
      this.close();
      this.select.dispatchEvent(new Event("change", { bubbles: true }));
    }
  }

  window.SearchableSelect = {
    enhance(select, options) {
      if (!select) return null;

      const currentInstance = instances.get(select);
      if (currentInstance) {
        currentInstance.update(options);
        return currentInstance;
      }

      const instance = new SearchableSelectInstance(select, options);
      instances.set(select, instance);
      return instance;
    }
  };
})();
