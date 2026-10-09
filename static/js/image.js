
    const localHosts = ['localhost', '127.0.0.1'];
    const API_URL = localHosts.includes(window.location.hostname) ? '' : 'https://allverter-api-j6lv.onrender.com';
    const input = document.querySelector('#file-input');
    const dropzone = document.querySelector('#dropzone');
    const options = document.querySelector('#options');
    const formatOptions = document.querySelector('#format-options');
    const status = document.querySelector('#status');
    const fileSummary = document.querySelector('#file-summary');
    const fileName = document.querySelector('#file-name');
    const fileSize = document.querySelector('#file-size');
    const previewImage = document.querySelector('#preview-image');
    const convertButton = document.querySelector('#convert-button');
    const themeToggle = document.querySelector('#theme-toggle');
    const languageToggle = document.querySelector('#language-toggle');
    const MAX_FILE_SIZE = 100 * 1024 * 1024;
    let selectedFiles = [];
    let selectedTarget = '';
    const translations = { en: { mediaLink: 'Audio / video', convert: 'Convert', images: 'images.', imageIntro: 'Choose a file, pick a format, and download the result.', bringImage: 'Bring something in.', dropImages: 'Drop images here or', browse: 'browse your device', imageFormats: 'PNG, JPG, WEBP, TIFF, and more', outputFormat: 'Output format', convertFiles: 'Convert files', chooseFile: 'Choose a file to begin.', checking: 'Checking compatible formats...', ready: 'file(s) ready.', unsupported: 'No shared output format is available for these files.', converting: 'Converting', done: 'Done. Your download should start automatically.' }, es: { mediaLink: 'Audio / video', convert: 'Convierte', images: 'imÃ¡genes.', imageIntro: 'Elige un archivo, selecciona un formato y descarga el resultado.', bringImage: 'AÃ±ade un archivo.', dropImages: 'Arrastra imÃ¡genes aquÃ­ o', browse: 'explora tu dispositivo', imageFormats: 'PNG, JPG, WEBP, TIFF y mÃ¡s', outputFormat: 'Formato de salida', convertFiles: 'Convertir archivos', chooseFile: 'Elige un archivo para comenzar.', checking: 'Comprobando formatos compatibles...', ready: 'archivo(s) listos.', unsupported: 'No hay un formato de salida comÃºn para estos archivos.', converting: 'Convirtiendo', done: 'Listo. La descarga comenzarÃ¡ automÃ¡ticamente.' } };
    let language = localStorage.getItem('allverter-language') || 'en';

    function applyLanguage() {
      document.querySelectorAll('[data-i18n]').forEach(element => { element.textContent = translations[language][element.dataset.i18n]; });
      languageToggle.innerHTML = `<span aria-hidden="true">${language === 'en' ? '🇪🇸' : '🇺🇸'}</span>`;
      languageToggle.title = language === 'en' ? 'Cambiar a español' : 'Switch to English';
      document.documentElement.lang = language;
    }
    languageToggle.addEventListener('click', () => { language = language === 'en' ? 'es' : 'en'; localStorage.setItem('allverter-language', language); applyLanguage(); });
    applyLanguage();

    document.querySelector('#browse-button').addEventListener('click', () => input.click());
    dropzone.addEventListener('keydown', event => {
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); input.click(); }
    });
    input.addEventListener('change', () => input.files.length && selectFiles([...input.files]));
    ['dragenter', 'dragover'].forEach(event => dropzone.addEventListener(event, event => { event.preventDefault(); dropzone.classList.add('dragging'); }));
    ['dragleave', 'drop'].forEach(event => dropzone.addEventListener(event, event => { event.preventDefault(); dropzone.classList.remove('dragging'); }));
    dropzone.addEventListener('drop', event => event.dataTransfer.files.length && selectFiles([...event.dataTransfer.files]));
    document.querySelector('#clear-button').addEventListener('click', resetForm);
    themeToggle.addEventListener('click', () => {
      document.body.classList.toggle('light-mode');
      const light = document.body.classList.contains('light-mode');
      localStorage.setItem('allverter-theme', light ? 'light' : 'dark');
      themeToggle.textContent = light ? 'Dark mode' : 'Light mode';
    });
    if (localStorage.getItem('allverter-theme') === 'light') themeToggle.click();

    async function selectFiles(files) {
      selectedFiles = files;
      const totalSize = files.reduce((total, file) => total + file.size, 0);
      fileName.textContent = files.length === 1 ? files[0].name : `${files.length} files selected`;
      fileSize.textContent = `${(totalSize / 1024 / 1024).toFixed(2)} MB total`;
      fileSummary.classList.remove('hidden'); fileSummary.classList.add('flex');
      if (files.length === 1 && files[0].type.startsWith('image/')) {
        previewImage.src = URL.createObjectURL(files[0]);
        previewImage.classList.remove('hidden');
      } else {
        previewImage.removeAttribute('src'); previewImage.classList.add('hidden');
      }
      options.classList.add('hidden'); options.classList.remove('flex');
      if (files.some(file => file.size > MAX_FILE_SIZE)) {
        status.textContent = 'Each file must be smaller than 100 MB.';
        selectedFiles = [];
        return;
      }
      status.textContent = translations[language].checking;
      try {
        const formatResponses = await Promise.all(files.map(file => fetch(`${API_URL}/api/formats?filename=${encodeURIComponent(file.name)}`).then(response => response.json())));
        const targets = formatResponses.slice(1).reduce((common, data) => common.filter(target => data.targets.includes(target)), formatResponses[0]?.targets || []);
        selectedTarget = targets[0] || '';
        formatOptions.innerHTML = targets.map((target, index) => `<button type="button" class="format-button rounded-lg border border-[#b9cbb7] bg-white px-3 py-2 text-sm font-bold text-[#526b5c] transition hover:border-[#e75c35] hover:text-[#c94824] ${index === 0 ? 'selected' : ''}" data-format="${target}" role="radio" aria-checked="${index === 0}"><span class="format-icon" aria-hidden="true">${target.toUpperCase()}</span><span>.${target.toUpperCase()}</span></button>`).join('');
        options.classList.toggle('hidden', !targets.length);
        options.classList.toggle('flex', Boolean(targets.length));
        status.textContent = targets.length ? `${files.length} ${translations[language].ready}` : translations[language].unsupported;
      } catch (error) {
        status.textContent = 'Could not check this file. Is the server still running?';
      }
    }

    formatOptions.addEventListener('click', event => {
      const button = event.target.closest('[data-format]');
      if (!button) return;
      selectedTarget = button.dataset.format;
      formatOptions.querySelectorAll('[data-format]').forEach(option => {
        const isSelected = option === button;
        option.classList.toggle('selected', isSelected);
        option.classList.toggle('border-[#e75c35]', isSelected);
        option.classList.toggle('bg-[#fff2ed]', isSelected);
        option.classList.toggle('text-[#c94824]', isSelected);
        option.setAttribute('aria-checked', isSelected);
      });
    });

    document.querySelector('#converter-form').addEventListener('submit', async event => {
      event.preventDefault();
      if (!selectedFiles.length || !selectedTarget) return;
      convertButton.disabled = true; convertButton.textContent = `${translations[language].converting}...`; status.textContent = `${translations[language].converting}...`;
      try {
        const body = new FormData();
        const endpoint = selectedFiles.length === 1 ? '/api/convert' : '/api/batch-convert';
        const fieldName = selectedFiles.length === 1 ? 'upload' : 'uploads';
        selectedFiles.forEach(file => body.append(fieldName, file));
        body.append('target_format', selectedTarget);
        status.textContent = selectedFiles.length === 1 ? 'Converting your file...' : `Converting ${selectedFiles.length} files into a ZIP...`;
        const response = await fetch(`${API_URL}${endpoint}`, { method: 'POST', body });
        if (!response.ok) {
          const error = await response.json().catch(() => ({}));
          throw new Error(error.detail || 'Conversion failed.');
        }
        const blob = await response.blob(); const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = response.headers.get('content-disposition')?.split('filename=')[1]?.replaceAll('"', '') || (selectedFiles.length === 1 ? `converted.${selectedTarget}` : 'allverter-results.zip'); link.click(); URL.revokeObjectURL(link.href);
        status.textContent = selectedFiles.length === 1 ? translations[language].done : `${translations[language].done} (${selectedFiles.length})`;
      } catch (error) {
        status.textContent = error.message || 'Could not connect to the converter.';
      } finally {
        convertButton.disabled = false; convertButton.textContent = translations[language].convertFiles;
      }
    });

    function resetForm() {
      selectedFiles = []; selectedTarget = ''; input.value = ''; formatOptions.innerHTML = '';
      previewImage.removeAttribute('src'); previewImage.classList.add('hidden');
      fileName.textContent = ''; fileSize.textContent = ''; fileSummary.classList.add('hidden'); fileSummary.classList.remove('flex');
      options.classList.add('hidden'); options.classList.remove('flex'); status.textContent = translations[language].chooseFile;
    }
  
