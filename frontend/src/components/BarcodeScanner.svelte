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
        cameraId = cameras[cameras.length - 1].id; // Use back camera
        scanner = new Html5Qrcode('barcode-reader');

        await scanner.start(
          cameraId,
          {
            fps: 10,
            qrbox: { width: 250, height: 250 }
          },
          onScanSuccess,
          onScanError
        );

        scanning = true;
      } else {
        error = 'No cameras found';
      }
    } catch (err) {
      error = `Error starting scanner: ${err.message}`;
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

  #barcode-reader {
    margin: 1rem 0;
    max-width: 100%;
  }

  .scanner-controls {
    display: flex;
    justify-content: center;
    gap: 1rem;
  }
</style>
