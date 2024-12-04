// marked-wrapper.js
export const markedPromise = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/marked@4.3.0/marked.min.js';
    script.onload = () => {
        console.log('Marked loaded:', window.marked); // 调试信息
        if (window.marked && typeof window.marked.parse === 'function') {
            resolve(window.marked);
        } else {
            reject(new Error('Marked.parse is not available as a function'));
        }
    };
    script.onerror = () => reject(new Error('Failed to load marked'));
    document.head.appendChild(script);
});