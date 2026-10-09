
    const localHosts = ['localhost', '127.0.0.1'];
    const API_URL = localHosts.includes(window.location.hostname) ? '' : 'https://allverter-api-j6lv.onrender.com';
    const input = document.querySelector('#file-input');
    const dropzone = document.querySelector('#dropzone');
    const target = document.querySelector('#target');
    const options = document.querySelector('#options');
    const status = document.querySelector('#status');
    let selectedFile;
    const languageToggle = document.querySelector('#language-toggle');
    const themeToggle = document.querySelector('#theme-toggle');
    const languageFlag = document.querySelector('#language-flag');
    const translations = { en: { imageLink: 'Image studio', convert: 'Convert', media: 'media.', mediaIntro: 'Choose an audio or video file, pick a format, and download the result.', bringMedia: 'Bring a file in.', dropMedia: 'Drop audio or video here, or', browse: 'browse your device', mediaFormats: 'MP3, WAV, MP4, WEBM, MOV, and more', outputFormat: 'Output format', choose: 'Choose a media file to begin.', checking: 'Checking compatible formats...', ready: 'Ready to convert.', unsupported: 'Unsupported media format.', ffmpeg: 'FFmpeg is not installed. Install it and add it to PATH to enable media conversion.', lightMode: 'Light mode', darkMode: 'Dark mode' }, es: { imageLink: 'Estudio de imágenes', convert: 'Convertir', media: 'medios.', mediaIntro: 'Elige un archivo de audio o video, selecciona un formato y descarga el resultado.', bringMedia: 'Añade un archivo.', dropMedia: 'Arrastra audio o video aquí, o', browse: 'explora tu dispositivo', mediaFormats: 'MP3, WAV, MP4, WEBM, MOV y más', outputFormat: 'Formato de salida', choose: 'Elige un archivo multimedia para comenzar.', checking: 'Comprobando formatos compatibles...', ready: 'Listo para convertir.', unsupported: 'Formato multimedia no compatible.', ffmpeg: 'FFmpeg no está instalado. Instálalo y añádelo al PATH para activar la conversión multimedia.', lightMode: 'Modo claro', darkMode: 'Modo oscuro' } };
    let language = localStorage.getItem('allverter-language') || 'en';
    function applyLanguage() { document.querySelectorAll('[data-i18n]').forEach(element => { element.textContent = translations[language][element.dataset.i18n]; }); languageFlag.className = `flag ${language === 'en' ? 'flag-es' : 'flag-us'}`; languageToggle.title = language === 'en' ? 'Cambiar a español' : 'Switch to English'; document.querySelector('#theme-label').textContent = document.body.classList.contains('light-mode') ? translations[language].darkMode : translations[language].lightMode; document.documentElement.lang = language; }
    languageToggle.addEventListener('click', () => { language = language === 'en' ? 'es' : 'en'; localStorage.setItem('allverter-language', language); applyLanguage(); });
    themeToggle.addEventListener('click', () => { document.body.classList.toggle('light-mode'); localStorage.setItem('allverter-theme', document.body.classList.contains('light-mode') ? 'light' : 'dark'); applyLanguage(); });
    applyLanguage();
    if (localStorage.getItem('allverter-theme') === 'light') themeToggle.click();
    document.querySelector('#browse').addEventListener('click', () => input.click());
    dropzone.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); input.click(); } });
    input.addEventListener('change', () => input.files[0] && selectFile(input.files[0]));
    ['dragenter', 'dragover'].forEach(name => dropzone.addEventListener(name, event => { event.preventDefault(); dropzone.classList.add('dragging'); }));
    ['dragleave', 'drop'].forEach(name => dropzone.addEventListener(name, event => { event.preventDefault(); dropzone.classList.remove('dragging'); }));
    dropzone.addEventListener('drop', event => event.dataTransfer.files[0] && selectFile(event.dataTransfer.files[0]));
    async function selectFile(file) {
      selectedFile = file; document.querySelector('#filename').textContent = file.name; document.querySelector('#filename').classList.remove('hidden'); status.textContent = translations[language].checking;
      const response = await fetch(`${API_URL}/api/media/formats?filename=${encodeURIComponent(file.name)}`); const data = await response.json();
      target.innerHTML = data.targets.map(format => `<option value="${format}">.${format.toUpperCase()}</option>`).join('');
      const ready = data.available && data.targets.length;
      options.classList.toggle('hidden', !ready);
      options.classList.toggle('flex', Boolean(ready));
      status.textContent = !data.available ? translations[language].ffmpeg : data.targets.length ? translations[language].ready : translations[language].unsupported;
    }
    document.querySelector('#media-form').addEventListener('submit', async event => {
      event.preventDefault(); if (!selectedFile || !target.value) return; status.textContent = 'Converting...';
      const body = new FormData(); body.append('upload', selectedFile); body.append('target_format', target.value);
      try { const response = await fetch(`${API_URL}/api/media/convert`, { method: 'POST', body }); if (!response.ok) { const error = await response.json(); throw new Error(error.detail); } const blob = await response.blob(); const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = response.headers.get('content-disposition')?.split('filename=')[1]?.replaceAll('"', '') || `converted.${target.value}`; link.click(); URL.revokeObjectURL(link.href); status.textContent = 'Done. Your download should start automatically.'; } catch (error) { status.textContent = error.message || 'Conversion failed.'; }
    });
  
