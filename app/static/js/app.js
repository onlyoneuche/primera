"use strict";
// Answers live only in this closure. No browser storage, URLs, or third-party requests.
(() => {
  const main = document.querySelector("#app");
  const announcements = document.querySelector("#announcements");
  const dialog = document.querySelector("#about");
  const assetVersion = document.documentElement.dataset.assetVersion;
  let config, copy, answers = {}, step = 0, scale = "4", submitting = false;
  const node = (tag, text, attributes = {}) => {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    for (const [name, value] of Object.entries(attributes)) element.setAttribute(name, value);
    return element;
  };
  const button = (text, action, secondary = false) => {
    const element = node("button", text, {type: "button"});
    if (secondary) element.className = "secondary";
    element.addEventListener("click", action);
    return element;
  };
  function screen(title, kind = "question") {
    main.dataset.screen = kind;
    document.body.dataset.screen = kind;
    main.replaceChildren();
    main.setAttribute("aria-busy", "false");
    const heading = node("h1", title, {id: "screen-title", tabindex: "-1"});
    main.append(heading);
    heading.focus();
    window.scrollTo(0, 0);
    announcements.textContent = title;
    return heading;
  }
  function illustration(name, className) {
    return node("img", undefined, {src: `/static/img/${name}.svg?v=${assetVersion}`, alt: "", "aria-hidden": "true", class: className});
  }
  function support(parent) {
    const titleId = parent === dialog ? "dialog-support-title" : "support-title";
    const section = node("section", undefined, {class: "support", "aria-labelledby": titleId});
    section.append(illustration("support", "support-illustration"), node("h2", config.support_contacts.heading, {id: titleId}));
    section.append(node("p", config.support_contacts.verification_note));
    const list = node("ul");
    for (const item of config.support_contacts.items) {
      const entry = node("li");
      entry.append(node("h3", item.name), node("p", item.note));
      if (item.tel) entry.append(node("a", item.display, {href: `tel:${item.tel}`, class: "phone"}));
      if (item.mailto) entry.append(node("a", item.mailto, {href: `mailto:${item.mailto}`}));
      list.append(entry);
    }
    section.append(list);
    parent.append(section);
  }
  function showAbout() {
    dialog.replaceChildren(node("h2", copy.about.title, {id: "about-title", tabindex: "-1"}));
    for (const part of copy.about.sections) dialog.append(node("h3", part.title), node("p", part.text));
    support(dialog);
    dialog.append(button(copy.controls.close, () => dialog.close()));
    dialog.showModal();
    dialog.querySelector("h2").focus();
  }
  function welcome() {
    screen(copy.welcome.title, "welcome");
    main.prepend(illustration("welcome", "hero-illustration"));
    main.append(node("p", copy.welcome.body), button(copy.welcome.start, () => { step = 0; question(); }), node("p", copy.welcome.small));
  }
  function restart() {
    answers = {};
    scale = "4";
    step = 0;
    welcome();
  }
  function options(question, choices, form, name) {
    const group = node("div", undefined, {role: "radiogroup", "aria-labelledby": "screen-title", "aria-describedby": "helper error"});
    for (const choice of choices) {
      const label = node("label", undefined, {class: "option"});
      const input = node("input", undefined, {type: "radio", name, value: JSON.stringify(choice.value)});
      input.checked = answers[question.key] === choice.value;
      input.addEventListener("change", () => { answers[question.key] = choice.value; clearError(); });
      label.append(input, node("span", "✓", {class: "choice-mark", "aria-hidden": "true"}), node("span", choice.label));
      group.append(label);
    }
    form.append(group);
  }
  function clearError() {
    const error = document.querySelector("#error");
    if (error) error.textContent = "";
    main.querySelectorAll('[aria-invalid="true"]').forEach(control => control.removeAttribute("aria-invalid"));
  }
  function question() {
    const q = copy.questions[step];
    screen(q.prompt);
    const progress = copy.controls.progress.replace("{current}", step + 1).replace("{total}", copy.questions.length);
    const label = node("p", progress, {id: "progress-label"});
    const bar = node("progress", undefined, {value: step + 1, max: copy.questions.length, "aria-labelledby": "progress-label"});
    const progressRegion = node("div", undefined, {class: "question-progress"});
    const segments = node("div", undefined, {class: "progress-path", "aria-hidden": "true"});
    for (let index = 0; index < copy.questions.length; index++) {
      segments.append(node("span", "", {class: index < step ? "complete" : index === step ? "current" : "pending"}));
    }
    bar.className = "sr-only";
    progressRegion.append(label, segments, bar);
    main.prepend(progressRegion);
    main.append(node("p", q.helper || "", {id: "helper"}));
    const form = node("form", undefined, {novalidate: "", autocomplete: "off"});
    if (q.kind === "number") {
      const input = node("input", undefined, {type: "number", min: "16", max: "60", step: "1", inputmode: "numeric", id: "age", "aria-labelledby": "screen-title", "aria-describedby": "helper error"});
      input.value = answers.age ?? "";
      input.addEventListener("input", () => { answers.age = input.value === "" ? null : Number(input.value); clearError(); });
      form.append(input);
    } else if (q.kind === "select") {
      const select = node("select", undefined, {id: "faculty", "aria-labelledby": "screen-title", "aria-describedby": "helper error"});
      select.append(node("option", copy.controls.choose, {value: ""}));
      for (const faculty of config.faculty_groups.groups) select.append(node("option", faculty, {value: faculty}));
      select.value = answers.faculty_group || "";
      select.addEventListener("change", () => { answers.faculty_group = select.value; clearError(); });
      form.append(select);
    } else if (q.kind === "cgpa") {
      const fieldset = node("fieldset", undefined, {class: "scale-toggle"});
      fieldset.append(node("legend", copy.controls.scale));
      for (const value of ["4", "5"]) {
        const label = node("label", undefined, {class: "option"});
        const input = node("input", undefined, {type: "radio", name: "scale", value});
        input.checked = value === scale;
        input.addEventListener("change", () => { scale = value; delete answers.cgpa_band; question(); });
        label.append(input, node("span", value === "4" ? copy.controls.scale4 : copy.controls.scale5));
        fieldset.append(label);
      }
      form.append(fieldset);
      if (scale === "5") form.append(node("p", copy.cgpa.help));
      options(q, copy.cgpa.values.map((value, index) => ({value, label: copy.cgpa[`labels${scale}`][index]})), form, q.key);
    } else options(q, q.options, form, q.key);
    form.append(node("p", "", {id: "error", class: "error", role: "alert"}));
    const actions = node("div", undefined, {class: "actions"});
    if (step > 0) actions.append(button(copy.controls.back, () => { step--; question(); }, true));
    actions.append(node("button", copy.controls.next, {type: "submit"}));
    form.append(actions);
    form.addEventListener("submit", event => {
      event.preventDefault();
      const value = answers[q.key];
      const valid = q.kind === "number" ? Number.isInteger(value) && value >= 16 && value <= 60 : value !== undefined && value !== null && value !== "";
      if (!valid) {
        form.querySelector("#error").textContent = q.error;
        const target = form.querySelector(q.kind === "cgpa" ? `[name="${q.key}"]` : "input, select");
        target.setAttribute("aria-invalid", "true");
        target.focus();
        announcements.textContent = q.error;
      } else if (step < copy.questions.length - 1) { step++; question(); }
      else submit();
    });
    main.append(form);
    announcements.textContent = `${progress}. ${q.prompt}`;
  }
  async function submit() {
    if (submitting) return;
    submitting = true;
    screen(copy.loading, "loading");
    main.prepend(illustration("lower", "loading-illustration"));
    main.setAttribute("aria-busy", "true");
    const minimum = new Promise(resolve => setTimeout(resolve, 400));
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch("/predict", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(answers), cache: "no-store", credentials: "omit", signal: controller.signal});
      if (!response.ok) throw new Error("Request failed");
      const result = await response.json();
      if (!["lower", "higher"].includes(result.category)) throw new Error("Invalid result");
      await minimum;
      // Discard answers on success; retry keeps them only on failure.
      answers = {};
      screen(result.title, "result");
      main.prepend(illustration(result.category, "result-illustration"));
      main.append(node("p", result.label, {class: `result-label ${result.category}`}), node("p", result.message), node("p", result.disclaimer));
      for (const note of result.out_of_range_notes) main.append(node("p", note));
      main.append(node("p", result.model_note));
      support(main);
      main.append(button(copy.controls.restart, restart), node("p", copy.saved));
    } catch {
      await minimum;
      screen(copy.errors.network_title, "network-error");
      main.append(node("p", copy.errors.network));
      const actions = node("div", undefined, {class: "actions"});
      actions.append(button(copy.controls.retry, submit), button(copy.controls.restart, restart, true));
      main.append(actions);
    } finally {
      clearTimeout(timeout);
      submitting = false;
      main.setAttribute("aria-busy", "false");
    }
  }
  document.querySelector("#boot-retry").addEventListener("click", load);
  // Prevent browser back/forward cache from retaining an in-progress check-in.
  window.addEventListener("pagehide", () => { answers = {}; if (copy) restart(); });
  async function load() {
    document.querySelector("#boot-error").hidden = true;
    main.setAttribute("aria-busy", "true");
    try {
      const response = await fetch(`/api/config?v=${assetVersion}`, {credentials: "omit"});
      if (!response.ok) throw new Error("Configuration unavailable");
      config = await response.json();
      copy = config.copy;
      document.title = copy.app_title;
      const footer = document.querySelector("#footer");
      document.querySelector("#brand").replaceChildren(
        node("img", undefined, {src: `/static/img/favicon.svg?v=${assetVersion}`, alt: "", "aria-hidden": "true", width: "28", height: "28"}),
        node("span", copy.app_title));
      footer.replaceChildren(button(copy.footer.about, showAbout, true), node("span", copy.footer.privacy));
      restart();
    } catch {
      main.replaceChildren();
      main.setAttribute("aria-busy", "false");
      document.querySelector("#boot-error").hidden = false;
      document.querySelector("#boot-retry").focus();
    }
  }
  load();
})();
