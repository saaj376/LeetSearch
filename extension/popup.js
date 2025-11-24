const DEFAULT_API_BASE = "http://localhost:8000";
const STORAGE_KEY = "http://localhost:8000";

const collegeInput = document.getElementById("collegeInput");
const searchBtn = document.getElementById("searchBtn");
const filterInput = document.getElementById("filterInput");
const resultsContainer = document.getElementById("results");
const statsCard = document.getElementById("stats");
const totalUsersEl = document.getElementById("totalUsers");
const activeUsersEl = document.getElementById("activeUsers");
const variationsEl = document.getElementById("variations");

let currentResults = [];

async function getApiBase() {
  return new Promise((resolve) => {
    chrome.storage.sync.get([STORAGE_KEY], (data) => {
      resolve(data[STORAGE_KEY] || DEFAULT_API_BASE);
    });
  });
}

function saveApiBase(url) {
  chrome.storage.sync.set({ [STORAGE_KEY]: url });
}

function formatRanking(ranking) {
  if (!ranking && ranking !== 0) {
    return "N/A";
  }
  return ranking.toLocaleString();
}

function renderResults(list) {
  if (!list.length) {
    resultsContainer.innerHTML = `<p class="empty">No users found.</p>`;
    return;
  }

  resultsContainer.innerHTML = list
    .map(
      (user) => `
      <div class="userBox">
        <div class="userHeader">
          <a href="https://leetcode.com/${user.username}/" target="_blank" rel="noreferrer">
            ${user.username}
          </a>
          <span class="rank">Rank: ${formatRanking(user.ranking)}</span>
        </div>
        <div class="userMeta">
          <span>${user.realName || "Anonymous"}</span>
          <span>${user.country || "Unknown country"}</span>
        </div>
        <div class="userSchool">${user.school}</div>
      </div>`
    )
    .join("");
}

function updateStats(total) {
  statsCard.style.display = "block";
  totalUsersEl.textContent = `Profiles matched: ${total}`;
  activeUsersEl.textContent = `Filtered view: ${currentResults.length}`;
  variationsEl.textContent = `Last refreshed: ${new Date().toLocaleTimeString()}`;
}

function applyFilter() {
  const needle = filterInput.value.trim().toLowerCase();
  if (!needle) {
    renderResults(currentResults);
    updateStats(currentResults.length);
    return;
  }

  const filtered = currentResults.filter((user) => {
    const blob = `${user.username} ${user.realName || ""} ${user.country || ""}`.toLowerCase();
    return blob.includes(needle);
  });

  renderResults(filtered);
  totalUsersEl.textContent = `Profiles matched: ${currentResults.length}`;
  activeUsersEl.textContent = `Filtered view: ${filtered.length}`;
}

async function searchCollege() {
  const query = collegeInput.value.trim();
  if (!query) {
    resultsContainer.innerHTML = `<p class="empty">Please enter a college name.</p>`;
    return;
  }

  searchBtn.disabled = true;
  searchBtn.textContent = "Searching...";
  resultsContainer.innerHTML = "";

  try {
    const base = await getApiBase();
    const resp = await fetch(`${base}/search/college?query=${encodeURIComponent(query)}`);

    if (!resp.ok) {
      throw new Error(`Server error ${resp.status}`);
    }

    const data = await resp.json();
    currentResults = data.results || [];

    if (data.backendUrl && data.backendUrl !== base) {
      saveApiBase(data.backendUrl);
    }

    filterInput.style.display = currentResults.length ? "block" : "none";
    renderResults(currentResults);
    updateStats(data.total || 0);
  } catch (err) {
    console.error(err);
    resultsContainer.innerHTML = `<p class="error">Failed to fetch results. Check backend URL.</p>`;
  } finally {
    searchBtn.disabled = false;
    searchBtn.textContent = "Search";
  }
}

searchBtn.addEventListener("click", searchCollege);
collegeInput.addEventListener("keydown", (evt) => {
  if (evt.key === "Enter") {
    searchCollege();
  }
});
filterInput.addEventListener("input", applyFilter);

