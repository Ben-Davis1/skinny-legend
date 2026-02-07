<script>
  import { onMount, onDestroy, createEventDispatcher } from 'svelte';
  import { Html5Qrcode } from 'html5-qrcode';

  const dispatch = createEventDispatcher();

  let scanner = null;
  let scanning = false;
  let error = '';
  let cameraId = null;

  async function startScanner() {
    try {
      error = '';
      const cameras = await Html5Qrcode.getCameras();

      if (cameras && cameras.length) {
        // Use back camera (last in array) or first available
        cameraId = cameras[cameras.length - 1].id;
        scanner = new Html5Qrcode('barcode-reader');

        // Enhanced config for iPhone with autofocus
        const config = {
          fps: 10,
          qrbox: { width: 250, height: 250 },
          aspectRatio: 1.0,
          // Add constraints for better iPhone support
          videoConstraints: {
            facingMode: { ideal: "environment" },
            focusMode: { ideal: "continuous" },
            advanced: [{ focusMode: "continuous" }]
          }
        };

        await scanner.start(
          cameraId,
          config,
          onScanSuccess,
          onScanError
        );

        scanning = true;
      } else {
        error = 'No cameras found. Please allow camera access.';
      }
    } catch (err) {
      error = `Error starting scanner: ${err.message}`;
      console.error('Scanner error:', err);
    }
  }

  async function stopScanner() {
    if (scanner && scanning) {
      try {
        await scanner.stop();
        scanner.clear();
        scanning = false;
      } catch (err) {
        console.error('Error stopping scanner:', err);
      }
    }
  }

  function onScanSuccess(decodedText, decodedResult) {
    dispatch('scan', decodedText);
    stopScanner();
  }

  function onScanError(errorMessage) {
    // Ignore scan errors (they happen frequently during scanning)
  }

  onDestroy(() => {
    stopScanner();
  });
</script>

<div class="barcode-scanner card">
  <h3>Barcode Scanner</h3>
  <p class="scanner-info">Scan product barcodes to automatically lookup nutrition data from OpenFoodFacts database</p>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  <div id="barcode-reader"></div>

  <div class="scanner-controls">
    {#if !scanning}
      <button class="primary" on:click={startScanner}>Start Scanner</button>
    {:else}
      <button class="danger" on:click={stopScanner}>Stop Scanner</button>
    {/if}
  </div>
</div>

<style>
  .barcode-scanner {
    margin-bottom: 2rem;
  }

  .scanner-info {
    color: var(--text-light);
    font-size: 0.9rem;
    margin-bottom: 1rem;
  }

  #barcode-reader {
    margin: 1rem 0;
    max-width: 100%;
  }

  .scanner-controls {
    display: flex;
    justify-content: center;
    gap: 1rem;
  }

  .error {
    background: var(--danger);
    color: white;
    padding: 0.75rem;
    border-radius: 4px;
    margin-bottom: 1rem;
  }
</style>
