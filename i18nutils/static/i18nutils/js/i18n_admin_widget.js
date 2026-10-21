(function() {
    'use strict';

    function initI18nAdminWidgets() {
        var selectors = document.querySelectorAll('.i18n-lang-selector:not(.initialized)');
        
        for (var i = 0; i < selectors.length; i++) {
            var selector = selectors[i];
            selector.classList.add('initialized');
            
            // Using an IIFE to capture the correct container for each selector
            (function(sel) {
                var container = sel.closest('.i18n-form-group');
                if (!container) return;
                
                var items = container.querySelectorAll('.i18n-lang-container');
                
                sel.addEventListener('change', function(e) {
                    var selectedLang = e.target.value;
                    for (var j = 0; j < items.length; j++) {
                        var item = items[j];
                        if (item.getAttribute('data-i18n-lang') === selectedLang) {
                            item.style.display = 'block';
                        } else {
                            item.style.display = 'none';
                        }
                    }
                });
                
                // Trigger initial setup without dispatching event to avoid loops
                var initialLang = sel.value;
                for (var j = 0; j < items.length; j++) {
                    var item = items[j];
                    if (item.getAttribute('data-i18n-lang') === initialLang) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                }
            })(selector);
        }
    }

    // Standard init
    document.addEventListener('DOMContentLoaded', initI18nAdminWidgets);
    
    // Support for Django admin dynamically added inlines using MutationObserver (vanilla JS)
    // No jQuery required!
    var observer = new MutationObserver(function(mutations) {
        var shouldInit = false;
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                shouldInit = true;
            }
        });
        if (shouldInit) {
            initI18nAdminWidgets();
        }
    });

    // Start observing after DOM load
    document.addEventListener('DOMContentLoaded', function() {
        var target = document.querySelector('body');
        if (target) {
            observer.observe(target, { childList: true, subtree: true });
        }
    });

})();
