(function() {
    // Loading state in forms
    var $forms = document.querySelectorAll('form');
    for (var i=0; i<$forms.length; i++) {
        var $form = $forms[i];
        $form.addEventListener('submit', function() {
            const $formBtn = this.querySelector('button[type="submit"]');
            $formBtn.disabled = true;
            $formBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
        });
    }
})();
