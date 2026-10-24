(() => {
    if (!('serviceWorker' in navigator) || ['localhost', '127.0.0.1', '[::1]'].includes(location.hostname)) return;
    let applyingUpdate = false;
    let banner;
    let messageKey = 'Pwa.UpdateReady';
    const fallbacks = {
        'Pwa.UpdateReady': '更新があります。変換結果を保存してから更新してください。選択中のファイルは消去されます。',
        'Pwa.CloseTabs': '更新するには、このアプリを開いている他のタブを閉じてください。',
        'Pwa.ApplyUpdate': '更新して再読み込み'
    };
    const label = key => window.localizationStrings?.[key] || fallbacks[key];
    // Strings arrive from Blazor after this script runs, and change with the selected language.
    const renderBanner = () => {
        if (!banner) return;
        banner.querySelector('span').textContent = label(messageKey);
        banner.querySelector('button').textContent = label('Pwa.ApplyUpdate');
    };
    window.addEventListener('localizationchange', renderBanner);
    navigator.serviceWorker.addEventListener('controllerchange', () => {
        if (applyingUpdate) location.reload();
    });
    navigator.serviceWorker.addEventListener('message', event => {
        if (event.data?.type === 'CLOSE_OTHER_TABS') {
            applyingUpdate = false;
            messageKey = 'Pwa.CloseTabs';
            renderBanner();
        }
    });
    const showUpdate = registration => {
        if (!registration.waiting || !navigator.serviceWorker.controller || banner) return;
        banner = document.createElement('div');
        banner.className = 'alert alert-info position-fixed bottom-0 start-0 end-0 m-3';
        banner.style.zIndex = '2000';
        banner.setAttribute('role', 'status');
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'btn btn-primary ms-3';
        button.addEventListener('click', () => {
            if (!registration.waiting) return;
            applyingUpdate = true;
            registration.waiting.postMessage({ type: 'APPLY_UPDATE' });
        });
        banner.append(document.createElement('span'), button);
        renderBanner();
        document.body.append(banner);
    };
    window.addEventListener('load', async () => {
        try {
            const registration = await navigator.serviceWorker.register('sw.js', { updateViaCache: 'none' });
            showUpdate(registration);
            registration.addEventListener('updatefound', () => {
                registration.installing?.addEventListener('statechange', () => showUpdate(registration));
            });
            document.addEventListener('visibilitychange', () => {
                if (!document.hidden) registration.update().catch(console.warn);
            });
            await registration.update();
        } catch (error) {
            console.warn('Service Worker registration/update failed:', error);
        }
    });
})();
