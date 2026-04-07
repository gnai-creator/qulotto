function byId(id) {
  return document.getElementById(id);
}

function setStatus(message, isError = false) {
  const status = byId("status");
  status.textContent = message;
  status.classList.toggle("error", isError);
}

function renderStats(items) {
  const container = byId("stats");
  container.innerHTML = "";
  items.forEach(({ label, value }) => {
    const block = document.createElement("div");
    block.className = "stat";
    block.innerHTML = `<strong>${label}</strong><span>${value}</span>`;
    container.appendChild(block);
  });
}

function renderCheckboxes(containerId, values, selectedValues) {
  const container = byId(containerId);
  container.innerHTML = "";
  values.forEach((value) => {
    const wrapper = document.createElement("label");
    wrapper.className = "option";
    const checked = selectedValues.includes(value) ? "checked" : "";
    wrapper.innerHTML = `<input type="checkbox" value="${value}" ${checked}> <span>${value}</span>`;
    container.appendChild(wrapper);
  });
}

function selectedValues(containerId) {
  return Array.from(byId(containerId).querySelectorAll("input:checked"))
    .map((input) => input.value);
}

function renderArtifacts(data) {
  const list = byId("artifact-list");
  list.innerHTML = "";
  const items = Object.entries(data.artifact_urls || {});
  if (data.tickets_csv_url) {
    items.push(["tickets_csv", data.tickets_csv_url]);
  }

  items.forEach(([name, url]) => {
    const link = document.createElement("a");
    link.href = url;
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = `${name}: ${url}`;
    list.appendChild(link);
  });
}

function renderImages(data) {
  const imageList = byId("image-list");
  imageList.innerHTML = "";
  Object.entries(data.artifact_urls || {})
    .filter(([name]) => name.includes("chart"))
    .forEach(([name, url]) => {
      const block = document.createElement("div");
      block.innerHTML = `<div class="section-title" style="margin-bottom:10px">${name}</div><img src="${url}" alt="${name}">`;
      imageList.appendChild(block);
    });
}

function renderFuturePredictions(markdown) {
  const panel = byId("prediction-panel");
  const content = byId("prediction-content");
  const rows = [];
  let currentExperiment = "";

  markdown.split("\n").forEach((line) => {
    if (line.startsWith("## ")) {
      currentExperiment = line.replace("## ", "").trim();
      return;
    }
    if (!line.startsWith("- Seed ")) {
      return;
    }

    const match = line.match(/- Seed (.+?) \| Ticket (.+?): (.+)/);
    if (!match) {
      return;
    }
    rows.push(
      `<tr><td>${currentExperiment}</td><td>${match[1]}</td><td>${match[2]}</td><td>${match[3]}</td></tr>`
    );
  });

  if (!rows.length) {
    panel.hidden = true;
    content.innerHTML = "";
    return;
  }

  panel.hidden = false;
  content.innerHTML = `
    <table>
      <thead>
        <tr><th>Experimento</th><th>Seed</th><th>Ticket</th><th>Dezenas</th></tr>
      </thead>
      <tbody>${rows.join("")}</tbody>
    </table>
  `;
}

async function loadConfig() {
  const response = await fetch("/api/config");
  const config = await response.json();

  byId("qtd").value = config.defaults.qtd;
  byId("history").value = config.defaults.history;
  byId("inicio").value = config.defaults.inicio;
  byId("fim").value = config.defaults.fim;
  byId("seed").value = config.defaults.seed;
  byId("seed-count").value = config.defaults.seed_count;
  byId("future").checked = config.defaults.future;
  byId("completo").checked = config.defaults.completo;

  const singleBetSize = byId("tamanho-aposta");
  config.bet_sizes.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = `${value} dezenas`;
    singleBetSize.appendChild(option);
  });

  renderCheckboxes("bet-sizes", config.bet_sizes, config.default_bet_sizes.map(String));
  renderCheckboxes("presets", config.presets, config.default_presets);
  renderStats([
    { label: "Runs padrão", value: config.preview.total_runs },
    { label: "Concursos", value: config.preview.target_draw_count },
    { label: "Tickets estimados", value: config.preview.estimated_tickets },
    { label: "Custo estimado", value: `R$ ${config.preview.estimated_total_cost.toFixed(2)}` },
  ]);
  setStatus("Configuração carregada. Ajuste os argumentos e execute.");
}

function buildPayload() {
  return {
    future: byId("future").checked,
    completo: byId("completo").checked,
    qtd: Number(byId("qtd").value),
    history: byId("history").value ? Number(byId("history").value) : null,
    inicio: byId("inicio").value ? Number(byId("inicio").value) : null,
    fim: byId("fim").value ? Number(byId("fim").value) : null,
    seed: Number(byId("seed").value),
    seed_count: Number(byId("seed-count").value),
    tamanho_aposta: byId("tamanho-aposta").value ? Number(byId("tamanho-aposta").value) : null,
    tamanhos_aposta: selectedValues("bet-sizes").map(Number),
    presets: selectedValues("presets"),
  };
}

async function runWorkflow(event) {
  event.preventDefault();
  const submitBtn = byId("submit-btn");
  submitBtn.disabled = true;
  setStatus("Executando. Isso pode levar algum tempo, dependendo da bateria escolhida.");

  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(buildPayload()),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Falha ao executar o workflow.");
    }

    renderArtifacts(data);
    renderImages(data);
    renderFuturePredictions(data.markdown || "");
    byId("report-output").textContent = data.markdown || "Sem markdown disponível.";

    if (data.mode === "future") {
      renderStats([
        { label: "Concurso futuro", value: data.summary.future_contest },
        { label: "Base histórica", value: data.summary.based_on_latest_contest },
        { label: "Seeds", value: data.summary.seeds.join(", ") },
        { label: "Tickets por experimento", value: data.summary.qtd_por_experimento },
      ]);
      setStatus(`Palpites gerados para o concurso ${data.summary.future_contest}.`);
      return;
    }

    renderStats([
      { label: "Runs", value: data.summary.total_runs },
      { label: "Concursos", value: data.summary.target_draw_count },
      { label: "Tickets estimados", value: data.summary.estimated_tickets },
      { label: "Custo da bateria", value: `R$ ${data.summary.estimated_total_cost.toFixed(2)}` },
    ]);
    setStatus(`Backtest concluído. Relatório salvo em ${data.report_dir}.`);
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    submitBtn.disabled = false;
  }
}

byId("run-form").addEventListener("submit", runWorkflow);
loadConfig().catch((error) => setStatus(error.message, true));
