// 墨境BLOG通用JavaScript功能

// 阻止Vite开发模式请求 - 更全面的阻止
(function() {
    // 拦截XMLHttpRequest
    if (typeof window.XMLHttpRequest !== 'undefined') {
        const originalXHR = window.XMLHttpRequest;
        window.XMLHttpRequest = function() {
            const xhr = new originalXHR();
            const originalOpen = xhr.open;
            xhr.open = function(method, url, ...args) {
                if (typeof url === 'string' && url.includes('@vite/client')) {
                    console.log('阻止Vite客户端请求(XHR):', url);
                    // 返回一个模拟的成功响应
                    setTimeout(() => {
                        Object.defineProperty(xhr, 'status', { value: 200 });
                        Object.defineProperty(xhr, 'readyState', { value: 4 });
                        Object.defineProperty(xhr, 'responseText', { value: '' });
                        if (xhr.onreadystatechange) xhr.onreadystatechange();
                        if (xhr.onload) xhr.onload();
                    }, 0);
                    return;
                }
                return originalOpen.apply(this, [method, url, ...args]);
            };
            return xhr;
        };
    }

    // 拦截fetch
    if (typeof window.fetch !== 'undefined') {
        const originalFetch = window.fetch;
        window.fetch = function(url, options) {
            if (typeof url === 'string' && url.includes('@vite/client')) {
                console.log('阻止Vite客户端请求(fetch):', url);
                return Promise.resolve(new Response('', { 
                    status: 200, 
                    statusText: 'OK',
                    headers: new Headers({
                        'Content-Type': 'application/javascript',
                        'Cache-Control': 'no-cache'
                    })
                }));
            }
            return originalFetch.apply(this, arguments);
        };
    }

    // 阻止Vite相关WebSocket连接
    if (typeof window.WebSocket !== 'undefined') {
        const originalWebSocket = window.WebSocket;
        window.WebSocket = function(url, protocols) {
            if (typeof url === 'string' && (url.includes('vite') || url.includes('hmr'))) {
                console.log('阻止Vite WebSocket连接:', url);
                // 返回一个模拟的WebSocket对象
                const fakeWS = {
                    url: url,
                    readyState: 3, // CLOSED
                    CONNECTING: 0,
                    OPEN: 1,
                    CLOSING: 2,
                    CLOSED: 3,
                    send: function() {},
                    close: function() {},
                    addEventListener: function() {},
                    removeEventListener: function() {},
                    dispatchEvent: function() { return true; }
                };
                setTimeout(() => {
                    if (fakeWS.onopen) fakeWS.onopen();
                    setTimeout(() => {
                        if (fakeWS.onclose) fakeWS.onclose();
                    }, 100);
                }, 0);
                return fakeWS;
            }
            return new originalWebSocket(url, protocols);
        };
    }

    // 阻止Vite相关的script标签创建
    if (typeof document !== 'undefined' && document.createElement) {
        const originalCreateElement = document.createElement;
        document.createElement = function(tagName) {
            const element = originalCreateElement.call(this, tagName);
            if (tagName.toLowerCase() === 'script' && element.src) {
                const originalSrc = Object.getOwnPropertyDescriptor(HTMLScriptElement.prototype, 'src');
                Object.defineProperty(element, 'src', {
                    set: function(value) {
                        if (value && value.includes('@vite/client')) {
                            console.log('阻止Vite script标签创建:', value);
                            return;
                        }
                        originalSrc.set.call(this, value);
                    },
                    get: function() {
                        return originalSrc.get.call(this);
                    }
                });
            }
            return element;
        };
    }
})();

document.addEventListener('DOMContentLoaded', function() {

    // 页面加载动画处理
    const pageLoader = document.getElementById('page-loader');
    const mainContent = document.querySelector('.main-content');
    
    // 显示页面内容并隐藏加载动画
    function hideLoader() {
        if (pageLoader && mainContent) {
            setTimeout(() => {
                pageLoader.classList.add('fade-out');
                mainContent.classList.add('loaded');
                
                // 完全隐藏加载器
                setTimeout(() => {
                    if (pageLoader) {
                        pageLoader.style.display = 'none';
                    }
                }, 500);
            }, 300); // 延迟300ms显示，让页面有足够时间加载
        }
    }
    
    // 页面加载完成后隐藏加载动画
    hideLoader();

    // 确认删除对话框
    const deleteButtons = document.querySelectorAll('.btn-delete-confirm');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const deleteUrl = this.getAttribute('href');
            const itemType = this.getAttribute('data-type') || '此项目';
            
            if (confirm(`确定要删除${itemType}吗？此操作无法撤销。`)) {
                window.location.href = deleteUrl;
            }
        });
    });

    // 表单提交防抖
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 处理中...';
            }
        });
    });

    // 代码高亮（如果页面中有code标签）
    const codeBlocks = document.querySelectorAll('pre code');
    if (codeBlocks.length > 0) {
        // 添加复制按钮
        codeBlocks.forEach(function(codeBlock) {
            const pre = codeBlock.parentElement;
            const copyButton = document.createElement('button');
            copyButton.className = 'btn btn-sm btn-outline-secondary copy-btn';
            copyButton.innerHTML = '<i class="fas fa-copy"></i>';
            copyButton.style.position = 'absolute';
            copyButton.style.top = '5px';
            copyButton.style.right = '5px';
            
            pre.style.position = 'relative';
            pre.appendChild(copyButton);
            
            copyButton.addEventListener('click', function() {
                const text = codeBlock.textContent;
                navigator.clipboard.writeText(text).then(function() {
                    copyButton.innerHTML = '<i class="fas fa-check"></i>';
                    copyButton.classList.remove('btn-outline-secondary');
                    copyButton.classList.add('btn-success');
                    
                    setTimeout(function() {
                        copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                        copyButton.classList.remove('btn-success');
                        copyButton.classList.add('btn-outline-secondary');
                    }, 2000);
                });
            });
        });
    }

    // 返回顶部按钮
    const backToTopButton = document.createElement('button');
    backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopButton.className = 'btn btn-primary btn-back-to-top';
    backToTopButton.style.position = 'fixed';
    backToTopButton.style.bottom = '20px';
    backToTopButton.style.right = '20px';
    backToTopButton.style.display = 'none';
    backToTopButton.style.zIndex = '9999';
    backToTopButton.style.borderRadius = '50%';
    backToTopButton.style.width = '50px';
    backToTopButton.style.height = '50px';
    
    document.body.appendChild(backToTopButton);
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    });
    
    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    console.log('墨境BLOGJavaScript功能已加载');

    // 全局错误处理
    window.addEventListener('error', function(e) {
        console.error('页面错误:', e.error);
        // 可以在这里添加错误上报功能
    });

    // 未处理的Promise拒绝
    window.addEventListener('unhandledrejection', function(e) {
        console.error('未处理的Promise拒绝:', e.reason);
        // 可以在这里添加错误上报功能
    });
});