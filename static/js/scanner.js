// Employee check-in: camera QR scan (html5-qrcode) + GPS capture + submit to /checkin
let coords = null;
let hasSubmitted = false; // prevent double-submits from repeated QR frames

const locStatusEl = document.getElementById("locStatus");
const resultBoxEl = document.getElementById("resultBox");

function requestLocation() {
  if (!navigator.geolocation) {
    locStatusEl.textContent = "Geolocation not supported on this device.";
    return;
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      coords = { lat: pos.coords.latitude, lon: pos.coords.longitude };
      locStatusEl.textContent = `Location captured (±${Math.round(pos.coords.accuracy)}m)`;
    },
    () => {
      locStatusEl.textContent = "Location permission denied — check-in requires location access.";
    },
    { enableHighAccuracy: true, timeout: 10000 }
  );
}
requestLocation();

async function submitCheckin(token) {
  if (hasSubmitted) return;
  if (!coords) {
    resultBoxEl.innerHTML = `<div class="alert alert-warning">Waiting for location permission — please allow location access and scan again.</div>`;
    return;
  }
  hasSubmitted = true;

  try {
    const res = await fetch("/checkin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token, latitude: coords.lat, longitude: coords.lon }),
    });
    const data = await res.json();

    const okStatuses = ["PRESENT", "LATE"];
    const cls = okStatuses.includes(data.status) ? "alert-success" : "alert-danger";
    resultBoxEl.innerHTML = `<div class="alert ${cls}"><strong>${data.status}</strong><br>${data.message}</div>`;
  } catch (e) {
    resultBoxEl.innerHTML = `<div class="alert alert-danger">Error contacting server: ${e.message}</div>`;
  } finally {
    // allow another attempt after a few seconds (e.g. different employee's turn)
    setTimeout(() => { hasSubmitted = false; }, 4000);
  }
}

const html5QrCode = new Html5Qrcode("reader");
const qrConfig = { fps: 10, qrbox: { width: 250, height: 250 } };

Html5Qrcode.getCameras().then((cameras) => {
  if (cameras && cameras.length) {
    html5QrCode.start(
      { facingMode: "environment" },
      qrConfig,
      (decodedText) => submitCheckin(decodedText),
      () => { /* per-frame scan failures are normal, ignore */ }
    );
  } else {
    resultBoxEl.innerHTML = `<div class="alert alert-warning">No camera found on this device.</div>`;
  }
}).catch(() => {
  resultBoxEl.innerHTML = `<div class="alert alert-warning">Camera permission denied or unavailable.</div>`;
});
